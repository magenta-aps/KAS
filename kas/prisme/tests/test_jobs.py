import os
from unittest.mock import patch

import django_rq
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.test import TestCase
from fakeredis import FakeStrictRedis
from rq import Queue

from kas.jobs import generate_final_settlements_for_year, generate_batch_and_transactions_for_year
from kas.models import TaxYear, PersonTaxYear, Person, PolicyTaxYear, PensionCompany
from prisme.jobs import import_pre_payment_file
from prisme.models import PrePaymentFile, Transaction
from worker.models import Job


class ImportPrePaymentFile(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            username='user',
            email='test@example.com'
        )
        self.tax_year = TaxYear.objects.create(year=2020, year_part='ligning')
        self.company = PensionCompany.objects.create(name='test_company')
        for i, cpr in enumerate(['0708614866', '0103897769'], start=1):  # same as in test file
            person = Person.objects.create(cpr=cpr, name='person {}'.format(i))
            person_tax_year = PersonTaxYear.objects.create(person=person,
                                                           number_of_days=365,
                                                           tax_year=self.tax_year)

            PolicyTaxYear.objects.create(person_tax_year=person_tax_year,
                                         prefilled_amount=100000*i,
                                         self_reported_amount=100000*i,
                                         slutlignet=True,
                                         pension_company=self.company)

        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'data/PGF85_2021_897021_28-04-2021_080136.csv'), mode='rb') as test_data:
            self.prepayment = PrePaymentFile.objects.create(uploaded_by=self.user, file=File(test_data))

    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_import(self, django_rq):
        Job.schedule_job(import_pre_payment_file,
                         job_type='import_pre_payment_file',
                         job_kwargs={'pk': self.prepayment.pk},
                         created_by=self.user)

        new_transactions = Transaction.objects.filter(source_content_type=ContentType.objects.get_for_model(PrePaymentFile),
                                                      object_id=self.prepayment.pk)

        self.assertEqual(2, new_transactions.count())

        first_person_transactions = new_transactions.filter(person_tax_year__person__cpr='0708614866')
        self.assertEqual(first_person_transactions.count(), 1)
        first_person_transaction = first_person_transactions.first()
        self.assertEqual(first_person_transaction.amount, -18000)
        self.assertEqual(first_person_transaction.status, 'transferred')
        self.assertEqual(first_person_transactions.first().type, 'prepayment')

        second_person_transactions = new_transactions.filter(person_tax_year__person__cpr='0103897769')
        self.assertEqual(second_person_transactions.count(), 1)
        second_person_transaction = second_person_transactions.first()
        self.assertEqual(second_person_transaction.amount, -7000)
        self.assertEqual(second_person_transaction.status, 'transferred')
        self.assertEqual(second_person_transactions.first().type, 'prepayment')

    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_generate_transactions(self, django_rq):
        # import pre_payment file
        Job.schedule_job(import_pre_payment_file,
                         job_type='import_pre_payment_file',
                         job_kwargs={'pk': self.prepayment.pk},
                         created_by=self.user)

        # generate final settlement
        Job.schedule_job(generate_final_settlements_for_year,
                         job_type='generate_final_settlements_for_year',
                         job_kwargs={'year_pk': self.tax_year.pk},
                         created_by=self.user)

        # generate batch and transactions
        Job.schedule_job(generate_batch_and_transactions_for_year,
                         job_type='generate_batch_and_transactions_for_year',
                         job_kwargs={'year_pk': self.tax_year.pk},
                         created_by=self.user)

        first_person_transactions = Transaction.objects.filter(person_tax_year__person__cpr='0708614866')
        first_person_prepayments = first_person_transactions.filter(type='prepayment')
        # 1 prepayment from file
        self.assertEqual(first_person_prepayments.count(), 1)
        self.assertEqual(first_person_prepayments.first().amount, -18000)

        first_person_10q = first_person_transactions.filter(type='prisme10q')
        # one 10Q transaction to transfer
        self.assertEqual(first_person_10q.count(), 1)
        # the citizen is owed 2.742kr
        self.assertEqual(first_person_10q.first().amount, -2742)

        second_person_transactions = Transaction.objects.filter(person_tax_year__person__cpr='0103897769')
        second_person_prepayments = first_person_transactions.filter(type='prepayment')
        # 1 prepayment from file
        self.assertEqual(second_person_prepayments.count(), 1)
        self.assertEqual(second_person_prepayments.first().amount, -18000)

        second_person_10q = second_person_transactions.filter(type='prisme10q')
        # one 10Q transaction to transfer
        self.assertEqual(second_person_10q.count(), 1)
        # the citizen needs to pay 23.516kr
        self.assertEqual(second_person_10q.first().amount, 23516)
