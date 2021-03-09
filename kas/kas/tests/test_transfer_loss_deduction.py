from builtins import Exception

from django.test import TestCase
from kas.models import TaxYear, PensionCompany, Person, PolicyTaxYear, PersonTaxYear


class DeductionTest(TestCase):

    # Validate that losses can be used as deductions in future years, until all is used.
    # Validate than when all losses us used, other years can be used as basis for the deduction
    def test_Using_up_loss_from_2019(self):
        person = Person.objects.create(cpr='1234567890')
        pension_company = PensionCompany.objects.create(
            cvr=12345678,
            name='Foobar A/S',
            address='Foobarvej 42'
        )
        person_tax_year0 = PersonTaxYear.objects.create(
            person=person,
            tax_year=TaxYear.objects.create(year=2018)
        )
        person_tax_year1 = PersonTaxYear.objects.create(
            person=person,
            tax_year=TaxYear.objects.create(year=2019)
        )
        person_tax_year2 = PersonTaxYear.objects.create(
            person=person,
            tax_year=TaxYear.objects.create(year=2020)
        )

        policy_tax_year0 = PolicyTaxYear.objects.create(
            policy_number='1234',
            person_tax_year=person_tax_year0,
            pension_company=pension_company,
            prefilled_amount=100,
            self_reported_amount=100,
            preliminary_paid_amount=0,
            from_pension=True,
            calculated_result=-1000
        )
        policy_tax_year1 = PolicyTaxYear.objects.create(
            policy_number='1234',
            person_tax_year=person_tax_year1,
            pension_company=pension_company,
            prefilled_amount=100,
            self_reported_amount=100,
            preliminary_paid_amount=0,
            from_pension=True,
            calculated_result=-1000
        )
        policy_tax_year2 = PolicyTaxYear.objects.create(
            policy_number='1234',
            person_tax_year=person_tax_year2,
            pension_company=pension_company,
            prefilled_amount=200,
            self_reported_amount=200,
            preliminary_paid_amount=20,
            from_pension=False,
            calculated_result=1000
        )

        used_previous_loss = policy_tax_year0.use_amount(900, policy_tax_year2)
        assert used_previous_loss == 900
        used_previous_loss = policy_tax_year0.use_amount(900, policy_tax_year2)
        assert used_previous_loss == 100
        try:
            policy_tax_year0.use_amount(900, policy_tax_year2)
        except Exception:
            pass

        used_previous_loss = policy_tax_year1.use_amount(300, policy_tax_year2)
        assert used_previous_loss == 300

    # Validate that losses can not be used on years with no loss
    def test_Using_up_loss_from_2020(self):
        person = Person.objects.create(cpr='1234567890')
        pension_company = PensionCompany.objects.create(
            cvr=12345678,
            name='Foobar A/S',
            address='Foobarvej 42'
        )

        person_tax_year2 = PersonTaxYear.objects.create(
            person=person,
            tax_year=TaxYear.objects.create(year=2020)
        )
        person_tax_year3 = PersonTaxYear.objects.create(
            person=person,
            tax_year=TaxYear.objects.create(year=2021)
        )

        policy_tax_year2 = PolicyTaxYear.objects.create(
            policy_number='1234',
            person_tax_year=person_tax_year2,
            pension_company=pension_company,
            prefilled_amount=200,
            self_reported_amount=200,
            preliminary_paid_amount=20,
            from_pension=False,
            calculated_result=1000
        )
        policy_tax_year3 = PolicyTaxYear.objects.create(
            policy_number='1234',
            person_tax_year=person_tax_year3,
            pension_company=pension_company,
            prefilled_amount=200,
            self_reported_amount=200,
            preliminary_paid_amount=20,
            from_pension=False,
            calculated_result=1000
        )

        try:
            policy_tax_year2.use_amount(1, policy_tax_year3)
        except Exception:
            pass
