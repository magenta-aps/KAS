from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Creates or updates a user with login admin and the specified password'

    def add_arguments(self, parser):
        parser.add_argument('admin_password', type=str)

    def handle(self, *args, **options):
        # Sanity check: We do not want a weak password in production
        if settings.ENVIRONMENT == "production" and options["admin_password"] == "admin":
            raise Exception("Will not create admin user with weak password in production")

        User.objects.update_or_create(
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "email": "",
                "password": make_password(options["admin_password"]),
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            },
            username="admin"
        )
