import os
from builtins import len

from django.test import TestCase
from kas.models import TaxYear, PensionCompany, Person, PolicyTaxYear, PersonTaxYear
from kas.reportgeneration.kas_report import TaxPDF
import tempfile


class DeductionTest(TestCase):

    # Validate that losses can be used as deductions in future years, until all is used.
    # Validate than when all losses us used, other years can be used as basis for the deduction
    def test_Using_up_loss_from_2019(self):
        person1 = Person.objects.create(cpr='1234567890', municipality_code=956, municipality_name='Sermersooq', address_line_2='Mut aqqut 13', address_line_4='3900 Nuuk', name='Andersine And')
        person2 = Person.objects.create(cpr='1234567891', municipality_code=956, municipality_name='Sermersooq', address_line_2='Mut aqqut 15', address_line_4='3900 Nuuk', name='Anders And')
        pension_company = PensionCompany.objects.create(
            cvr=12345678,
            name='Foobar A/S',
            address='Foobarvej 42'
        )
        tax_year_2019 = TaxYear.objects.create(year=2019)
        tax_year_2020 = TaxYear.objects.create(year=2020)

        person_tax_year_p1_2019 = PersonTaxYear.objects.create(
            person=person1,
            tax_year=tax_year_2019
        )

        person_tax_year_p1_2020 = PersonTaxYear.objects.create(
            person=person1,
            tax_year=tax_year_2020
        )

        PolicyTaxYear.objects.create(
            policy_number='1234',
            person_tax_year=person_tax_year_p1_2019,
            pension_company=pension_company,
            prefilled_amount=100,
            self_reported_amount=100,
            preliminary_paid_amount=0,
            from_pension=True,
            year_adjusted_amount=-1000
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

        self.test_dir = tempfile.mkdtemp()+'/'

        pdf_documen = TaxPDF()
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
