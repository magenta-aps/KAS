from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from eskat.jobs import generate_sample_data
from worker.models import Job


class Command(BaseCommand):
    help = 'Populates database with some dummy data'

    def handle(self, *args, **options):
        admin_user, _ = get_user_model().objects.get_or_create(
            username='admin'
        )

        Job.schedule_job(
            generate_sample_data,
            'GenerateSampleData',
            admin_user,
        )
