import pandas as pd
import io
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
import uuid

from kas.models import (
    TaxYear,
    PensionCompany,
    Person,
    PolicyTaxYear,
    PersonTaxYear,
    FinalSettlement,
)
from eskat.models import ImportedKasBeregningerX
from kas.views import PersonTaxYearEskatDiffListView


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        self.username = "admin"
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = "admin"
        self.user.set_password(self.password)
        self.user.save()
        self.administrator_group = Group.objects.get(name="administrator")
        self.user.groups.set([self.administrator_group])
        self.client.login(username=self.username, password=self.password)

        self.year = 2018
        self.person = Person.objects.create(
            cpr="1234567890",
            name="TestPerson",
            full_address="foo street",
            municipality_name="bar municipality",
        )
        self.pension_company = PensionCompany.objects.create()
        self.tax_year = TaxYear.objects.create(year=self.year)
        self.person_tax_year = PersonTaxYear.objects.create(
            tax_year=self.tax_year,
            person=self.person,
            number_of_days=self.tax_year.days_in_year,
        )
        self.policy_tax_year = PolicyTaxYear.objects.create(
            person_tax_year=self.person_tax_year,
            pension_company=self.pension_company,
            prefilled_amount=35,
            policy_number="1234",
        )

        self.final_settlement = FinalSettlement.objects.create(
            person_tax_year=self.person_tax_year, lock=self.tax_year.get_current_lock
        )

        self.imported_kas_beregninger = ImportedKasBeregningerX.objects.create(
            person_tax_year=self.person_tax_year,
            skatteaar=self.year,
            pension_crt_calc_guid=uuid.uuid4(),
        )


class LecagcyYearsTestCase(BaseTestCase):
    def get_persons_with_difference_from_context(self):
        r = self.client.get(
            reverse("kas:person_search_eskat_diff") + "?year=%d" % self.year
        )
        return r.context["personstaxyears"]

    def test_legacy_years_diff_list(self):
        """
        Test the 2018/2019 difference between kas and eskat difference list
        """

        # Verify that the list shows no users
        persons = self.get_persons_with_difference_from_context()
        self.assertEqual(len(persons), 0)

        # Change pseudo amount on final settlement
        self.final_settlement.pseudo = True
        self.final_settlement.pseudo_amount = 100
        self.final_settlement.save()

        # Verify that we can now see the user in the list
        persons = self.get_persons_with_difference_from_context()
        self.assertEqual(len(persons), 1)

        # Verify that Efterbehandling = False in the list
        self.assertEqual(persons[0].efterbehandling, False)

        # Set the policy to Efterbehandling = True
        response = self.client.post(
            reverse(
                "kas:update-efterbehandling",
                kwargs={
                    "pk": self.policy_tax_year.pk,
                },
            ),
            data={"efterbehandling": True},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        # Verify that Efterbehandling = True in the list
        persons = self.get_persons_with_difference_from_context()
        self.assertEqual(persons[0].efterbehandling, True)

        # Test if the excel download button works
        response = self.client.get(
            reverse("kas:person_search_eskat_diff")
            + "?year=%d&format=excel" % self.year,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEquals(
            response.get("Content-Disposition"), "attachment; filename=eskat_diff.xls"
        )

        # Read the excel file
        with io.BytesIO(response.content) as fh:
            df = pd.io.excel.read_excel(fh)

        # Check that all the columns are there
        expected_columns = PersonTaxYearEskatDiffListView.excel_headers
        for col in expected_columns:
            self.assertIn(col, df.columns)

        # Check that the data looks as expected
        self.assertEquals(str(df.loc[0, "Personnummer"]), self.person.cpr)
        self.assertEquals(df.loc[0, "Navn"], self.person.name)
        self.assertEquals(df.loc[0, "Adresse"], self.person.full_address)
        self.assertEquals(df.loc[0, "Kommune"], self.person.municipality_name)
        self.assertEquals(df.loc[0, "Antal policer"], 1)
        self.assertEquals(
            df.loc[0, "Beløb i E-skat"],
            self.imported_kas_beregninger.capital_return_tax,
        )
        self.assertEquals(df.loc[0, "Beløb i KAS"], self.final_settlement.pseudo_amount)
        self.assertEquals(
            df.loc[0, "Kræver efterbehandling"], self.person_tax_year.efterbehandling
        )
