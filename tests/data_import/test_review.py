import json

from django.urls import reverse
import pytest

from data_import.utils.queues import ReviewQueue
from data_import.views import RespondingAgencyReview, RespondingAgencyQueue


@pytest.mark.parametrize('remaining,item', [
    (1, (bytes('foo', encoding='utf-8'), {'name': 'bar'})),
    (0, (None, None)),
    (1, (None, None)),
])
def test_review_dispatch(mocker, admin_client, remaining, item):
    mock_queue = mocker.PropertyMock(spec=ReviewQueue)
    mock_queue.remaining = remaining
    mock_queue.checkout.return_value = item

    mock_q = mocker.patch.object(RespondingAgencyReview, 'q', new_callable=mocker.PropertyMock)
    mock_q.return_value = mock_queue

    mock_transition = mocker.patch.object(RespondingAgencyReview, 'finish_review_step')

    render_review = remaining and all(item)
    flush_queue = remaining and not all(item)
    nothing_to_review = not remaining

    review_url = reverse('review-responding-agency', kwargs={'s_file_id': 99})

    if flush_queue:
        review_url += '?flush=true'

    rv = admin_client.get(review_url)

    if render_review:
        assert rv.status_code == 200

    elif flush_queue:
        assert rv.status_code == 302
        assert mock_transition.call_count == 1
        assert rv.url == reverse(
            'admin:data_import_standardizedfile_change',
            args=(99,)
        )

    elif nothing_to_review:
        assert rv.status_code == 302
        assert mock_transition.call_count == 1
        assert rv.url == reverse(
            'admin:data_import_standardizedfile_change',
            args=(99,)
        )


def test_match(mocker, admin_client):
    mock_queue = mocker.MagicMock(spec=RespondingAgencyQueue)
    mocker.patch('data_import.views.RespondingAgencyQueue', return_value=mock_queue)

    data = {
        'entity_type': 'responding-agency',
        's_file_id': 99,
        'unseen': 'foo',
    }

    with pytest.raises(AssertionError):
        admin_client.post(reverse('match-entity'), data={'data': json.dumps(data)})

    data['match'] = 1

    admin_client.post(reverse('match-entity'), data={'data': json.dumps(data)})

    mock_queue.match_or_create.assert_called_once_with(data['unseen'], data['match'])


def test_add(mocker, admin_client):
    mock_queue = mocker.MagicMock(spec=RespondingAgencyQueue)
    mocker.patch('data_import.views.RespondingAgencyQueue', return_value=mock_queue)

    data = {
        'entity_type': 'responding-agency',
        's_file_id': 99,
        'unseen': 'foo',
        'match': 1,
    }

    with pytest.raises(AssertionError):
        admin_client.post(reverse('add-entity'), data={'data': json.dumps(data)})

    del data['match']

    admin_client.post(reverse('add-entity'), data={'data': json.dumps(data)})

    mock_queue.match_or_create.assert_called_once_with(data['unseen'], None)
