import eskat.models as eskat_models
from django.apps import apps
from django.test import TestCase, override_settings
from eskat.database_routers import ESkatRouter
from eskat.jobs import delete_protected
from eskat.mockupdata import generate_persons
from eskat.models import MockModels

import kas.models as kas_models
from kas.models import Person, PersonTaxYear, PolicyDocument, TaxYear


class EskatModelsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        generate_persons()

    def test_models_points_to_mock_database(self):
        for model in (
            eskat_models.get_kas_beregninger_x_model(),
            eskat_models.get_kas_mandtal_model(),
            eskat_models.get_r75_private_pension_model(),
        ):
            self.assertTrue(model._meta.model_name.startswith("mock"))

    @override_settings(ENVIRONMENT="production")
    def test_prod_models_points_to_real_database(self):
        for model in (
            eskat_models.get_kas_beregninger_x_model(),
            eskat_models.get_kas_mandtal_model(),
            eskat_models.get_r75_private_pension_model(),
        ):
            self.assertFalse(model._meta.model_name.startswith("mock"))

    def test_mockup_data_present(self):
        self.assertTrue(MockModels.MockKasMandtal.objects.exists())
        self.assertTrue(MockModels.MockR75Idx4500230.objects.exists())

    def test_delete_protected(self):
        person = Person.objects.create()
        tax_year = TaxYear.objects.create(year=2023)
        person_tax_year = PersonTaxYear.objects.create(tax_year=tax_year, person=person)
        PolicyDocument.objects.create(person_tax_year=person_tax_year)

        for model in apps.all_models.get("kas").values():
            delete_protected(model.objects.all())

        self.assertFalse(Person.objects.exists())
        self.assertFalse(TaxYear.objects.exists())
        self.assertFalse(PersonTaxYear.objects.exists())
        self.assertFalse(PolicyDocument.objects.exists())


class ESkatRouterTestCase(TestCase):
    def setUp(self):
        self.router = ESkatRouter()
        self.eskat_model = eskat_models.EskatModels.KasMandtal
        self.kas_model = kas_models.FinalSettlement

    def test_db_for_read(self):
        self.assertEqual(self.router.db_for_read(self.eskat_model), "eskat")
        self.assertEqual(self.router.db_for_read(self.kas_model), None)

    def test_db_for_write(self):
        self.assertEqual(self.router.db_for_write(self.eskat_model), "eskat")
        self.assertEqual(self.router.db_for_write(self.kas_model), None)

    def test_allow_migrate(self):
        self.assertFalse(self.router.allow_migrate("eskat", None))
        self.assertEqual(self.router.allow_migrate("kas", None), None)
