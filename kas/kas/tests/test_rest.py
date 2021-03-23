import json
import os

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from kas.models import TaxYear, PensionCompany, Person, PolicyTaxYear, PersonTaxYear, PolicyDocument
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class RestTest(TestCase):
    client_class = APIClient
    maxDiff = None

    testresources_folder = 'kas/tests/resources'

    invalid_string_values = [-4, 0, [], None]
    invalid_submit_body = invalid_string_values + ['', 'foobar', None, 17]
    invalid_year_values = invalid_string_values + ['', 1900]
    invalid_cpr_values = invalid_string_values + ['', 'hephey', '123456-7890', '123456789', '12345678901', '-1234567890']
    invalid_res_values = [-4, 0, [], 'hephey']
    invalid_fk_values = invalid_string_values + ['', 'hephey']
    invalid_policy_number_values = ['', [], {}, 'x'*41]
    invalid_amount_values = ['', [], {}, 'hephey']
    invalid_positive_amount_values = ['', [], {}, 'hephey', -123]
    invalid_filedata_values = ['', -4, 0, []]
    invalid_boolean_values = ['', -4, [], {}, 'hephey', 43]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='tester',
            email='test@example.com',
            password='we_are_testing'
        )
        cls.token = Token.objects.create(user=cls.user)
        cls.token.save()

    @staticmethod
    def strip_id(item):
        if type(item) == list:
            return [RestTest.strip_id(i) for i in item]
        if type(item) == dict and 'id' in item:
            del item['id']
        return item

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_nonauthenticated(self):
        if hasattr(self, 'url'):
            self.client.credentials()
            for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                response = self.client.generic(method, self.url)
                self.assertEquals(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_wrongauthenticated(self):
        if hasattr(self, 'url'):
            self.client.credentials(HTTP_AUTHORIZATION="Token some-invalid-token")
            for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                response = self.client.generic(method, self.url)
                self.assertEquals(status.HTTP_401_UNAUTHORIZED, response.status_code)


class TaxYearTest(RestTest):
    url = '/rest/tax_year/'

    def test_get_all(self):
        TaxYear.objects.create(year=2020)
        TaxYear.objects.create(year=2021)
        self.authenticate()
        response = self.client.get(self.url)
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(
            [{'year': year.year, 'id': year.id, 'days_in_year': year.days_in_year} for year in TaxYear.objects.all()],
            response.json()
        )

    def test_get_id(self):
        year2020 = TaxYear.objects.create(year=2020)
        year2021 = TaxYear.objects.create(year=2021)
        self.authenticate()
        response = self.client.get(f"{self.url}{year2020.id}/")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual({'year': 2020, 'id': year2020.id, 'days_in_year': 366}, response.json())
        response = self.client.get(f"{self.url}{year2021.id}/")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual({'year': 2021, 'id': year2021.id, 'days_in_year': 365}, response.json())

    def test_get_filter(self):
        year2020 = TaxYear.objects.create(year=2020)
        year2021 = TaxYear.objects.create(year=2021)
        self.authenticate()
        response = self.client.get(f"{self.url}?year=2020")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual([{'year': 2020, 'id': year2020.id, 'days_in_year': year2020.days_in_year}], response.json())
        response = self.client.get(f"{self.url}?year_lt=2021")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual([{'year': 2020, 'id': year2020.id, 'days_in_year': year2020.days_in_year}], response.json())
        response = self.client.get(f"{self.url}?year_lt=2022")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual([
            {'year': 2020, 'id': year2020.id, 'days_in_year': year2020.days_in_year},
            {'year': 2021, 'id': year2021.id, 'days_in_year': year2021.days_in_year}
        ], response.json())

    def test_create_one(self):
        # Create one item, test the response and the created object
        self.authenticate()
        item = {'year': 2021}
        response = self.client.post(self.url, json.dumps(item), content_type='application/json; charset=utf-8')
        self.assertEquals(201, response.status_code, response.content)
        self.assertDictEqual({**item, 'days_in_year': 365}, self.strip_id(response.json()))
        self.assertEquals(1, TaxYear.objects.count())
        self.assertEquals(item['year'], TaxYear.objects.first().year)

    def test_create_two(self):
        # Create two items with the same input. Test that only one item is created
        self.authenticate()
        item = {'year': 2021}
        response = self.client.post(self.url, json.dumps(item), content_type='application/json; charset=utf-8')
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        self.assertEquals(1, TaxYear.objects.count())
        response2 = self.client.post(self.url, json.dumps(item), content_type='application/json; charset=utf-8')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response2.status_code)
        self.assertEquals(1, TaxYear.objects.count())

    def test_invalid_input(self):
        # Create an item with invalid input and expect errors
        self.authenticate()
        inputs = self.invalid_submit_body + \
            [{'year': x} for x in self.invalid_year_values]
        for input in inputs:
            response = self.client.post(self.url, json.dumps(input), content_type='application/json; charset=utf-8')
            self.assertEquals(400, response.status_code, input)


class PersonTest(RestTest):
    url = '/rest/person/'

    def test_get_all(self):
        Person.objects.create(cpr='1234567890')
        Person.objects.create(cpr='1234567891')
        self.authenticate()
        response = self.client.get(self.url)
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(
            [{'cpr': person.cpr, 'id': person.id} for person in Person.objects.all()],
            response.json()
        )

    def test_get_id(self):
        person1 = Person.objects.create(cpr='1234567890')
        person2 = Person.objects.create(cpr='1234567891')
        self.authenticate()
        response = self.client.get(f"{self.url}{person1.id}/")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual({'cpr': '1234567890', 'id': person1.id}, response.json())
        response = self.client.get(f"{self.url}{person2.id}/")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual({'cpr': '1234567891', 'id': person2.id}, response.json())

    def test_get_filter(self):
        person1 = Person.objects.create(cpr='1234567890')
        Person.objects.create(cpr='1234567891')
        self.authenticate()
        response = self.client.get(f"{self.url}?cpr=1234567890")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual([{'cpr': '1234567890', 'id': person1.id}], response.json())

    def test_create_one(self):
        # Create one item, test the response and the created object
        self.authenticate()
        item = {'cpr': '1234567890'}
        response = self.client.post(self.url, json.dumps(item), content_type='application/json; charset=utf-8')
        self.assertEquals(201, response.status_code, response.content)
        self.assertDictEqual(item, self.strip_id(response.json()))
        self.assertEquals(1, Person.objects.count())
        self.assertEquals(item['cpr'], Person.objects.first().cpr)

    def test_create_two(self):
        # Create two items with the same input. Test that only one item is created
        self.authenticate()
        item = {'cpr': '1234567890'}
        response = self.client.post(self.url, json.dumps(item), content_type='application/json; charset=utf-8')
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        self.assertEquals(1, Person.objects.count())
        response2 = self.client.post(self.url, json.dumps(item), content_type='application/json; charset=utf-8')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response2.status_code)
        self.assertEquals(1, Person.objects.count())

    def test_invalid_input(self):
        # Create an item with invalid input and expect errors
        self.authenticate()
        inputs = self.invalid_submit_body + \
            [{'cpr': x} for x in self.invalid_cpr_values]
        for input in inputs:
            response = self.client.post(self.url, json.dumps(input), content_type='application/json; charset=utf-8')
            self.assertEquals(400, response.status_code, input)


class PensionCompanyTest(RestTest):

    url = '/rest/pension_company/'

    extra_fields = {
        'agreement_present': False,
        'phone': None,
        'email': None,
        'domestic_or_foreign': PensionCompany.DOF_UNKNOWN,
        'accepts_payments': False,
    }

    def test_get_all(self):
        pension_company_data1 = {'res': '12345678', 'name': 'Foobar A/S', 'address': 'Foobarvej 42'}
        pension_company_data2 = {'res': '12345670', 'name': 'Hephey A/S', 'address': 'Hepheyvej 21'}
        PensionCompany.objects.create(**pension_company_data1)
        PensionCompany.objects.create(**pension_company_data2)
        self.authenticate()
        response = self.client.get(self.url)
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(
            [
                {**{key: getattr(person, key) for key in ['res', 'name', 'address', 'phone', 'email', 'agreement_present', 'domestic_or_foreign', 'accepts_payments']}, 'id': person.id, **self.extra_fields}
                for person in PensionCompany.objects.all()
            ],
            response.json()
        )

    def test_get_id(self):
        pension_company_data1 = {'res': 12345678, 'name': 'Foobar A/S', 'address': 'Foobarvej 42'}
        pension_company_data2 = {'res': 12345670, 'name': 'Hephey A/S', 'address': 'Hepheyvej 21'}
        pension_company1 = PensionCompany.objects.create(**pension_company_data1)
        pension_company2 = PensionCompany.objects.create(**pension_company_data2)
        self.authenticate()
        response = self.client.get(f"{self.url}{pension_company1.id}/")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual({**pension_company_data1, 'id': pension_company1.id, **self.extra_fields}, response.json())
        response = self.client.get(f"{self.url}{pension_company2.id}/")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual({**pension_company_data2, 'id': pension_company2.id, **self.extra_fields}, response.json())

    def test_get_filter(self):
        pension_company_data1 = {'res': 12345678, 'name': 'Foobar A/S', 'address': 'Foobarvej 42'}
        pension_company_data2 = {'res': 12345670, 'name': 'Hephey A/S', 'address': 'Hepheyvej 21'}
        pension_company1 = PensionCompany.objects.create(**pension_company_data1)
        PensionCompany.objects.create(**pension_company_data2)
        self.authenticate()
        response = self.client.get(f"{self.url}?res=12345678")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual([{**pension_company_data1, 'id': pension_company1.id, **self.extra_fields}], response.json())

    def test_create_one(self):
        # Create one item, test the response and the created object
        self.authenticate()
        pension_company_data1 = {'res': 12345678, 'name': 'Foobar A/S', 'address': 'Foobarvej 42'}
        response = self.client.post(self.url, json.dumps(pension_company_data1), content_type='application/json; charset=utf-8')
        self.assertEquals(201, response.status_code, response.content)
        self.assertDictEqual({**pension_company_data1, **self.extra_fields}, self.strip_id(response.json()))
        self.assertEquals(1, PensionCompany.objects.count())
        self.assertEquals(pension_company_data1['res'], PensionCompany.objects.first().res)

    def test_create_two(self):
        # Create two items with the same input. Test that only one item is created
        self.authenticate()
        pension_company_data1 = {'res': 12345678, 'name': 'Foobar A/S', 'address': 'Foobarvej 42'}
        self.client.post(self.url, json.dumps(pension_company_data1), content_type='application/json; charset=utf-8')
        self.assertEquals(1, PensionCompany.objects.count())
        response2 = self.client.post(self.url, json.dumps(pension_company_data1), content_type='application/json; charset=utf-8')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response2.status_code)
        self.assertEquals(1, PensionCompany.objects.count())

    def test_invalid_input(self):
        # Create an item with invalid input and expect errors
        self.authenticate()
        full = {'res': 12345678, 'name': 'Foobar A/S', 'address': 'Foobarvej 42'}
        inputs = self.invalid_submit_body + \
            [{**full, 'res': x} for x in self.invalid_res_values] + \
            [{**full, 'name': x} for x in ['x'*256]]
        for input in inputs:
            response = self.client.post(self.url, json.dumps(input), content_type='application/json; charset=utf-8')
            self.assertEquals(400, response.status_code, input)


class PersonTaxYearTest(RestTest):
    url = '/rest/person_tax_year/'

    def test_get_all(self):
        person = Person.objects.create(
            cpr='1234567890'
        )
        PersonTaxYear.objects.create(
            person=person,
            tax_year=TaxYear.objects.create(year=2020),
            number_of_days=366,
        )
        PersonTaxYear.objects.create(
            person=person,
            tax_year=TaxYear.objects.create(year=2021),
            fully_tax_liable=False,
            number_of_days=365,
        )
        extra = {}
        self.authenticate()
        response = self.client.get(self.url)
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(
            [
                {
                    'person': person.cpr,
                    'tax_year': person_tax_year.tax_year.year,
                    'id': person_tax_year.id,
                    'fully_tax_liable': person_tax_year.fully_tax_liable,
                    'days_in_year_factor': person_tax_year.days_in_year_factor,
                    'number_of_days': person_tax_year.number_of_days,
                    'foreign_pension_notes': person_tax_year.foreign_pension_notes,
                    'general_notes': person_tax_year.general_notes,
                    **extra
                }
                for person_tax_year in PersonTaxYear.objects.all()
            ],
            response.json()
        )

    def test_get_id(self):
        person = Person.objects.create(
            cpr='1234567890'
        )
        person_tax_year1 = PersonTaxYear.objects.create(
            person=person,
            tax_year=TaxYear.objects.create(year=2020),
            fully_tax_liable=False,
            number_of_days=366,
        )
        person_tax_year2 = PersonTaxYear.objects.create(
            person=person,
            tax_year=TaxYear.objects.create(year=2021),
            fully_tax_liable=True,
            number_of_days=365,
        )
        extra = {}
        self.authenticate()
        response = self.client.get(f"{self.url}{person_tax_year1.id}/")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual({
            'person': person.cpr,
            'tax_year': person_tax_year1.tax_year.year,
            'id': person_tax_year1.id,
            'fully_tax_liable': person_tax_year1.fully_tax_liable,
            'days_in_year_factor': person_tax_year1.days_in_year_factor,
            'number_of_days': person_tax_year1.number_of_days,
            'foreign_pension_notes': person_tax_year1.foreign_pension_notes,
            'general_notes': person_tax_year1.general_notes,
            **extra
        }, response.json())
        response = self.client.get(f"{self.url}{person_tax_year2.id}/")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual({
            'person': person.cpr,
            'tax_year': person_tax_year2.tax_year.year,
            'id': person_tax_year2.id,
            'fully_tax_liable': person_tax_year2.fully_tax_liable,
            'days_in_year_factor': person_tax_year2.days_in_year_factor,
            'number_of_days': person_tax_year2.number_of_days,
            'foreign_pension_notes': person_tax_year2.foreign_pension_notes,
            'general_notes': person_tax_year2.general_notes,
            **extra
        }, response.json())

    def test_get_filter(self):
        person_tax_year1 = PersonTaxYear.objects.create(
            person=Person.objects.create(cpr='1234567890'),
            tax_year=TaxYear.objects.create(year=2020),
            fully_tax_liable=True,
            number_of_days=366,
        )
        person_tax_year2 = PersonTaxYear.objects.create(
            person=Person.objects.create(cpr='1234567891'),
            tax_year=TaxYear.objects.create(year=2021),
            fully_tax_liable=False,
            number_of_days=365,
        )
        extra = {}
        self.authenticate()
        response = self.client.get(f"{self.url}?cpr=1234567890")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual([{
            'person': person_tax_year1.person.cpr,
            'tax_year': person_tax_year1.tax_year.year,
            'id': person_tax_year1.id,
            'fully_tax_liable': person_tax_year1.fully_tax_liable,
            'days_in_year_factor': person_tax_year1.days_in_year_factor,
            'number_of_days': person_tax_year1.number_of_days,
            'foreign_pension_notes': person_tax_year1.foreign_pension_notes,
            'general_notes': person_tax_year1.general_notes,
            **extra
        }], response.json())
        response = self.client.get(f"{self.url}?year=2021")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual([{
            'person': person_tax_year2.person.cpr,
            'tax_year': person_tax_year2.tax_year.year,
            'id': person_tax_year2.id,
            'fully_tax_liable': person_tax_year2.fully_tax_liable,
            'days_in_year_factor': person_tax_year2.days_in_year_factor,
            'number_of_days': person_tax_year2.number_of_days,
            'foreign_pension_notes': person_tax_year2.foreign_pension_notes,
            'general_notes': person_tax_year2.general_notes,
            **extra
        }], response.json())
        response = self.client.get(f"{self.url}?cpr=1234567890&year=2020")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual([{
            'person': person_tax_year1.person.cpr,
            'tax_year': person_tax_year1.tax_year.year,
            'id': person_tax_year1.id,
            'fully_tax_liable': person_tax_year1.fully_tax_liable,
            'days_in_year_factor': person_tax_year1.days_in_year_factor,
            'number_of_days': person_tax_year1.number_of_days,
            'foreign_pension_notes': person_tax_year1.foreign_pension_notes,
            'general_notes': person_tax_year1.general_notes,
            **extra
        }], response.json())
        response = self.client.get(f"{self.url}?cpr=1234567891&year=2020")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual([], response.json())

    def test_create_one(self):
        # Create one item, test the response and the created object
        person = Person.objects.create(cpr='1234567890')
        tax_year = TaxYear.objects.create(year=2020)
        self.authenticate()
        item = {'person': '1234567890', 'tax_year': 2020}
        response = self.client.post(self.url, json.dumps(item), content_type='application/json; charset=utf-8')
        self.assertEquals(201, response.status_code, response.content)
        self.assertDictEqual({
            **item,
            'fully_tax_liable': True,
            'days_in_year_factor': 1,
            'number_of_days': None,
            'foreign_pension_notes': None,
            'general_notes': None,
        }, self.strip_id(response.json()))
        self.assertEquals(1, PersonTaxYear.objects.count())
        self.assertEquals(person.cpr, PersonTaxYear.objects.first().person.cpr)
        self.assertEquals(tax_year.year, PersonTaxYear.objects.first().tax_year.year)

    def test_create_two(self):
        # Create two items with the same input. Test that only one item is created
        person = Person.objects.create(cpr='1234567890')
        tax_year = TaxYear.objects.create(year=2020)
        self.authenticate()
        item = {'person': '1234567890', 'tax_year': 2020}
        response = self.client.post(self.url, json.dumps(item), content_type='application/json; charset=utf-8')
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        self.assertEquals(1, PersonTaxYear.objects.count())
        response2 = self.client.post(self.url, json.dumps(item), content_type='application/json; charset=utf-8')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response2.status_code)
        self.assertEquals(1, PersonTaxYear.objects.count())
        self.assertEquals(person.cpr, PersonTaxYear.objects.first().person.cpr)
        self.assertEquals(tax_year.year, PersonTaxYear.objects.first().tax_year.year)

    def test_invalid_input(self):
        # Create an item with invalid input and expect errors
        person = Person.objects.create(cpr='1234567890')
        tax_year = TaxYear.objects.create(year=2020)
        self.authenticate()
        full = {'person': person.id, 'tax_year': tax_year.id}
        inputs = self.invalid_submit_body + \
            [{**full, 'person': x} for x in self.invalid_fk_values + [person.id + 1]] + \
            [{**full, 'tax_year': x} for x in self.invalid_fk_values + [tax_year.id + 1]]
        for input in inputs:
            response = self.client.post(self.url, json.dumps(input), content_type='application/json; charset=utf-8')
            self.assertEquals(400, response.status_code, input)


class PolicyTaxYearTest(RestTest):
    url = '/rest/policy_tax_year/'

    def test_get_all(self):
        person = Person.objects.create(cpr='1234567890')
        pension_company = PensionCompany.objects.create(
            res=12345678,
            name='Foobar A/S',
            address='Foobarvej 42'
        )
        person_tax_year = PersonTaxYear.objects.create(
            person=person,
            tax_year=TaxYear.objects.create(year=2020),
            number_of_days=366,
        )
        PolicyTaxYear.objects.create(
            policy_number='1234',
            person_tax_year=person_tax_year,
            pension_company=pension_company,
            prefilled_amount=100,
            self_reported_amount=100,
            preliminary_paid_amount=0,
            from_pension=True,
        )
        PolicyTaxYear.objects.create(
            policy_number='5678',
            person_tax_year=person_tax_year,
            pension_company=pension_company,
            prefilled_amount=200,
            self_reported_amount=200,
            preliminary_paid_amount=20,
            from_pension=False,
        )
        extra = {}
        self.authenticate()
        response = self.client.get(self.url)
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual(
            [
                {
                    'person_tax_year': person_tax_year.id,
                    'policy_number': policy_tax_year.policy_number,
                    'id': policy_tax_year.id,
                    'prefilled_amount': policy_tax_year.prefilled_amount,
                    'self_reported_amount': policy_tax_year.self_reported_amount,
                    'pension_company': pension_company.id,
                    'preliminary_paid_amount': policy_tax_year.preliminary_paid_amount,
                    'foreign_paid_amount_self_reported': policy_tax_year.foreign_paid_amount_self_reported,
                    'available_deduction_from_previous_years': policy_tax_year.available_deduction_from_previous_years,
                    'applied_deduction_from_previous_years': policy_tax_year.applied_deduction_from_previous_years,
                    'from_pension': policy_tax_year.from_pension,
                    'policy_documents': [],
                    'year_adjusted_amount': policy_tax_year.year_adjusted_amount,
                    'calculated_result': policy_tax_year.calculated_result,
                    'estimated_amount': policy_tax_year.estimated_amount,
                    'foreign_paid_amount_actual': policy_tax_year.foreign_paid_amount_actual,
                    **extra
                }
                for policy_tax_year in PolicyTaxYear.objects.all()
            ],
            response.json()
        )

    def test_get_id(self):
        person = Person.objects.create(cpr='1234567890')
        person_tax_year = PersonTaxYear.objects.create(
            person=person,
            tax_year=TaxYear.objects.create(year=2020),
            number_of_days=366,
        )
        pension_company = PensionCompany.objects.create(
            res=12345678,
            name='Foobar A/S',
            address='Foobarvej 42'
        )
        policy_tax_year1 = PolicyTaxYear.objects.create(
            policy_number='1234',
            person_tax_year=person_tax_year,
            pension_company=pension_company,
            prefilled_amount=100,
            self_reported_amount=100,
            preliminary_paid_amount=50,
            from_pension=False,
        )
        policy_tax_year2 = PolicyTaxYear.objects.create(
            policy_number='5678',
            person_tax_year=person_tax_year,
            pension_company=pension_company,
            prefilled_amount=200,
            self_reported_amount=200,
            preliminary_paid_amount=0,
            from_pension=True,
        )

        self.authenticate()

        response = self.client.get(f"{self.url}{policy_tax_year1.id}/")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual({
            'person_tax_year': person_tax_year.id,
            'policy_number': policy_tax_year1.policy_number,
            'id': policy_tax_year1.id,
            'prefilled_amount': policy_tax_year1.prefilled_amount,
            'self_reported_amount': policy_tax_year1.self_reported_amount,
            'pension_company': pension_company.id,
            'preliminary_paid_amount': policy_tax_year1.preliminary_paid_amount,
            'foreign_paid_amount_self_reported': policy_tax_year1.foreign_paid_amount_self_reported,
            'available_deduction_from_previous_years': policy_tax_year1.available_deduction_from_previous_years,
            'applied_deduction_from_previous_years': policy_tax_year1.applied_deduction_from_previous_years,
            'from_pension': policy_tax_year1.from_pension,
            'policy_documents': [],
            'year_adjusted_amount': policy_tax_year1.year_adjusted_amount,
            'calculated_result': policy_tax_year1.calculated_result,
            'estimated_amount': policy_tax_year1.estimated_amount,
            'foreign_paid_amount_actual': policy_tax_year1.foreign_paid_amount_actual,
        }, response.json())

        response = self.client.get(f"{self.url}{policy_tax_year2.id}/")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual({
            'person_tax_year': person_tax_year.id,
            'policy_number': policy_tax_year2.policy_number,
            'id': policy_tax_year2.id,
            'prefilled_amount': policy_tax_year2.prefilled_amount,
            'self_reported_amount': policy_tax_year2.self_reported_amount,
            'pension_company': pension_company.id,
            'preliminary_paid_amount': policy_tax_year2.preliminary_paid_amount,
            'foreign_paid_amount_self_reported': policy_tax_year2.foreign_paid_amount_self_reported,
            'available_deduction_from_previous_years': policy_tax_year2.available_deduction_from_previous_years,
            'applied_deduction_from_previous_years': policy_tax_year2.applied_deduction_from_previous_years,
            'from_pension': policy_tax_year2.from_pension,
            'policy_documents': [],
            'year_adjusted_amount': policy_tax_year1.year_adjusted_amount,
            'calculated_result': policy_tax_year1.calculated_result,
            'estimated_amount': policy_tax_year1.estimated_amount,
            'foreign_paid_amount_actual': policy_tax_year1.foreign_paid_amount_actual,
        }, response.json())

    def test_get_filter(self):
        person_tax_year1 = PersonTaxYear.objects.create(
            person=Person.objects.create(cpr='1234567890'),
            tax_year=TaxYear.objects.create(year=2020),
            number_of_days=366,
        )
        person_tax_year2 = PersonTaxYear.objects.create(
            person=Person.objects.create(cpr='1234567891'),
            tax_year=TaxYear.objects.create(year=2021),
            number_of_days=365,
        )
        pension_company = PensionCompany.objects.create(
            res=12345678,
            name='Foobar A/S',
            address='Foobarvej 42'
        )
        policy_tax_year1 = PolicyTaxYear.objects.create(
            policy_number='1234',
            person_tax_year=person_tax_year1,
            pension_company=pension_company,
            prefilled_amount=100,
            self_reported_amount=100,
            preliminary_paid_amount=50,
            foreign_paid_amount_self_reported=0,
            from_pension=True,
        )
        policy_tax_year2 = PolicyTaxYear.objects.create(
            policy_number='5678',
            person_tax_year=person_tax_year2,
            pension_company=pension_company,
            prefilled_amount=200,
            self_reported_amount=200,
            preliminary_paid_amount=50,
            foreign_paid_amount_self_reported=0,
            from_pension=False,
        )
        self.authenticate()

        response = self.client.get(f"{self.url}?cpr=1234567890")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual([{
            'person_tax_year': person_tax_year1.id,
            'policy_number': policy_tax_year1.policy_number,
            'id': policy_tax_year1.id,
            'prefilled_amount': policy_tax_year1.prefilled_amount,
            'self_reported_amount': policy_tax_year1.self_reported_amount,
            'pension_company': pension_company.id,
            'preliminary_paid_amount': policy_tax_year1.preliminary_paid_amount,
            'foreign_paid_amount_self_reported': policy_tax_year1.foreign_paid_amount_self_reported,
            'available_deduction_from_previous_years': policy_tax_year1.available_deduction_from_previous_years,
            'applied_deduction_from_previous_years': policy_tax_year1.applied_deduction_from_previous_years,
            'from_pension': policy_tax_year1.from_pension,
            'policy_documents': [],
            'year_adjusted_amount': policy_tax_year1.year_adjusted_amount,
            'calculated_result': policy_tax_year1.calculated_result,
            'estimated_amount': policy_tax_year1.estimated_amount,
            'foreign_paid_amount_actual': policy_tax_year1.foreign_paid_amount_actual,
        }], response.json())

        response = self.client.get(f"{self.url}?year=2020")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual([{
            'person_tax_year': person_tax_year1.id,
            'policy_number': policy_tax_year1.policy_number,
            'id': policy_tax_year1.id,
            'prefilled_amount': policy_tax_year1.prefilled_amount,
            'self_reported_amount': policy_tax_year1.self_reported_amount,
            'pension_company': pension_company.id,
            'preliminary_paid_amount': policy_tax_year1.preliminary_paid_amount,
            'foreign_paid_amount_self_reported': policy_tax_year1.foreign_paid_amount_self_reported,
            'available_deduction_from_previous_years': policy_tax_year1.available_deduction_from_previous_years,
            'applied_deduction_from_previous_years': policy_tax_year1.applied_deduction_from_previous_years,
            'from_pension': policy_tax_year1.from_pension,
            'policy_documents': [],
            'year_adjusted_amount': policy_tax_year1.year_adjusted_amount,
            'calculated_result': policy_tax_year1.calculated_result,
            'estimated_amount': policy_tax_year1.estimated_amount,
            'foreign_paid_amount_actual': policy_tax_year1.foreign_paid_amount_actual,
        }], response.json())

        response = self.client.get(f"{self.url}?cpr=1234567891&year=2021")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual([{
            'person_tax_year': person_tax_year2.id,
            'policy_number': policy_tax_year2.policy_number,
            'id': policy_tax_year2.id,
            'prefilled_amount': policy_tax_year2.prefilled_amount,
            'self_reported_amount': policy_tax_year2.self_reported_amount,
            'pension_company': pension_company.id,
            'preliminary_paid_amount': policy_tax_year2.preliminary_paid_amount,
            'foreign_paid_amount_self_reported': policy_tax_year1.foreign_paid_amount_self_reported,
            'available_deduction_from_previous_years': policy_tax_year1.available_deduction_from_previous_years,
            'applied_deduction_from_previous_years': policy_tax_year1.applied_deduction_from_previous_years,
            'from_pension': policy_tax_year2.from_pension,
            'policy_documents': [],
            'year_adjusted_amount': policy_tax_year2.year_adjusted_amount,
            'calculated_result': policy_tax_year2.calculated_result,
            'estimated_amount': policy_tax_year2.estimated_amount,
            'foreign_paid_amount_actual': policy_tax_year2.foreign_paid_amount_actual,
        }], response.json())

        response = self.client.get(f"{self.url}?cpr=1234567891&year=2020")
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertCountEqual([], response.json())

    def test_update_one(self):
        # Update one item, test the response and the created object
        person_tax_year = PersonTaxYear.objects.create(
            person=Person.objects.create(cpr='1234567890'),
            tax_year=TaxYear.objects.create(year=2021),
            number_of_days=365,
        )
        pension_company = PensionCompany.objects.create(
            res=12345678,
            name='Foobar A/S',
            address='Foobarvej 42'
        )
        policy_tax_year = PolicyTaxYear.objects.create(
            pension_company=pension_company,
            policy_number='1234',
            person_tax_year=person_tax_year,
            prefilled_amount=100
        )
        self.authenticate()
        item = {
            'self_reported_amount': 200,
            'preliminary_paid_amount': 30,
            'foreign_paid_amount_self_reported': 0,
            'from_pension': True,
        }
        response = self.client.patch(f"{self.url}{policy_tax_year.id}/", json.dumps(item), content_type='application/json; charset=utf-8')
        policy_tax_year.refresh_from_db()
        self.assertEquals(200, response.status_code, response.content)
        self.assertDictEqual(
            {
                **item,
                'pension_company': pension_company.id,
                'person_tax_year': person_tax_year.id,
                'policy_number': policy_tax_year.policy_number,
                'prefilled_amount': policy_tax_year.prefilled_amount,
                'available_deduction_from_previous_years': policy_tax_year.available_deduction_from_previous_years,
                'applied_deduction_from_previous_years': policy_tax_year.applied_deduction_from_previous_years,
                'policy_documents': [],
                'year_adjusted_amount': policy_tax_year.year_adjusted_amount,
                'calculated_result': policy_tax_year.calculated_result,
                'estimated_amount': policy_tax_year.estimated_amount,
                'foreign_paid_amount_actual': policy_tax_year.foreign_paid_amount_actual,
            },
            self.strip_id(response.json())
        )
        data = response.json()
        policy_tax_year.refresh_from_db()
        self.assertEquals(policy_tax_year.self_reported_amount, data['self_reported_amount'])
        self.assertEquals(policy_tax_year.prefilled_amount, data['prefilled_amount'])
        self.assertEquals(policy_tax_year.from_pension, data['from_pension'])

    def test_invalid_input(self):
        # Create an item with invalid input and expect errors
        person_tax_year = PersonTaxYear.objects.create(
            person=Person.objects.create(cpr='1234567890'),
            tax_year=TaxYear.objects.create(year=2021),
            number_of_days=365,
        )
        pension_company = PensionCompany.objects.create(
            res=12345678,
            name='Foobar A/S',
            address='Foobarvej 42'
        )
        self.authenticate()
        full = {
            'policy_number': '1234',
            'prefilled_amount': 100,
            'self_reported_amount': 200,
            'person_tax_year': person_tax_year.id,
            'pension_company': pension_company.id,
            'preliminary_paid_amount': '10.25',
            'foreign_paid_amount_self_reported': 0,
            'from_pension': True
        }

        inputs = self.invalid_submit_body + \
            [{**full, 'prefilled_amount': x} for x in self.invalid_amount_values] + \
            [{**full, 'self_reported_amount': x} for x in self.invalid_amount_values] + \
            [{**full, 'preliminary_paid_amount': x} for x in self.invalid_positive_amount_values] + \
            [{**full, 'from_pension': x} for x in self.invalid_boolean_values]
        for input in inputs:
            response = self.client.post(self.url, json.dumps(input), content_type='application/json; charset=utf-8')
            self.assertEquals(400, response.status_code, input)


class PolicyDocumentTest(RestTest):

    url = '/rest/policy_document/'

    def test_upload(self):
        policy_tax_year = PolicyTaxYear.objects.create(
            policy_number='1234',
            prefilled_amount=200,
            self_reported_amount=250,
            person_tax_year=PersonTaxYear.objects.create(
                person=Person.objects.create(cpr='1234567890'),
                tax_year=TaxYear.objects.create(year=2021),
                number_of_days=365,
            ),
            pension_company=PensionCompany.objects.create(
                res=12345678,
                name='Foobar A/S',
                address='Foobarvej 42'
            )
        )
        self.authenticate()

        filename = os.path.join(self.testresources_folder, 'textfile.txt')
        self.assertTrue(os.path.isfile(filename))

        with open(filename, 'rb') as fp:
            b = fp.read()
            upload_file = SimpleUploadedFile('textfile.txt', b, content_type="text/plain")
            response = self.client.post(self.url, {
                'policy_tax_year': policy_tax_year.id,
                'name': 'Testfile',
                'description': 'File used in automated test',
                'file': upload_file,
            }, format="multipart", headers={"Authorization": "Token "+self.token.key})
            self.assertEquals(status.HTTP_201_CREATED, response.status_code)
            self.assertEquals(1, PolicyDocument.objects.count())
            policy_document = PolicyDocument.objects.first()
            upload_file.seek(0)
            self.assertEquals(upload_file.readlines(), policy_document.file.readlines())

    def test_invalid_input(self):
        # Create an item with invalid input and expect errors
        policy_tax_year = PolicyTaxYear.objects.create(
            policy_number='1234',
            prefilled_amount=200,
            self_reported_amount=250,
            person_tax_year=PersonTaxYear.objects.create(
                person=Person.objects.create(cpr='1234567890'),
                tax_year=TaxYear.objects.create(year=2021),
                number_of_days=365,
            ),
            pension_company=PensionCompany.objects.create(
                res=12345678,
                name='Foobar A/S',
                address='Foobarvej 42'
            )
        )
        self.authenticate()

        filename = os.path.join(self.testresources_folder, 'textfile.txt')
        with open(filename, 'rb') as fp:
            b = fp.read()
            upload_file = SimpleUploadedFile('textfile.txt', b, content_type="text/plain")
        full = {'policy_tax_year': policy_tax_year.id, 'name': 'Testfile', 'description': 'File used in automated test', 'file': upload_file}

        inputs = [{**full, 'policy_tax_year': x} for x in self.invalid_fk_values + [policy_tax_year.id + 1]] + \
                 [{**full, 'name': x} for x in self.invalid_string_values + ['x'*256]] + \
                 [{**full, 'description': x} for x in self.invalid_string_values] + \
                 [{**full, 'file': x} for x in self.invalid_filedata_values]

        for input in inputs:
            if len([v for v in input.values() if v in [{}, None]]):  # Skip setups with values that cannot even be sent out in a multipart request
                continue
            response = self.client.post(self.url, input, format="multipart")
            self.assertEquals(400, response.status_code, input)
