import json
import os

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from kas.models import TaxYear, PensionCompany, Person, PolicyTaxYear, PersonTaxYear, PolicyDocument
from kas.models import PreviousYearNegativePayout
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class DeductionTest(TestCase):

    def test_simple(self):
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

        policy_tax_year1.use_amount(2000, policy_tax_year2)



        print(PreviousYearNegativePayout.objects.first())

