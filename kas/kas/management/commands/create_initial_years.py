from django.core.management.base import BaseCommand
from kas.models import TaxYear


class Command(BaseCommand):
    help = 'Creates the initial years used in the project (2018, 2019, 2020)'

    def handle(self, *args, **options):

        for year in (2018, 2019, 2020):
            TaxYear.objects.update_or_create(year=year)
