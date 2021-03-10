
from django.test import TestCase
from kas.models import TaxYear, PensionCompany, Person, PolicyTaxYear, PersonTaxYear


class DeductionTest(TestCase):

    # Validate that losses can be used as deductions in future years, until all is used.
    # Validate than when all losses us used, other years can be used as basis for the deduction
    def test_Using_up_loss_from_2019(self):
        person1 = Person.objects.create(cpr='1234567890', municipality_code=956, municipality_name='Sermersooq')
        person2 = Person.objects.create(cpr='1234567891', municipality_code=956, municipality_name='Sermersooq')
        pension_company = PensionCompany.objects.create(
            cvr=12345678,
            name='Foobar A/S',
            address='Foobarvej 42'
        )
        tax_year_2020 = TaxYear.objects.create(year=2020)

        person_tax_year_p1_2020 = PersonTaxYear.objects.create(
            person=person1,
            tax_year=tax_year_2020
        )

        PolicyTaxYear.objects.create(
            policy_number='1234',
            person_tax_year=person_tax_year_p1_2020,
            pension_company=pension_company,
            prefilled_amount=100,
            self_reported_amount=100,
            preliminary_paid_amount=0,
            from_pension=True,
            year_adjusted_amount=-1000
        )

        PolicyTaxYear.objects.create(
            policy_number='1235',
            person_tax_year=person_tax_year_p1_2020,
            pension_company=pension_company,
            prefilled_amount=100,
            self_reported_amount=112,
            preliminary_paid_amount=0,
            from_pension=True,
            year_adjusted_amount=-1000
        )

        person_tax_year_p2_2020 = PersonTaxYear.objects.create(
            person=person2,
            tax_year=tax_year_2020
        )

        PolicyTaxYear.objects.create(
            policy_number='1234',
            person_tax_year=person_tax_year_p2_2020,
            pension_company=pension_company,
            prefilled_amount=100,
            self_reported_amount=142,
            preliminary_paid_amount=0,
            from_pension=True,
            year_adjusted_amount=-1000
        )

        stuff = PersonTaxYear.objects.filter(
            tax_year__year=2020
        )

        for s in stuff:
            tax_year = s.tax_year.year
            tax_return_date_limit = f'1. maj {(s.tax_year.year+1)}'
            request_pay = f'1. september {(s.tax_year.year+1)}'
            pay_date = f'20. september {(s.tax_year.year+1)}'
            person_number = s.person.cpr
            reciever_name = s.person.name
            reciever_address = s.person.full_address
            reciever_postnumber = None
            sender_name = 'Skattestyrelsen'
            sender_address = 'Postboks 1605'
            sender_postnumber = '3900 Nuuk'
            nemid_kode = None
            policys = None

            print(tax_year)
            print(tax_return_date_limit)
            print(request_pay)
            print(pay_date)
            print(person_number)
            print(reciever_name)
            print(reciever_address)
            print(reciever_postnumber)
            print(sender_name)
            print(sender_address)
            print(sender_postnumber)
            print(nemid_kode)
            print(policys)

            stuff2 = PolicyTaxYear.objects.filter(
                person_tax_year=s

            )
            print(stuff2)
            print('-------------------------------')
