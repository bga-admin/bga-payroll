# Generated by Django 2.0.2 on 2018-06-06 15:18

from django.core.management import call_command
from django.db import connection, migrations, models
import django.db.models.deletion


def insert_raw_population(*args):
    call_command('import_metadata', endpoints='population')


def delete_raw_population(*args):
    with connection.cursor() as cursor:
        cursor.execute('DROP TABLE raw_population')


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0012_classify_employers'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployerPopulation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('population', models.IntegerField()),
                ('data_year', models.IntegerField()),
                ('employer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='population', to='payroll.Employer')),
            ],
        ),
        migrations.RunPython(insert_raw_population, delete_raw_population),
    ]
