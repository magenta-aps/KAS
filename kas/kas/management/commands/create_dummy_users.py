import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Creates dummy users'

    def handle(self, *args, **options):
        if settings.ENVIRONMENT == "production":
            raise Exception("Will not create dummy users in production")

        User.objects.update_or_create(
            defaults={'is_superuser': True,
                      'is_staff': True,
                      'password': make_password('super')},
            username='super'
        )
        admin, created = User.objects.update_or_create(
            # Admin user
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "email": "",
                "password": make_password(os.environ.get('ADMIN_PASSWORD', 'admin')),
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
            },
            username="admin"
        )
        admin.groups.add(Group.objects.get(name='administrator'))
        User.objects.update_or_create(
            defaults={
                "first_name": "Normal",
                "last_name": "User",
                "email": "",
                "password": make_password('user'),
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
            },
            username="user"
        )
