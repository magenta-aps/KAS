import os

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates dummy users"

    def handle(self, *args, **options):
        if settings.ENVIRONMENT in ("production", "staging"):
            raise Exception(f"Will not create dummy users in {settings.ENVIRONMENT}")

        User.objects.update_or_create(
            defaults={
                "is_superuser": True,
                "is_staff": True,
                "password": make_password("super"),
            },
            username="super",
        )
        admin, created = User.objects.update_or_create(
            # Admin user
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "email": "",
                "password": make_password(os.environ.get("ADMIN_PASSWORD", "admin")),
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
            },
            username="admin",
        )
        if created:
            admin.groups.add(Group.objects.get(name="administrator"))

        for name in ("Sagsbehandler", "Borgerservice", "Regnskab", "Skatteråd"):
            user, created = User.objects.update_or_create(
                username=name.lower(),
                defaults={
                    "password": make_password(name.lower()),
                    "first_name": name.capitalize(),
                    "last_name": name.capitalize(),
                    "is_active": True,
                },
            )
            if created:
                # if the user was created add the user to the group
                user.groups.add(Group.objects.get(name=name))
