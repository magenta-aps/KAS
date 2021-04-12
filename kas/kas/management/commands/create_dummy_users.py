from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Creates dummy users'

    def handle(self, *args, **options):
        # Sanity check: We do not want a weak password in production
        if settings.ENVIRONMENT == "production":
            raise Exception("Will not create dev users in production")

        User.objects.update_or_create(
            defaults={
                "first_name": "Staff",
                "last_name": "User",
                "email": "",
                "password": make_password('staff'),
                "is_active": True,
                "is_staff": True,
                "is_superuser": False,
            },
            username="staff"
        )
        User.objects.update_or_create(
            defaults={
                "first_name": "Normal",
                "last_name": "User",
                "email": "",
                "password": make_password('normal'),
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
            },
            username="normal"
        )
