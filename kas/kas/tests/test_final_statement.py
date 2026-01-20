from django.test import TestCase
from prisme.models import Transaction

from kas.reportgeneration.kas_final_statement import TaxFinalStatementPDF
from kas.tests.test_mixin import create_admin_user

from kas.models import (  # isort: skip
    FinalSettlement,
    PensionCompany,
    Person,
    PersonTaxYear,
    PolicyTaxYear,
    TaxYear,
)


class DeductionTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_admin_user()

    def test_generate_final_taxslip(self):
        # Set up two older policies with losses, and one new policy that will deduct those losses
        person = Person.objects.create(
            cpr="0102031234",
            name="Test Testperson",
            municipality_code=956,
            municipality_name="Sermersooq",
            address_line_2="Testvej 42",
            address_line_4="1234  Testby",
        )

        tax_year = TaxYear.objects.create(year=2020)
        person_tax_year = PersonTaxYear.objects.create(
            person=person,
            tax_year=tax_year,
            number_of_days=300,
        )

        pension_company1 = PensionCompany.objects.create(
            res=12345671, name="P+, Pensionskassen for Akademikere"
        )
        pension_company2 = PensionCompany.objects.create(
            res=12345672, name="PFA", agreement_present=True
        )
        pension_company3 = PensionCompany.objects.create(
            res=12345673, name="High Risk Invest & Pension"
        )

        Transaction.objects.create(
            amount=200, person_tax_year=person_tax_year, source_object=person_tax_year
        )

        older_policy_1 = PolicyTaxYear.objects.create(
            person_tax_year=PersonTaxYear.objects.create(
                person=person,
                tax_year=TaxYear.objects.create(year=2018),
                number_of_days=365,
                fully_tax_liable=False,
            ),
            pension_company=pension_company1,
            policy_number="123456",
            prefilled_amount=-500,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
        )
        older_policy_2 = PolicyTaxYear.objects.create(
            person_tax_year=PersonTaxYear.objects.create(
                person=person,
                tax_year=TaxYear.objects.create(year=2019),
                number_of_days=365,
            ),
            pension_company=pension_company1,
            policy_number="123456",
            prefilled_amount=-500,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
        )
        PolicyTaxYear.objects.create(
            person_tax_year=person_tax_year,
            pension_company=pension_company1,
            policy_number="123456",
            prefilled_amount=10000,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
            foreign_paid_amount_actual=300,
        )
        PolicyTaxYear.objects.create(
            person_tax_year=person_tax_year,
            pension_company=pension_company2,
            policy_number="314159265",
            prefilled_amount=3000,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
            foreign_paid_amount_actual=0,
        )
        PolicyTaxYear.objects.create(
            person_tax_year=person_tax_year,
            pension_company=pension_company3,
            policy_number="1337",
            prefilled_amount=-2000,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
            foreign_paid_amount_actual=0,
        )

        older_policy_1.recalculate()
        older_policy_2.recalculate()

        final_settlement = TaxFinalStatementPDF.generate_pdf(
            person_tax_year=person_tax_year
        )

        self.assertEqual(1, FinalSettlement.objects.count())

        self.assertEqual("created", final_settlement.status)
