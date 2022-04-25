from datetime import datetime
from unittest.mock import patch, MagicMock

import django_rq
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import override_settings, TransactionTestCase
from fakeredis import FakeStrictRedis
from rq import Queue

from eskat.jobs import generate_sample_data
from kas.eboks import EboksClient
from kas.jobs import dispatch_tax_year, generate_batch_and_transactions_for_year, merge_pension_companies, \
    import_mandtal
from kas.models import TaxYear, PersonTaxYear, Person, PolicyTaxYear, PensionCompany, TaxSlipGenerated, FinalSettlement
from prisme.models import Prisme10QBatch
from worker.models import Job
from project.dafo import DatafordelerClient

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


@override_settings(METRICS={'disabled': True})
@override_settings(FEATURE_FLAGS={'enable_dafo_override_of_address': True})
class BaseTransactionTestCase(TransactionTestCase):

    def setUp(self) -> None:
        self.tax_year = TaxYear.objects.create(year=2021)
        self.pension_company = PensionCompany.objects.create(name='test', res=2)
        self.person = Person.objects.create(
            cpr='0102031234',
            name='Test Testperson',
            municipality_code=956,
            municipality_name='Sermersooq',
            address_line_2='Testvej 42',
            address_line_4='1234  Testby'
        )

        self.user = get_user_model().objects.create(username='test2')


class MandtalImportJobsTest(BaseTransactionTestCase):

    @patch.object(DatafordelerClient, '_get', return_value={
        "0101570010": {"cprNummer": "0101570010", "fornavn": "Anders", "efternavn": "And",
                       "adresse": "Testadresse 32A, 3.", "postnummer": 3900, "bynavn": "Nuuk", "civilstand": "D"},
        "2512484916": {"cprNummer": "2512484916", "fornavn": "Andersine", "efternavn": "And",
                       "adresse": "Imaneq 32A, 3.", "postnummer": 3900, "bynavn": "Nuuk"}})
    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_mandtal_import_and_merge_with_dafo(self, django_rq, _get):
        Job.schedule_job(
            generate_sample_data,
            'GenerateSampleData',
            self.user,
        )

        # Indlæs fra e-skat data til KAS systemet, herunder fletning af adresser
        Job.schedule_job(import_mandtal,
                         job_type='ImportMandtalJob',
                         job_kwargs={"year": "2021"}, created_by=self.user)

        self.assertEqual(Person.objects.count(), 16)

        self.assertEqual(Person.objects.filter(updated_from_dafo=True).count(), 2)
        self.assertEqual(Person.objects.filter(updated_from_dafo=False).count(), 14)

        self.assertEqual(Person.objects.filter(status='Alive').count(), 1)  # Mocked af Andessine in Dafo
        self.assertEqual(Person.objects.filter(status='Dead').count(), 1)  # Mocked af Andes in Dafo
        self.assertEqual(Person.objects.filter(status='Undefined').count(),
                         14)  # 0102031234, the predefined person that is also 'Undefined'

        person = Person.objects.get(cpr='0101570010')
        self.assertEqual(person.name, 'Anders And')
        self.assertEqual(person.full_address, "Testadresse 32A, 3.,3900 Nuuk")
        self.assertEqual(person.updated_from_dafo, True)

        person = Person.objects.get(cpr='2512484916')
        self.assertEqual(person.name, 'Andersine And')
        self.assertEqual(person.updated_from_dafo, True)


class TaxslipGeneratedJobsTest(BaseTransactionTestCase):
    def setUp(self) -> None:
        super(TaxslipGeneratedJobsTest, self).setUp()
        report_file = ContentFile("test_report")
        for i in range(1, 8):
            if i == 3:
                person = Person.objects.create(cpr='111111111{}'.format(i), status='Dead')
            elif i == 4:
                person = Person.objects.create(cpr='111111111{}'.format(i), status='Invalid')
            else:
                person = Person.objects.create(cpr='111111111{}'.format(i))

            person_tax_year = PersonTaxYear.objects.create(tax_year=self.tax_year, person=person)
            person_tax_year.tax_slip = TaxSlipGenerated.objects.create(persontaxyear=person_tax_year)
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
        self.assertEqual(TaxSlipGenerated.objects.filter(status='send').count(), 5)  # 5 persons is not dead or invalid

    @patch.object(EboksClient, 'get_recipient_status')
    @patch.object(EboksClient, 'send_message')
    @patch.object(EboksClient, 'get_message_id')
    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    @override_settings(EBOKS=test_settings, METRICS={'disabled': True})
    def test_multi_child_jobs(self, django_rq, get_message_id_mock, send_message, get_recipient_mock):
        get_message_id_mock.side_effect = self.mock_message.keys()
        send_message.return_value = send_message_mock(self.mock_message)
        get_recipient_mock.return_value = get_recipient_status_mock(as_side_effect=True)
        parent_job = Job.schedule_job(dispatch_tax_year,
                                      job_type='dispatch_tax_year',
                                      job_kwargs=self.job_kwargs,
                                      created_by=self.user)
        self.assertEqual(Job.objects.filter(parent=parent_job).count(), 3)  # 4 jobs should have been started
        self.assertEqual(TaxSlipGenerated.objects.filter(status='send').count(), 5)


class GenerateBatchAndTransactionsForYearJobsTest(BaseTransactionTestCase):

    def setUp(self) -> None:
        super(GenerateBatchAndTransactionsForYearJobsTest, self).setUp()
        self.tax_year.year_part = 'ligning'
        self.tax_year.save()
        person_tax_year = PersonTaxYear.objects.create(
            person=self.person,
            tax_year=self.tax_year,
            number_of_days=300,
            fully_tax_liable=True
        )

        self.policytaxyear = PolicyTaxYear.objects.create(
            person_tax_year=person_tax_year,
            pension_company=self.pension_company,
            policy_number='123456',
            prefilled_amount=10,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
            foreign_paid_amount_actual=0,
            slutlignet=True
        )
        self.settlement = FinalSettlement.objects.create(person_tax_year=person_tax_year)
        self.user = get_user_model().objects.create(username='test')

        self.job_kwargs = {
            'year_pk': self.tax_year.pk,
            'title': 'test af final statement: {}'.format(str(self.tax_year.year))
        }

    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_zero_sum(self, django_rq):
        self.policytaxyear.prefilled_amount = 0
        self.policytaxyear.save()

        Job.schedule_job(
            generate_batch_and_transactions_for_year,
            job_type='generate_batch_and_transactions_for_year',
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
            generate_batch_and_transactions_for_year,
            job_type='generate_batch_and_transactions_for_year',
            job_kwargs=self.job_kwargs,
            created_by=self.user
        )

        qs = Prisme10QBatch.objects.filter(tax_year__pk=self.job_kwargs['year_pk'])
        self.assertEqual(qs.count(), 1)
        batch = qs.first()
        self.assertEqual(FinalSettlement.objects.count(), 1)
        self.assertEqual(FinalSettlement.objects.first().get_transaction_amount(), 1)
        self.assertEqual(batch.transaction_set.count(), 1)


class MergeCompanyJobsTest(BaseTransactionTestCase):
    def setUp(self) -> None:
        super(MergeCompanyJobsTest, self).setUp()
        self.user = get_user_model().objects.create(username='test')
        self.to_be_merged = [PensionCompany.objects.create(name='to_be_merged 1', res=3).pk,
                             PensionCompany.objects.create(name='to_be_merged 2', res=4).pk]
        self.person_tax_year = PersonTaxYear.objects.create(person=self.person, tax_year=self.tax_year)
        # one person one, policy for each company
        for i, company_id in enumerate(self.to_be_merged):
            PolicyTaxYear.objects.create(person_tax_year=self.person_tax_year,
                                         pension_company_id=company_id,
                                         policy_number=str(i))

    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_merge_same_person(self, django_rq):
        """
        Same person, two policies for two different companies.
        The end result should be one person, one company, two policies.
        """
        Job.schedule_job(merge_pension_companies,
                         job_type='MergeCompanies',
                         job_kwargs={'target': self.pension_company.pk,
                                     'to_be_merged': self.to_be_merged},
                         created_by=self.user)
        # All policies should now have been moved to the target company
        policies = PolicyTaxYear.objects.filter(pension_company=self.pension_company,
                                                person_tax_year=self.person_tax_year)
        self.assertEqual(policies.count(), 2)
