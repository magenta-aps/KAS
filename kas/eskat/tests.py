from django.test import TestCase, override_settings
from eskat.management.commands.import_eskat_mockup_data import Command
from eskat.models import MockModels

# Need to import the module here since we want to fetch models using runtime
# properties.
import eskat.models as eskat_models


# Make sure this test never uses the production eSkat database
@override_settings(ENVIRONMENT="development")
class EskatModelsTestCase(TestCase):

    imported_tables = (
        eskat_models.ImportedKasBeregningerX,
        eskat_models.ImportedKasMandtal,
        eskat_models.ImportedR75PrivatePension,
    )

    def import_all_tables(self):

        # Run imports for years 2018 and 2019 on all Imported tables, moving
        # data from mock tables to imported tables
        for year in (2018, 2019):
            for model in self.imported_tables:
                model.import_year(year)

    def setUp(self):

        # Run the import command, importing data files into the Mockup tables
        Command().handle()

        # And import data from mockup tables to imported tables
        self.import_all_tables()

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

        self.assertGreater(MockModels.MockKasBeregningerX.objects.count(), 0)
        self.assertGreater(MockModels.MockKasMandtal.objects.count(), 0)
        self.assertGreater(MockModels.MockR75PrivatePension.objects.count(), 0)

    def test_imported_data_present(self):
        for x in self.imported_tables:
            self.assertGreater(x.objects.count(), 0)

    def test_mock_reimport_does_not_create_new_entries(self):
        tables = (
            eskat_models.get_kas_beregninger_x_model(),
            eskat_models.get_kas_mandtal_model(),
            eskat_models.get_r75_private_pension_model(),
        )

        before_counts = [x.objects.count() for x in tables]
        Command().handle()
        after_counts = [x.objects.count() for x in tables]

        self.assertEquals(before_counts, after_counts)

    def test_reimport_does_not_create_new_entries(self):

        before_counts = [x.objects.count() for x in self.imported_tables]
        self.import_all_tables()
        after_counts = [x.objects.count() for x in self.imported_tables]

        self.assertEquals(before_counts, after_counts)

    def test_update_creates_history(self):

        for model in self.imported_tables:
            item = model.objects.first()

            count_before = item.history.count()

            item._change_reason = "Updated during testing"
            item.save()

            count_after = item.history.count()

            self.assertEqual(count_before + 1, count_after)
