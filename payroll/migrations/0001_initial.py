# Generated by Django 2.0.2 on 2018-02-09 23:21

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GovernmentalUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=255, null=True)),
                ('last_name', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, null=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.Department')),
            ],
        ),
        migrations.CreateModel(
            name='Salary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('vintage', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Tenure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(null=True)),
                ('person', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='payroll.Person')),
                ('position', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='payroll.Position')),
                ('salary', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='payroll.Salary')),
            ],
        ),
        migrations.AddField(
            model_name='person',
            name='tenures',
            field=models.ManyToManyField(through='payroll.Tenure', to='payroll.Salary'),
        ),
        migrations.AddField(
            model_name='department',
            name='governmental_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payroll.GovernmentalUnit'),
        ),
    ]
