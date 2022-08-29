# Generated by Django 3.2.12 on 2022-06-08 10:04

from django.db import migrations

cprs = ('1212121212',)


def apply_migration(apps, schema_editor):
    Person = apps.get_model('kas', 'Person')
    Person.objects.filter(cpr__in=cprs).update(is_test_person=True)


def revert_migration(apps, schema_editor):
    Person = apps.get_model('kas', 'Person')
    Person.objects.filter(cpr__in=cprs).update(is_test_person=False)


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0038_auto_20220829_0858'),
    ]

    operations = [
        migrations.RunPython(apply_migration, reverse_code=revert_migration)
    ]
