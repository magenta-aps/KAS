from datetime import datetime
from unittest.mock import patch, MagicMock

import django_rq
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import override_settings, TransactionTestCase
from fakeredis import FakeStrictRedis
from rq import Queue

from kas.eboks import EboksClient
from kas.jobs import dispatch_tax_year, generate_final_settlements_for_year
from kas.models import TaxYear, PersonTaxYear, Person, PolicyTaxYear, PensionCompany, TaxSlipGenerated, FinalSettlement
from worker.models import Job
from prisme.models import Prisme10QBatch

test_settings = dict(settings.EBOKS)
test_settings['dispatch_bulk_size'] = 2


def send_message_mock(message_and_status):
    responses = []
    for message_id, status in message_and_status.items():
        response = {"message_id": message_id,
                    'recipients': [{
                        'nr': "",
                        'recipient_type': 'cpr',
                        'nationality': 'Denmark',
                        'status': '',
                        'reject_reason': '',
                        'post_processing_status': status}]}
        responses.append(response)

    mock = MagicMock()
    mock.json = MagicMock(side_effect=responses)
    mock.status_code = 200
    return mock


def get_recipient_status_mock(as_side_effect=False):
    response = [
        {"message_id": '2505811057',
         "proxy_response_code": "200",
         "proxy_error": "",
         "modified_at": datetime.utcnow().isoformat(),
         "recipients": [{"nr": "",
                         "recipient_type": "cpr",
                         "nationality": "Denmark",
                         "status": "exempt",
                         "reject_reason": "",
                         "post_processing_status": "address resolved"}]},
        {"message_id": '2505636811',
         "proxy_response_code": "200",
         "proxy_error": "",
         "modified_at": datetime.utcnow().isoformat(),
         "recipients": [{
             "nr": "",
             "recipient_type": "cpr",
             "nationality": "Denmark",
             "status": "exempt",
             "reject_reason": "",
             "post_processing_status": "address resolved"}]},
        {"message_id": '8111245036',
         "proxy_response_code": "200",
         "proxy_error": "",
         "modified_at": datetime.utcnow().isoformat(),
         "recipients": [{
             "nr": "",
             "recipient_type": "cpr",
             "nationality": "Denmark",
             "status": "exempt",
             "reject_reason": "",
             "post_processing_status": "address resolved"}]}]
    mock = MagicMock()
    if as_side_effect:
        mock.json = MagicMock(side_effect=[response, response])
    else:
        mock.json = MagicMock(return_value=response)
    mock.status_code = 200
    return mock


class TaxslipGeneratedJobsTest(TransactionTestCase):
    def setUp(self) -> None:
        self.tax_year = TaxYear.objects.create(year=2020)

        self.pension_company = PensionCompany.objects.create(name='test', res=2)
        report_file = ContentFile("test_report")
        for i in range(1, 8):
            person = Person.objects.create(cpr='111111111{}'.format(i))
            person_tax_year = PersonTaxYear.objects.create(tax_year=self.tax_year, person=person)
            person_tax_year.tax_slip = TaxSlipGenerated.objects.create()
            person_tax_year.tax_slip.file.save('test', report_file)
            person_tax_year.save()

            PolicyTaxYear.objects.create(person_tax_year=person_tax_year,
                                         pension_company=self.pension_company,
                                         policy_number='test')

        self.user = get_user_model().objects.create(username='test')

        self.job_kwargs = {'year_pk': self.tax_year.pk,
                           'title': 'test af eboks: {}'.format(str(self.tax_year.year))}

        self.mock_message = {'0112947728': '',
                             '1256874212': '',
                             '1256842143': '',
                             '125742u568': '',
                             '2505811057': 'pending',
                             '2505636811': 'pending',
                             '8111245036': 'pending'}

    @patch.object(EboksClient, 'get_recipient_status')
    @patch.object(EboksClient, 'send_message')
    @patch.object(EboksClient, 'get_message_id')
    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_successful(self, django_rq, get_message_id_mock, send_message, get_recipient_mock):
        get_message_id_mock.side_effect = self.mock_message.keys()
        send_message.return_value = send_message_mock(self.mock_message)
        get_recipient_mock.return_value = get_recipient_status_mock()

        parent_job = Job.schedule_job(dispatch_tax_year,
                                      job_type='dispatch_tax_year',
                                      job_kwargs=self.job_kwargs,
                                      created_by=self.user)

        self.assertEqual(Job.objects.filter(parent=parent_job).count(), 1)
        # all slips where marked as send
        self.assertEqual(TaxSlipGenerated.objects.filter(status='send').count(), 7)

    @patch.object(EboksClient, 'get_recipient_status')
    @patch.object(EboksClient, 'send_message')
    @patch.object(EboksClient, 'get_message_id')
    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    @override_settings(EBOKS=test_settings)
    def test_multi_child_jobs(self, django_rq, get_message_id_mock, send_message, get_recipient_mock):
        get_message_id_mock.side_effect = self.mock_message.keys()
        send_message.return_value = send_message_mock(self.mock_message)
        get_recipient_mock.return_value = get_recipient_status_mock(as_side_effect=True)
        parent_job = Job.schedule_job(dispatch_tax_year,
                                      job_type='dispatch_tax_year',
                                      job_kwargs=self.job_kwargs,
                                      created_by=self.user)
        self.assertEqual(Job.objects.filter(parent=parent_job).count(), 4)  # 4 jobs should have been started
        self.assertEqual(TaxSlipGenerated.objects.filter(status='send').count(), 7)


class FinalStatementJobsTest(TransactionTestCase):

    def setUp(self) -> None:
        tax_year = TaxYear.objects.create(year=2020)

        person = Person.objects.create(
            cpr='0102031234',
            name='Test Testperson',
            municipality_code=956,
            municipality_name='Sermersooq',
            address_line_2='Testvej 42',
            address_line_4='1234  Testby'
        )

        person_tax_year = PersonTaxYear.objects.create(
            person=person,
            tax_year=tax_year,
            number_of_days=300,
            fully_tax_liable=True
        )

        pension_company = PensionCompany.objects.create(
            res=12345673,
            name='High Risk Invest & Pension'
        )

        self.policytaxyear = PolicyTaxYear.objects.create(
            person_tax_year=person_tax_year,
            pension_company=pension_company,
            policy_number='123456',
            prefilled_amount=10,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
            foreign_paid_amount_actual=0,
            slutlignet=True
        )

        self.user = get_user_model().objects.create(username='test')

        self.job_kwargs = {
            'year_pk': tax_year.pk,
            'title': 'test af final statement: {}'.format(str(tax_year.year))
        }

    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_zero_sum(self, django_rq):

        self.policytaxyear.prefilled_amount = 0
        self.policytaxyear.save()

        Job.schedule_job(
            generate_final_settlements_for_year,
            job_type='generate_final_settlements_for_year',
            job_kwargs=self.job_kwargs,
            created_by=self.user
        )

        qs = Prisme10QBatch.objects.filter(tax_year__pk=self.job_kwargs['year_pk'])
        self.assertEqual(qs.count(), 1)
        batch = qs.first()
        self.assertEqual(FinalSettlement.objects.count(), 1)
        self.assertEqual(FinalSettlement.objects.first().get_transaction_amount(), 0)
        self.assertEqual(batch.transaction_set.count(), 0)

    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_nonzero_sum(self, django_rq):

        self.policytaxyear.prefilled_amount = 10
        self.policytaxyear.save()

        Job.schedule_job(
            generate_final_settlements_for_year,
            job_type='generate_final_settlements_for_year',
            job_kwargs=self.job_kwargs,
            created_by=self.user
        )

        qs = Prisme10QBatch.objects.filter(tax_year__pk=self.job_kwargs['year_pk'])
        self.assertEqual(qs.count(), 1)
        batch = qs.first()
        self.assertEqual(FinalSettlement.objects.count(), 1)
        self.assertEqual(FinalSettlement.objects.first().get_transaction_amount(), 1)
        self.assertEqual(batch.transaction_set.count(), 1)
