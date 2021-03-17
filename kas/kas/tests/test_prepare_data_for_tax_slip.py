import os
from builtins import len

from django.test import TestCase
from kas.models import TaxYear, PensionCompany, Person, PolicyTaxYear, PersonTaxYear
from kas.reportgeneration.kas_report import TaxSlipHandling
import tempfile


class DeductionTest(TestCase):

    # Validate that losses can be used as deductions in future years, until all is used.
    # Validate than when all losses us used, other years can be used as basis for the deduction
    def test_Using_up_loss_from_2019(self):
        person1 = Person.objects.create(cpr='1234567890', municipality_code=956, municipality_name='Sermersooq',
                                        address_line_2='Mut aqqut 13', address_line_4='3900 Nuuk', name='Andersine And')
        person2 = Person.objects.create(cpr='1234567891', municipality_code=956, municipality_name='Sermersooq',
                                        address_line_2='Mut aqqut 15', address_line_4='3900 Nuuk', name='Anders And')
        person3 = Person.objects.create(cpr='1234567897', municipality_code=956, municipality_name='Sermersooq',
                                        address_line_2='Mut aqqut 17', address_line_4='3900 Nuuk',
                                        name='Joakim Von And')
        pension_company1 = PensionCompany.objects.create(
            name='Pensionsselskab uden aftale A/S',
            address='Foobarvej 42',
            agreement_present=False,
        )
        pension_company2 = PensionCompany.objects.create(
            name='Pensionsselskab med aftale A/S',
            address='Foobarvej 42',
            agreement_present=True,
        )
        tax_year_2019 = TaxYear.objects.create(year=2019)
        tax_year_2020 = TaxYear.objects.create(year=2020)

        person_tax_year_p1_2019 = PersonTaxYear.objects.create(
            person=person1,
            tax_year=tax_year_2019,
            fully_tax_liable=True
        )

        person_tax_year_p1_2020 = PersonTaxYear.objects.create(
            person=person1,
            tax_year=tax_year_2020,
            fully_tax_liable=True
        )

        PolicyTaxYear.objects.create(
            policy_number='1234',
            person_tax_year=person_tax_year_p1_2019,
            pension_company=pension_company2,
            prefilled_amount=100,
            self_reported_amount=100,
            preliminary_paid_amount=0,
        )

        PolicyTaxYear.objects.create(
            policy_number='1234',
            person_tax_year=person_tax_year_p1_2020,
            pension_company=pension_company1,
            prefilled_amount=200,
            self_reported_amount=100,
            preliminary_paid_amount=7,
        )

        PolicyTaxYear.objects.create(
            policy_number='1235',
            person_tax_year=person_tax_year_p1_2020,
            pension_company=pension_company2,
            prefilled_amount=300,
            self_reported_amount=112,
            preliminary_paid_amount=8,
        )

        person_tax_year_p2_2020 = PersonTaxYear.objects.create(
            person=person2,
            tax_year=tax_year_2020,
            number_of_days=150,
            fully_tax_liable=False
        )

        PolicyTaxYear.objects.create(
            policy_number='1234',
            person_tax_year=person_tax_year_p2_2020,
            pension_company=pension_company1,
            prefilled_amount=402.46,
            self_reported_amount=142,
            preliminary_paid_amount=9,
        )

        person_tax_year_p3_2020 = PersonTaxYear.objects.create(
            person=person3,
            tax_year=tax_year_2020,
            fully_tax_liable=True
        )

        PolicyTaxYear.objects.create(
            policy_number='12341230',
            person_tax_year=person_tax_year_p3_2020,
            pension_company=pension_company1,
            prefilled_amount=400,
            self_reported_amount=142,
            preliminary_paid_amount=9,
        )
        PolicyTaxYear.objects.create(
            policy_number='12341231',
            person_tax_year=person_tax_year_p3_2020,
            pension_company=pension_company1,
            prefilled_amount=400,
            self_reported_amount=142,
            preliminary_paid_amount=9,
        )
        PolicyTaxYear.objects.create(
            policy_number='12341232',
            person_tax_year=person_tax_year_p3_2020,
            pension_company=pension_company1,
            prefilled_amount=400,
            self_reported_amount=142,
            preliminary_paid_amount=9,
        )
        PolicyTaxYear.objects.create(
            policy_number='12341233',
            person_tax_year=person_tax_year_p3_2020,
            pension_company=pension_company1,
            prefilled_amount=400,
            self_reported_amount=142,
            preliminary_paid_amount=9,
        )
        PolicyTaxYear.objects.create(
            policy_number='12341234',
            person_tax_year=person_tax_year_p3_2020,
            pension_company=pension_company1,
            prefilled_amount=400,
            self_reported_amount=142,
            preliminary_paid_amount=9,
        )
        PolicyTaxYear.objects.create(
            policy_number='12341235',
            person_tax_year=person_tax_year_p3_2020,
            pension_company=pension_company1,
            prefilled_amount=400,
            self_reported_amount=142,
            preliminary_paid_amount=9,
        )
        PolicyTaxYear.objects.create(
            policy_number='12341236',
            person_tax_year=person_tax_year_p3_2020,
            pension_company=pension_company1,
            prefilled_amount=400,
            self_reported_amount=142,
            preliminary_paid_amount=9,
        )
        PolicyTaxYear.objects.create(
            policy_number='12341237',
            person_tax_year=person_tax_year_p3_2020,
            pension_company=pension_company1,
            prefilled_amount=400,
            self_reported_amount=142,
            preliminary_paid_amount=9,
        )
        PolicyTaxYear.objects.create(
            policy_number='12341238',
            person_tax_year=person_tax_year_p3_2020,
            pension_company=pension_company1,
            prefilled_amount=400,
            self_reported_amount=142,
            preliminary_paid_amount=9,
        )
        PolicyTaxYear.objects.create(
            policy_number='12341239',
            person_tax_year=person_tax_year_p3_2020,
            pension_company=pension_company1,
            prefilled_amount=400,
            self_reported_amount=142,
            preliminary_paid_amount=9,
        )

        pdf_documen = TaxSlipHandling()
        pdf_documen.perform_complete_write_of_one_tax_year(destination_path=self.test_dir, tax_year=2020)

        filelist1 = os.listdir(self.test_dir)

        self.assertEqual(2, len(filelist1))
        self.assertEqual(True, 'Y_2020_1234567890.pdf' in filelist1)
        self.assertEqual(True, 'Y_2020_1234567891.pdf' in filelist1)

        self.test_dir = tempfile.mkdtemp()+'/'
        pdf_documen.perform_complete_write_of_one_tax_year(destination_path=self.test_dir, tax_year=2019)
        filelist2 = os.listdir(self.test_dir)
        self.assertEqual(1, len(filelist2))
        self.assertEqual(True, 'Y_2019_1234567890.pdf' in filelist2)

        person_tax_year_list = PersonTaxYear.objects.all()

        for person_tax_year in person_tax_year_list:
            self.assertEqual('created', person_tax_year.tax_slip.status)
