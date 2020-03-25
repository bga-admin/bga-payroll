# Generated by Django 2.2.9 on 2020-03-18 20:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0030_alias_base_class'),
    ]

    operations = [
        migrations.RunSQL('''
            INSERT INTO payroll_employeralias (employer_id, name, preferred)
              SELECT id, name, TRUE
              FROM payroll_employer
        ''')
    ]
