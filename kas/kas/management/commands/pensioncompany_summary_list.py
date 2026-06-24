from django.core.management import BaseCommand

from kas.models import TaxYear, TotalPensionCompanySummaryFile


class Command(BaseCommand):
    help = """
        Calculates a summarized overview for all PensionCompanies
        and returns a .csv table
    """

    def add_arguments(self, parser):
        parser.add_argument("year", type=int)

    def handle(self, *args, **options):
        year = options["year"]
        try:
            tax_year = TaxYear.objects.get(year)
        except TaxYear.ObjectDoesNotExist:
            print(f"No valid TaxYear objects for entered year: {year}")
            return None

        return TotalPensionCompanySummaryFile.create(tax_year, "system")
