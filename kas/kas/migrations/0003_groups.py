import os

from django.contrib.auth.models import Permission
from django.core.management.sql import emit_post_migrate_signal
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('kas', '0002_note'),
    ]

    def create_groups(apps, schema_editor):
        from django.contrib.auth.models import Group
        group, _ = Group.objects.get_or_create(name=os.environ['DJANGO_ADMIN_GROUP'])

        # Send signal that will trigger Permission object creation
        emit_post_migrate_signal(2, False, 'default')

        kas_permissions = Permission.objects.filter(content_type__app_label='kas')
        group.permissions.set([
            kas_permissions.get(codename='add_pensioncompany'),
            kas_permissions.get(codename='change_pensioncompany'),

            kas_permissions.get(codename='add_persontaxyear'),
            kas_permissions.get(codename='change_persontaxyear'),

            kas_permissions.get(codename='add_policytaxyear'),
            kas_permissions.get(codename='change_policytaxyear'),
        ])

    operations = [
        migrations.RunPython(create_groups),
    ]
