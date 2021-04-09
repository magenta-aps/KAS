import os
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('kas', '0002_note'),
    ]

    def create_groups(apps, schema_editor):
        from django.contrib.auth.models import Group
        group, _ = Group.objects.get_or_create(name=os.environ['DJANGO_ADMIN_GROUP'])

    operations = [
        migrations.RunPython(create_groups),
    ]
