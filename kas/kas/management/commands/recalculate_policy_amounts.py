from django.core.management import BaseCommand
from django.db.models import Count
from eskat.models import ImportedR75PrivatePension
from kas.models import PolicyTaxYear


class Command(BaseCommand):
    help = "Updates prefilled_amount for PolixyTaxYears with more than 1 R75 entry"

    def add_arguments(self, parser):
        parser.add_argument("year", type=int)

    def handle(self, *args, **options):
        year = options["year"]
        qs = ImportedR75PrivatePension.objects.values("cpr", "res", "ktd")
        qs = qs.filter(tax_year=year)
        qs = qs.annotate(number_per_policy=Count("r75_ctl_sekvens_guid"))
        qs = qs.filter(number_per_policy__gt=1)
        for item in qs.iterator():
            try:
                policy_tax_year = PolicyTaxYear.objects.get(
                    person_tax_year__person__cpr=item["cpr"],
                    person_tax_year__tax_year__year=year,
                    pension_company__res=item["res"],
                    policy_number=item["ktd"],
                )
                policy_tax_year.recalculate_from_r75()
            except PolicyTaxYear.DoesNotExist:
                pass
