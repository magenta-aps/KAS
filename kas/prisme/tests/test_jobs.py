import os
from unittest.mock import patch

import django_rq
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.test import TestCase
from fakeredis import FakeStrictRedis
from rq import Queue

from kas.models import TaxYear, PersonTaxYear, Person
from prisme.jobs import import_pre_payment_file
from prisme.models import PrePaymentFile, Transaction
from worker.models import Job


class ImportPrePaymentFile(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            username='user',
            email='test@example.com'
        )
        self.tax_year = TaxYear.objects.create(year=2020)
        for cpr in ('0708614866', '0103897769'):
            person = Person.objects.create(cpr=cpr)
            PersonTaxYear.objects.create(person=person,
                                         tax_year=self.tax_year)

        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data/PGF85_2021_897021_28-04-2021_080136.csv'), mode='rb') as test_data:
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
        self.assertEqual(first_person_transaction.amount, 18000)
        self.assertEqual(first_person_transaction.status, 'transferred')
        self.assertEqual(first_person_transactions.first().type, 'prepayment')

        second_person_transactions = new_transactions.filter(person_tax_year__person__cpr='0103897769')
        self.assertEqual(second_person_transactions.count(), 1)
        second_person_transaction = second_person_transactions.first()
        self.assertEqual(second_person_transaction.amount, 7000)
        self.assertEqual(second_person_transaction.status, 'transferred')
        self.assertEqual(second_person_transactions.first().type, 'prepayment')
