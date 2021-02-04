# Generated by Django 2.2.18 on 2021-02-04 11:29

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('end_at', models.DateTimeField(blank=True, null=True)),
                ('job_type', models.TextField(choices=[('slow_job', 'Slow job'), ('slow_job_with_children', 'Job with children'), ('job_with_exception', 'Job with exception')])),
                ('rq_job_id', models.TextField(blank=True, null=True)),
                ('checkpoint', models.TextField(blank=True, default='')),
                ('progress', models.IntegerField(blank=True, default=0)),
                ('status', models.TextField(blank=True, choices=[('queued', 'Pending'), ('started', 'Started'), ('deferred', 'Deferred'), ('failed', 'Failed'), ('finished', 'Finished')], default='queued')),
                ('traceback', models.TextField(blank=True, default='')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='worker.Job')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
    ]
