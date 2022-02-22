from django.test import TestCase
from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from kas.models import RepresentationToken
from django.db.models import Q


class GroupPermissionTestCase(TestCase):
    black_listed_models = [RepresentationToken]

    @classmethod
    def get_content_types_for_app(cls, app):
        """
        :param app: App name to get the ContentTypes for
        :return: All ContentTypes for the app unless the model is on the blacklist
        """
        models = []
        app = apps.get_app_config(app)
        for model in app.get_models():
            if model not in cls.black_listed_models:
                models.append(model)
        return ContentType.objects.get_for_models(*models).values()

    def test_view_permissions_for_kas(self):
        """
        all groups should have view_* permissions on all kas models, except pensioncompanysummaryfile.
        If this fails you most likely have added a new model without adding view_ permission to the groups
        or forgot to add the model to the blacklist.
        """
        kas_content_types = self.get_content_types_for_app('kas')
        view_permissions = Permission.objects.filter(content_type__in=kas_content_types
                                                     ).filter(codename__startswith='view_').exclude(
            content_type__model='pensioncompanysummaryfile')
        for group in Group.objects.all():
            group_view_permission = group.permissions.filter(
                content_type__in=kas_content_types).filter(
                codename__startswith='view_').exclude(
                content_type__model='pensioncompanysummaryfile')
            self.assertCountEqual(view_permissions, group_view_permission)

    def test_administrator_worker_permission(self):
        """
        only users in the administrator group should be able to view/add/change jobs.
        """
        content_types = self.get_content_types_for_app('worker')
        permissions = Permission.objects.filter(content_type__in=content_types)
        group = Group.objects.get(name='administrator')
        # administrator group should have all permissions on the Worker models
        self.assertTrue(set(group.permissions.filter(content_type__in=content_types)).issubset(set(permissions)))

    def test_sagsbehandler_kas_permission(self):
        kas_content_types = self.get_content_types_for_app('kas')
        group = Group.objects.get(name='Sagsbehandler')
        expected_kas_permission = Permission.objects.filter(
            content_type__in=kas_content_types).exclude(
            codename__startswith='delete_').exclude(
            Q(codename='add_taxyear') | Q(codename='change_taxyear'))
        current_group_permissions = group.permissions.filter(content_type__in=kas_content_types)
        self.assertCountEqual(expected_kas_permission, current_group_permissions)

    def test_borger_service_kas_permissions(self):
        """
        Borger service employee is allowed to add policy documents and notes.
        """
        kas_content_types = self.get_content_types_for_app('kas')
        group = Group.objects.get(name='Borgerservice')
        expected_kas_permission = Permission.objects.filter(
            content_type__in=kas_content_types).filter(
            Q(codename__startswith='view_') | Q(codename__in=['add_policydocument',
                                                              'add_note'])).exclude(content_type__model='pensioncompanysummaryfile')
        current_group_permissions = group.permissions.filter(content_type__in=kas_content_types)
        self.assertCountEqual(expected_kas_permission, current_group_permissions)

    def test_regnskab_prisme_permissions(self):
        """
        Regnskab can add add prisme10qbatch instances
        """
        prisme_content_types = self.get_content_types_for_app('prisme')
        group = Group.objects.get(name='Regnskab')
        expected_prism_permission = Permission.objects.filter(
            content_type__in=prisme_content_types).filter(
            Q(codename__startswith='view_') | Q(codename='add_prisme10qbatch'))
        current_group_permissions = group.permissions.filter(content_type__in=prisme_content_types)
        self.assertCountEqual(expected_prism_permission, current_group_permissions)
