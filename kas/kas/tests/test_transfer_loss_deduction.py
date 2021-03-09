from builtins import Exception

from django.test import TestCase
from kas.models import TaxYear, PensionCompany, Person, PolicyTaxYear, PersonTaxYear


class DeductionTest(TestCase):

    def test_Using_up_loss(self):
        person = Person.objects.create(cpr='1234567890')
        pension_company = PensionCompany.objects.create(
            cvr=12345678,
            name='Foobar A/S',
            address='Foobarvej 42'
        )
        person_tax_year1 = PersonTaxYear.objects.create(
            person=person,
            tax_year=TaxYear.objects.create(year=2019)
        )
        person_tax_year2 = PersonTaxYear.objects.create(
            person=person,
            tax_year=TaxYear.objects.create(year=2020)
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

        usup = policy_tax_year1.use_amount(900, policy_tax_year2)
        assert usup == 900
        usup = policy_tax_year1.use_amount(900, policy_tax_year2)
        assert usup == 100
        try:
            policy_tax_year1.use_amount(900, policy_tax_year2)
        except Exception:
            pass
