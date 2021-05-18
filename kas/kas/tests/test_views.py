from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from kas.models import TaxYear, PensionCompany, Person, PolicyTaxYear, PersonTaxYear


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        self.username = 'test'
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = 'test'
        self.user.set_password(self.password)
        self.user.save()
        self.tax_year = TaxYear.objects.create(year=2021)
        self.person = Person.objects.create(cpr='1234567890')
        self.person_tax_year = PersonTaxYear.objects.create(tax_year=self.tax_year,
                                                            person=self.person,
                                                            number_of_days=1)
        self.pension_company = PensionCompany.objects.create()
        self.policy_tax_year = PolicyTaxYear.objects.create(person_tax_year=self.person_tax_year,
                                                            pension_company=self.pension_company,
                                                            prefilled_amount=35)


class SelfReportedAmountUpdateViewTestCase(BaseTestCase):

    def test_not_logged_in(self):
        r = self.client.get(reverse('kas:change-self-reported-amount', args=[self.policy_tax_year.pk]))
        # should redirect to login page
        self.assertEqual(r.status_code, 302)

    def test_valid_get(self):
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        r = self.client.get(reverse('kas:change-self-reported-amount', kwargs={'pk': self.policy_tax_year.pk}))
        self.assertEqual(r.status_code, 200)

    def test_invalid_urls(self):
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        r = self.client.get(reverse('kas:change-self-reported-amount', args=[self.policy_tax_year.pk+1]))
        self.assertEqual(r.status_code, 404)

    def test_form_submit(self):
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        r = self.client.post(reverse('kas:change-self-reported-amount', args=[self.policy_tax_year.pk]),
                             follow=True,
                             data={'self_reported_amount': 99,
                                   'notes-TOTAL_FORMS': 1,
                                   'notes-INITIAL_FORMS': 0,
                                   'uploads-TOTAL_FORMS': 1,
                                   'uploads-INITIAL_FORMS': 0})
        self.assertEqual(r.status_code, 200)
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertEqual(policy_tax_year.self_reported_amount, 99)
        self.assertFalse(policy_tax_year.notes.exists())
        self.assertFalse(policy_tax_year.person_tax_year.notes.exists())
        self.assertFalse(policy_tax_year.policy_documents.exists())
        self.assertFalse(policy_tax_year.person_tax_year.policydocument_set.exists())

    def test_submit_note(self):
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        r = self.client.post(reverse('kas:change-self-reported-amount', args=[self.policy_tax_year.pk]),
                             follow=True,
                             data={'self_reported_amount': 99,
                                   'notes-TOTAL_FORMS': 1,
                                   'notes-0-content': 'test',
                                   'notes-INITIAL_FORMS': 0,
                                   'uploads-TOTAL_FORMS': 1,
                                   'uploads-INITIAL_FORMS': 0})
        self.assertEqual(r.status_code, 200)
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertEqual(policy_tax_year.self_reported_amount, 99)
        self.assertEqual(policy_tax_year.notes.count(), 1)
        self.assertEqual(policy_tax_year.notes.first().author, self.user)
        self.assertEqual(policy_tax_year.person_tax_year.notes.count(), 1)
        self.assertFalse(policy_tax_year.policy_documents.exists())
        self.assertFalse(policy_tax_year.person_tax_year.policydocument_set.exists())

    def test_submit_document(self):
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        r = self.client.post(reverse('kas:change-self-reported-amount', args=[self.policy_tax_year.pk]),
                             follow=True,
                             data={'self_reported_amount': 99,
                                   'notes-TOTAL_FORMS': 1,
                                   'notes-INITIAL_FORMS': 0,
                                   'uploads-TOTAL_FORMS': 1,
                                   'uploads-0-description': 'test_description',
                                   'uploads-0-file': SimpleUploadedFile(name='test', content=b'test'),
                                   'uploads-INITIAL_FORMS': 0})
        self.assertEqual(r.status_code, 200)
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertEqual(policy_tax_year.self_reported_amount, 99)
        self.assertFalse(policy_tax_year.notes.exists())
        self.assertFalse(policy_tax_year.person_tax_year.notes.exists())
        self.assertEquals(policy_tax_year.policy_documents.count(), 1)
        self.assertEquals(policy_tax_year.person_tax_year.policydocument_set.count(), 1)
        policy_documents = policy_tax_year.policy_documents.first()
        self.assertEqual(policy_documents.uploaded_by, self.user)

    def test_submit_note_and_document(self):
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        r = self.client.post(reverse('kas:change-self-reported-amount', args=[self.policy_tax_year.pk]),
                             follow=True,
                             data={'self_reported_amount': 99,
                                   'notes-TOTAL_FORMS': 1,
                                   'notes-INITIAL_FORMS': 0,
                                   'notes-0-content': 'test',
                                   'uploads-TOTAL_FORMS': 1,
                                   'uploads-0-description': 'test_description',
                                   'uploads-0-file': SimpleUploadedFile(name='test', content=b'test'),
                                   'uploads-INITIAL_FORMS': 0})
        self.assertEqual(r.status_code, 200)
        policy_tax_year = PolicyTaxYear.objects.get(pk=self.policy_tax_year.pk)
        self.assertEqual(policy_tax_year.self_reported_amount, 99)
        self.assertEqual(policy_tax_year.notes.count(), 1)
        self.assertEqual(policy_tax_year.notes.first().author, self.user)
        self.assertEqual(policy_tax_year.person_tax_year.notes.count(), 1)
        self.assertEquals(policy_tax_year.policy_documents.count(), 1)
        self.assertEquals(policy_tax_year.person_tax_year.policydocument_set.count(), 1)
        policy_documents = policy_tax_year.policy_documents.first()
        self.assertEqual(policy_documents.uploaded_by, self.user)


class EditAmountsUpdateViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(EditAmountsUpdateViewTestCase, self).setUp()
        self.tax_year.year_part = 'ligning'
        self.tax_year.save()
        self.client.login(username=self.username, password=self.password)

    def test_not_logged_in(self):
        self.client.logout()
        r = self.client.get(reverse('kas:change-edit-amounts', args=[self.policy_tax_year.pk]))
        # should redirect to login page
        self.assertEqual(r.status_code, 302)

    def test_valid_get(self):
        r = self.client.get(reverse('kas:change-edit-amounts', kwargs={'pk': self.policy_tax_year.pk}))
        self.assertEqual(r.status_code, 200)

    def test_self_reported_amount(self):
        self.policy_tax_year.self_reported_amount = 924
        self.policy_tax_year.save()
        r = self.client.get(reverse('kas:change-edit-amounts', kwargs={'pk': self.policy_tax_year.pk}))
        self.assertEqual(r.context['form']['assessed_amount'].value(), 924)
        self.assertEqual(r.context['form']['adjusted_r75_amount'].value(), 35)

    def test_adjusted_r75_amount(self):
        self.policy_tax_year.adjusted_r75_amount = 501
        self.policy_tax_year.save()
        r = self.client.get(reverse('kas:change-edit-amounts', kwargs={'pk': self.policy_tax_year.pk}))
        self.assertEqual(r.context['form']['assessed_amount'].value(), 501)
        self.assertEqual(r.context['form']['adjusted_r75_amount'].value(), 501)

    def test_prefilled_amount(self):
        r = self.client.get(reverse('kas:change-edit-amounts', kwargs={'pk': self.policy_tax_year.pk}))
        self.assertEqual(r.context['form']['assessed_amount'].value(), 35)
        self.assertEqual(r.context['form']['adjusted_r75_amount'].value(), 35)
