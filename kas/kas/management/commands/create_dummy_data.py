from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from worker.job_registry import get_job_types, resolve_job_function
from worker.models import Job

from kas.models import Person, PensionCompany, TaxYear, PersonTaxYear
from kas.models import PolicyTaxYear, Transaction, PensionCompanySummaryFile
from kas.models import PolicyDocument, TaxSlipGenerated
from kas.reportgeneration.kas_final_statement import TaxFinalStatementPDF
from prisme.models import PrePaymentFile


class Command(BaseCommand):
    help = 'Populates database with some dummy data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete old data before importing dummy data',
        )

    def handle(self, *args, **options):
        job_data = get_job_types()['ResetToMockupOnly']
        job_function = resolve_job_function(job_data['function'])

        admin_user, _ = get_user_model().objects.get_or_create(
            username='admin'
        )

        Job.schedule_job(
            job_function,
            'ResetToMockupOnly',
            admin_user,
            job_kwargs={'skip_deletions': not options['delete']},
        )

        self.create_final_statement(admin_user)
        self.create_pensioncompanysummary(admin_user)
        self.create_policydocument(admin_user)
        self.create_taxslip()
        self.create_prepaymentfile(admin_user)

    def create_final_statement(self, user):
        person, _ = Person.objects.get_or_create(
            cpr='0102031234',
            name='Test Testperson',
            municipality_code=956,
            municipality_name='Sermersooq',
            address_line_2='Testvej 42',
            address_line_4='1234  Testby'
        )

        tax_year, _ = TaxYear.objects.get_or_create(year=2020)
        person_tax_year, _ = PersonTaxYear.objects.get_or_create(
            person=person,
            tax_year=tax_year,
            number_of_days=300,
        )

        pension_company1, _ = PensionCompany.objects.get_or_create(res=12345671, name='P+, Pensionskassen for Akademikere')
        pension_company2, _ = PensionCompany.objects.get_or_create(res=12345672, name='PFA', agreement_present=True)
        pension_company3, _ = PensionCompany.objects.get_or_create(res=12345673, name='High Risk Invest & Pension')

        Transaction.objects.create(
            amount=200,
            person_tax_year=person_tax_year,
            source_object=person_tax_year
        )

        older_policy_1 = PolicyTaxYear.objects.create(
            person_tax_year=PersonTaxYear.objects.create(
                person=person,
                tax_year=TaxYear.objects.create(year=2018),
                number_of_days=365,
                fully_tax_liable=False,
            ),
            pension_company=pension_company1,
            policy_number='123456',
            prefilled_amount=-500,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED
        )
        older_policy_2 = PolicyTaxYear.objects.create(
            person_tax_year=PersonTaxYear.objects.create(
                person=person,
                tax_year=TaxYear.objects.create(year=2019),
                number_of_days=365,
            ),
            pension_company=pension_company1,
            policy_number='123456',
            prefilled_amount=-500,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
        )
        PolicyTaxYear.objects.create(
            person_tax_year=person_tax_year,
            pension_company=pension_company1,
            policy_number='123456',
            prefilled_amount=10000,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
            foreign_paid_amount_actual=300,
        )
        PolicyTaxYear.objects.create(
            person_tax_year=person_tax_year,
            pension_company=pension_company2,
            policy_number='314159265',
            prefilled_amount=3000,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
            foreign_paid_amount_actual=0,
        )
        PolicyTaxYear.objects.create(
            person_tax_year=person_tax_year,
            pension_company=pension_company3,
            policy_number='1337',
            prefilled_amount=-2000,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
            foreign_paid_amount_actual=0,
        )

        older_policy_1.recalculate()
        older_policy_2.recalculate()

        TaxFinalStatementPDF.generate_pdf(person_tax_year=person_tax_year)

    def create_pensioncompanysummary(self, user):
        pension_company, _ = PensionCompany.objects.get_or_create(res=12345671, name='P+, Pensionskassen for Akademikere')
        tax_year, _ = TaxYear.objects.get_or_create(year=2020)
        PensionCompanySummaryFile.create(pension_company, tax_year, user)

    def create_policydocument(self, user):
        person, _ = Person.objects.get_or_create(
            cpr='0102031234',
            name='Test Testperson',
            municipality_code=956,
            municipality_name='Sermersooq',
            address_line_2='Testvej 42',
            address_line_4='1234  Testby'
        )

        tax_year, _ = TaxYear.objects.get_or_create(year=2020)
        person_tax_year, _ = PersonTaxYear.objects.get_or_create(
            person=person,
            tax_year=tax_year,
        )
        item = PolicyDocument.objects.create(
            person_tax_year=person_tax_year,
            description='TestDokument',
            name='TestFil',
            uploaded_by=user
        )
        item.file.save("testfil", content=ContentFile("hephey"))

    def create_taxslip(self):
        person, _ = Person.objects.get_or_create(
            cpr='0102031234',
            name='Test Testperson',
            municipality_code=956,
            municipality_name='Sermersooq',
            address_line_2='Testvej 42',
            address_line_4='1234  Testby'
        )

        tax_year, _ = TaxYear.objects.get_or_create(year=2020)
        person_tax_year, _ = PersonTaxYear.objects.get_or_create(
            person=person,
            tax_year=tax_year,
        )
        item = TaxSlipGenerated.objects.create()
        person_tax_year.tax_slip = item
        item.file.save("testfil", content=ContentFile("hephey"))
        person_tax_year.save()

    def create_prepaymentfile(self, user):
        item = PrePaymentFile.objects.create(uploaded_by=user)
        item.file.save("testfil", content=ContentFile("hephey"))
