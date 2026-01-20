from django.core.management.base import BaseCommand

from eskat.models import ImportedKasMandtal
from kas.models import PersonTaxYear, PolicyTaxYear


class Command(BaseCommand):
    help = "Cleans up PersonTaxYears that are not present in Mandtal"

    def add_arguments(self, parser):
        parser.add_argument("year", type=int)
        parser.add_argument("--perform-delete", action="store_true")

    def handle(self, *args, **options):
        year = options["year"]
        persontaxyear_cprs = set(
            [
                result["person__cpr"]
                for result in PersonTaxYear.objects.filter(tax_year__year=year).values(
                    "person__cpr"
                )
            ]
        )
        mandtal_cprs = set(
            [
                result["cpr"]
                for result in ImportedKasMandtal.objects.filter(skatteaar=year).values(
                    "cpr"
                )
            ]
        )
        extraneous = persontaxyear_cprs - mandtal_cprs
        print(f"These cprs are in persontaxyear but not in mandtal: {list(extraneous)}")
        if options["perform_delete"]:
            print("They will be deleted")
            persontaxyear_extraneous = PersonTaxYear.objects.filter(
                person__cpr__in=extraneous
            )
            policytaxyear_extraneous = PolicyTaxYear.objects.filter(
                person_tax_year__in=persontaxyear_extraneous
            )
            policytaxyear_extraneous.delete()
            persontaxyear_extraneous.delete()
        else:
            print("Not deleting; add --perform-delete to input args to delete")
