from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from eskat.jobs import generate_sample_data
from worker.models import Job
from django.conf import settings


class Command(BaseCommand):
    help = 'Populates database with some dummy data'

    def handle(self, *args, **options):
        if settings.ENVIRONMENT in ("production", 'staging'):
            raise Exception(f"Will not create dummy data in {settings.ENVIRONMENT}")

        admin_user, _ = get_user_model().objects.get_or_create(
            username='admin'
        )

        Job.schedule_job(
            generate_sample_data,
            'GenerateSampleData',
            admin_user,
        )
