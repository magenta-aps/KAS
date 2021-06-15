from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Creates or updates a user with login admin and the specified password'

    def add_arguments(self, parser):
        parser.add_argument('--type', type=str)
        parser.add_argument('--login', type=str)
        parser.add_argument('--password', type=str)

    def handle(self, *args, **options):

        if options['type'] == 'admin':
            username = options['login'] or 'admin'
            defaults = {
                "first_name": "Admin",
                "last_name": "User",
                "email": "",
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
            }
        elif options['type'] == 'staff':
            username = options['login'] or 'staff'
            defaults = {
                "email": "",
                "is_active": True,
                "is_staff": True,
                "is_superuser": False,
            }
        else:
            raise Exception("type must be either 'admin' or 'staff'")

        defaults["password"] = make_password(options["password"])

        # Sanity check: We do not want a weak password in production
        if settings.ENVIRONMENT == "production" and options["password"] in ("admin", "staff", username):
            raise Exception("Will not create user with weak password in production")

        User.objects.update_or_create(
            defaults=defaults,
            username=username
        )
