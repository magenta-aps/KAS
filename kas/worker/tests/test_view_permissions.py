from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse


class PermissionTestCase(TestCase):
    """
    Tests that the project.view_mixin.IsStaffMixin works correctly
    """

    def setUp(self) -> None:
        self.username = "test"
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = "test"
        self.user.set_password(self.password)
        self.user.save()
        self.admin_username = "admin"
        self.admin_password = "admin"
        self.admin = get_user_model().objects.create_user(username=self.admin_username)
        self.admin.set_password(self.admin_password)
        self.admin.groups.add(Group.objects.get(name="administrator"))
        self.admin.save()

    def test_job_list_not_logged_in(self):
        r = self.client.get(reverse("worker:job_list"), follow=True)
        # results in a redirect to the login page
        self.assertRedirects(r, reverse("kas:login") + "?next=/worker/jobs/", 302)
        self.assertEqual(r.status_code, 200)

    def test_job_list_none_admin_user(self):
        self.client.login(username=self.username, password=self.password)
        r = self.client.get(reverse("worker:job_list"))
        self.assertEqual(r.status_code, 403)

    def test_job_list_admin_user(self):
        self.client.login(username=self.admin_username, password=self.admin_password)
        r = self.client.get(reverse("worker:job_list"))
        self.assertEqual(r.status_code, 200)
