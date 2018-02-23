# Generated by Django 2.0.2 on 2018-02-22 22:34

import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0003_employer_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(max_length=255, null=True),
        ),
    ]
