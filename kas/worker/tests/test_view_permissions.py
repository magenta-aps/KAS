from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class PermissionTestCase(TestCase):
    """
    Tests that the project.view_mixin.IsStaffMixin works correctly
    """

    def setUp(self) -> None:
        self.username = 'test'
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = 'test'
        self.user.set_password(self.password)
        self.user.save()
        self.staff_username = 'staff'
        self.staff_password = 'staff_test 1234'
        self.staff = get_user_model().objects.create_user(username=self.staff_username, is_staff=True)
        self.staff.set_password(self.staff_password)
        self.staff.save()

    def test_job_list_not_logged_in(self):
        r = self.client.get(reverse('worker:job_list'), follow=True)
        # results in a redirect to the login page
        self.assertRedirects(r, reverse('login')+'?next=/worker/jobs/', 302)
        self.assertEqual(r.status_code, 200)

    def test_job_list_none_staff_user(self):
        self.client.login(username=self.username, password=self.password)
        r = self.client.get(reverse('worker:job_list'))
        self.assertEqual(r.status_code, 403)

    def test_job_list_staff_user(self):
        self.client.login(username=self.staff_username, password=self.staff_password)
        r = self.client.get(reverse('worker:job_list'))
        self.assertEqual(r.status_code, 200)
