# Generated by Django 2.2.26 on 2022-02-21 12:10
from django.contrib.auth.management import create_permissions
from django.db import migrations


def add_view_list_permission_to_administrator_and_sagsbehandler(apps, schema_editor):

    # https://stackoverflow.com/questions/38822273/how-to-add-a-permission-to-a-user-group-during-a-django-migration
    # modified
    app_config = apps.get_app_config('kas')
    old = getattr(app_config, 'models_module', None)
    app_config.models_module = True
    create_permissions(app_config, verbosity=0)
    app_config.models_module = old

    Permission = apps.get_model('auth', 'Permission')
    list_permission = Permission.objects.get(codename='list_persontaxyear')
    Group = apps.get_model('auth', 'Group')
    administrator = Group.objects.get(name='administrator')
    administrator.permissions.add(list_permission)
    sagsbehandler = Group.objects.get(name='Sagsbehandler')
    sagsbehandler.permissions.add(list_permission)
    read_write_summary_file_permission = Permission.objects.filter(content_type__model='pensioncompanysummaryfile')
    for name in ('Borgerservice', 'Regnskab', 'Skatteråd'):
        # only administrator and sagsbehandler should be able to add/view summary files
        group = Group.objects.get(name=name)
        group.permissions.remove(*read_write_summary_file_permission)


def remove_view_list_permission_to_administrator_and_sagsbehandler(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    Group = apps.get_model('auth', 'Group')
    Permission.objects.get(codename='list_persontaxyear').delete()
    read_write_summary_file_permission = Permission.objects.filter(content_type__model='pensioncompanysummaryfile')
    for name in ('Borgerservice', 'Regnskab', 'Skatteråd'):
        group = Group.objects.get(name=name)
        group.permissions.add(*read_write_summary_file_permission)


class Migration(migrations.Migration):

    dependencies = [
        ('kas', '0025_usergroups'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='persontaxyear',
            options={'ordering': ['-tax_year__year', 'person__name'], 'permissions': [('list_persontaxyear', 'User is allow to use persontaxyear lists.')]},
        ),
        migrations.RunPython(add_view_list_permission_to_administrator_and_sagsbehandler,
                             reverse_code=remove_view_list_permission_to_administrator_and_sagsbehandler)
    ]
