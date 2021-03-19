from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from worker.job_registry import get_job_types, resolve_job_function
from worker.models import Job


class Command(BaseCommand):
    help = 'Populates database with some dummy data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete old data before importing dummy data',
        )

    def handle(self, *args, **options):
        job_data = get_job_types()['ResetToMockupOnly']
        job_function = resolve_job_function(job_data['function'])

        admin_user, _ = get_user_model().objects.get_or_create(
            username='admin'
        )

        Job.schedule_job(
            job_function,
            'ResetToMockupOnly',
            admin_user,
            job_kwargs={'skip_deletions': not options['delete']},
        )
