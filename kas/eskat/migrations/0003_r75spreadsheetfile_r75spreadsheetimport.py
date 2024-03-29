# Generated by Django 3.2.12 on 2022-06-21 12:42

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import eskat.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eskat', '0002_auto_20220516_0856'),
    ]

    operations = [
        migrations.CreateModel(
            name='R75SpreadsheetFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(upload_to=eskat.models.r75_spreadsheet_file_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['xlsx'])])),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='R75SpreadsheetImport',
            fields=[
                ('pt_census_guid', models.UUIDField()),
                ('tax_year', models.IntegerField()),
                ('cpr', models.TextField()),
                ('r75_ctl_sekvens_guid', models.UUIDField(primary_key=True, serialize=False)),
                ('r75_ctl_indeks_guid', models.UUIDField()),
                ('idx_nr', models.IntegerField()),
                ('res', models.TextField(blank=True, null=True)),
                ('ktd', models.TextField(blank=True, null=True)),
                ('ktt', models.TextField(blank=True, null=True)),
                ('kontotype', models.TextField(blank=True, null=True)),
                ('ibn', models.TextField(blank=True, null=True)),
                ('esk', models.TextField(blank=True, null=True)),
                ('ejerstatuskode', models.TextField(blank=True, null=True)),
                ('indestaaende', models.TextField(blank=True, db_column='indestående', null=True)),
                ('renteindtaegt', models.TextField(blank=True, db_column='renteindtægt', null=True)),
                ('r75_dato', models.TextField(blank=True, null=True)),
                ('file', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='eskat.r75spreadsheetfile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
