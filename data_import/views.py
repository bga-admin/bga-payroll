import datetime
import json

from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import FormView

from data_import.forms import UploadForm
from data_import.models import SourceFile, StandardizedFile, RespondingAgency, \
    Upload
from data_import.tasks import copy_to_database
from data_import.utils import RespondingAgencyQueue


class SourceFileHook(View):
    def post(self, request):
        '''
        Accept post containing file metadata & ID in Google Drive
        '''
        upload = Upload.objects.create()
        source_files = json.loads(request.POST['source_files'])

        for file_metadata in source_files:
            agency = file_metadata.pop('responding_agency')
            responding_agency, _ = RespondingAgency.objects.get_or_create(name=agency)

            file_metadata['upload'] = upload
            file_metadata['responding_agency'] = responding_agency

            file_metadata = self._hydrate_date_objects(file_metadata)

            SourceFile.objects.create(**file_metadata)

        # TO-DO: Kick off delayed task, which iterates over all source files
        # without an attached file and calls SourceFile.download_from_drive

        return HttpResponse('Caught!')

    def _hydrate_date_objects(self, file_metadata):
        '''
        Convert date strings to Python date objects.
        '''
        date_fields = [k for k in file_metadata.keys() if k.endswith('date')]

        for field in date_fields:
            date_string = file_metadata[field]
            date_object = datetime.datetime.strptime(date_string, '%Y-%m-%d')
            file_metadata[field] = date_object

        return file_metadata


class StandardizedDataUpload(FormView):
    template_name = 'data_import/upload.html'
    form_class = UploadForm
    success_url = 'upload-success/'

    def form_valid(self, form):
        upload = Upload.objects.create()

        uploaded_file = form.cleaned_data['standardized_file']
        now = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
        uploaded_file.name = '{}-{}'.format(now, uploaded_file.name)

        s_file_meta = {
            'standardized_file': uploaded_file,
            'upload': upload,
            'reporting_year': form.cleaned_data['reporting_year'],
        }

        s_file = StandardizedFile.objects.create(**s_file_meta)

        copy_to_database.delay(s_file_id=s_file.id)

        return super().form_valid(form)


class Uploads(ListView):
    '''
    Index of data import. Display a list of standardized uploads,
    their statuses, and next steps.
    '''
    template_name = 'data_import/index.html'
    model = Upload
    context_object_name = 'uploads'
    paginate_by = 25

    def get_queryset(self):
        return Upload.objects.filter(standardized_file__isnull=False)


class Review(ListView):
    template_name = 'data_import/review.html'
    paginate_by = 25
    context_object_name = 'items'

    def dispatch(self, request, *args, **kwargs):
        '''
        If there are no more items to review, flush the matched
        data to the raw_payroll table, and redirect to the index.

        Otherwise, show the review.
        '''
        if self.get_queryset(**kwargs):
            return super().dispatch(request, *args, **kwargs)

        else:
            self.q.flush()

        return redirect(reverse('data-import'))


class RespondingAgencyReview(Review):
    @property
    def q(self):
        return RespondingAgencyQueue(self.kwargs['s_file_id'])

    def get_queryset(self, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT *
                FROM {}
                WHERE processed = FALSE
                ORDER BY name
            '''.format(self.q.table_name))

            return [row for row in cursor]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'entity': 'responding agency',
            'entities': 'responding agencies',
            'display_slice': 1,
            's_file_id': self.kwargs['s_file_id'],
        })

        return context


def match(request):
    entity_type = request.GET['entity_type']
    s_file_id = request.GET['s_file_id']
    unseen = request.GET['unseen']
    match = request.GET['match']

    q_map = {
        'responding-agency': RespondingAgencyQueue,
    }

    q_obj = q_map[entity_type]

    q = q_obj(s_file_id)
    q.process(unseen, match)

    return JsonResponse({'status_code': 200})


def review_entity_lookup(request, entity_type):
    q = request.GET['term']

    model_map = {
        'responding-agency': RespondingAgency,
    }

    model_obj = model_map[entity_type]

    entities = []

    for e in RespondingAgency.objects.filter(name__istartswith=q):
        data = {
            'label': str(e),
            'value': str(e),
        }
        entities.append(data)

    return JsonResponse(entities, safe=False)
