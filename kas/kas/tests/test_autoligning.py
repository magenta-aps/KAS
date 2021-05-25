from unittest.mock import patch

import django_rq
from django.contrib.auth import get_user_model
from django.test import TestCase
from fakeredis import FakeStrictRedis
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rq import Queue

from kas.jobs import autoligning
from kas.models import TaxYear, Person, PersonTaxYear, PensionCompany, PolicyTaxYear, Note, PolicyDocument
from worker.models import Job


class AutoligningTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(AutoligningTestCase, cls).setUpClass()
        cls.rest_user = get_user_model().objects.create(username='rest')
        cls.clerk_user = get_user_model().objects.create(username='clerk')
        cls.token = 'test'
        cls.token = Token.objects.create(user=cls.rest_user, key='test')
        cls.year = TaxYear.objects.create(year=2020)
        cls.person = Person.objects.create(cpr='0000000000')
        cls.person_tax_year = PersonTaxYear.objects.create(tax_year=cls.year, person=cls.person, number_of_days=0)
        cls.pension_company = PensionCompany.objects.create(name='company')

    def setUp(self) -> None:
        self.client = APIClient()
        self.policy_tax_year = PolicyTaxYear.objects.create(person_tax_year=self.person_tax_year,
                                                            pension_company=self.pension_company,
                                                            prefilled_amount=0,
                                                            policy_number='134')
        # recalculate is execute as part of the import
        # so execute it here and we can verify Updated by import get filtered
        self.policy_tax_year._change_reason = 'Updated by import'
        self.policy_tax_year.recalculate()
        del self.policy_tax_year._change_reason

    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_created_by_citizen(self, djang_rq):
        policy_tax_year = PolicyTaxYear(person_tax_year=self.person_tax_year,
                                        pension_company=self.pension_company,
                                        policy_number='200')
        policy_tax_year._history_user = self.rest_user  # fake creating through the res API
        policy_tax_year.save()
        Job.schedule_job(autoligning,
                         job_type='autoligning',
                         job_kwargs={'year_pk': self.year.pk},
                         created_by=self.clerk_user)
        self.assertEqual(PolicyTaxYear.objects.filter(person_tax_year=self.person_tax_year,
                                                      slutlignet=False,
                                                      efterbehandling=True).count(), 1)
        self.assertEqual(TaxYear.objects.get(pk=self.year.pk).year_part, 'ligning')

    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_changed_by_citizen(self, djano_rq):
        self.policy_tax_year.self_reported_amount = 300
        self.policy_tax_year._history_user = self.rest_user  # citizen changes self_reported_amount
        self.policy_tax_year.save()
        Job.schedule_job(autoligning,
                         job_type='autoligning',
                         job_kwargs={'year_pk': self.year.pk},
                         created_by=self.clerk_user)

        self.assertEqual(PolicyTaxYear.objects.filter(person_tax_year=self.person_tax_year,
                                                      slutlignet=False,
                                                      efterbehandling=True).count(), 1)
        self.assertEqual(TaxYear.objects.get(pk=self.year.pk).year_part, 'ligning')

    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_changes_by_clerk(self, django_rq):
        self.policy_tax_year.self_reported_amount = 500
        self.policy_tax_year._history_user = self.clerk_user  # citizen changes self_reported_amount
        self.policy_tax_year.save()
        Job.schedule_job(autoligning,
                         job_type='autoligning',
                         job_kwargs={'year_pk': self.year.pk},
                         created_by=self.clerk_user)

        self.assertEqual(PolicyTaxYear.objects.filter(person_tax_year=self.person_tax_year,
                                                      slutlignet=False,
                                                      efterbehandling=True).count(), 1)
        self.assertEqual(TaxYear.objects.get(pk=self.year.pk).year_part, 'ligning')

    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_general_notes_empty_text(self, django_rq):
        self.person_tax_year.general_notes = ''
        self.person_tax_year.save()
        Job.schedule_job(autoligning,
                         job_type='autoligning',
                         job_kwargs={'year_pk': self.year.pk},
                         created_by=self.clerk_user)

        # empty string should not trigger efterbehandling
        self.assertEqual(PolicyTaxYear.objects.filter(person_tax_year=self.person_tax_year,
                                                      slutlignet=True,
                                                      efterbehandling=False).count(), 1)

        self.assertEqual(PolicyTaxYear.objects.filter(person_tax_year=self.person_tax_year,
                                                      slutlignet=False,
                                                      efterbehandling=True).count(), 0)
        self.assertEqual(TaxYear.objects.get(pk=self.year.pk).year_part, 'ligning')

    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_general_notes_contains_text(self, django_rq):
        # but a string with text should
        self.person_tax_year.general_notes = 'this is a test'
        self.person_tax_year.save()

        Job.schedule_job(autoligning,
                         job_type='autoligning',
                         job_kwargs={'year_pk': self.year.pk},
                         created_by=self.clerk_user)

        self.assertEqual(PolicyTaxYear.objects.filter(person_tax_year=self.person_tax_year,
                                                      slutlignet=False,
                                                      efterbehandling=True).count(), 1)

        self.assertEqual(PolicyTaxYear.objects.filter(person_tax_year=self.person_tax_year,
                                                      slutlignet=True,
                                                      efterbehandling=False).count(), 0)
        self.assertEqual(TaxYear.objects.get(pk=self.year.pk).year_part, 'ligning')

    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_notes_exists(self, django_rq):
        Note.objects.create(person_tax_year=self.person_tax_year, author=self.clerk_user, content='text')
        Job.schedule_job(autoligning,
                         job_type='autoligning',
                         job_kwargs={'year_pk': self.year.pk},
                         created_by=self.clerk_user)

        self.assertEqual(PolicyTaxYear.objects.filter(person_tax_year=self.person_tax_year,
                                                      slutlignet=False,
                                                      efterbehandling=True).count(), 1)
        self.assertEqual(TaxYear.objects.get(pk=self.year.pk).year_part, 'ligning')

    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_policy_documents_exists(self, django_rq):
        PolicyDocument.objects.create(person_tax_year=self.person_tax_year, name='test', description='test description')
        Job.schedule_job(autoligning,
                         job_type='autoligning',
                         job_kwargs={'year_pk': self.year.pk},
                         created_by=self.clerk_user)
        self.assertEqual(PolicyTaxYear.objects.filter(person_tax_year=self.person_tax_year,
                                                      slutlignet=False,
                                                      efterbehandling=True).count(), 1)
        self.assertEqual(TaxYear.objects.get(pk=self.year.pk).year_part, 'ligning')

    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_slutlignet(self, django_rq):
        Job.schedule_job(autoligning,
                         job_type='autoligning',
                         job_kwargs={'year_pk': self.year.pk},
                         created_by=self.clerk_user)
        self.assertEqual(PolicyTaxYear.objects.filter(person_tax_year=self.person_tax_year,
                                                      slutlignet=True,
                                                      efterbehandling=False).count(), 1)
        self.assertEqual(PolicyTaxYear.objects.filter(person_tax_year=self.person_tax_year,
                                                      slutlignet=False,
                                                      efterbehandling=True).count(), 0)
        self.assertEqual(TaxYear.objects.get(pk=self.year.pk).year_part, 'ligning')
