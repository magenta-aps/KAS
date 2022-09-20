# Generated by Django 2.2.26 on 2022-03-21 12:24

from django.db import migrations


def apply_migration(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')

    administrator_group = Group.objects.get(name='administrator')
    sagsbehandler_group = Group.objects.get(name='Sagsbehandler')
    for user in User.objects.filter(is_active=True).exclude(username__endswith='@magenta.dk'):
        if user.is_staff:
            # assign staff users to the new admin group
            user.groups.set([administrator_group])
        else:
            # assign user to sagsbehandler
            user.groups.set([sagsbehandler_group])
        # remove any directly assigned permissions
        user.user_permissions.all().delete()
        # remove is staff for none magenta admins
        user.is_staff = False
        user.save()


def reverse_migration(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    for user in User.objects.filter(groups__name='administrator'):
        # set is staff for administrators
        user.is_staff = True
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0027_auto_20220301_1335'),
    ]

    operations = [
        migrations.RunPython(apply_migration, reverse_code=reverse_migration)
    ]
