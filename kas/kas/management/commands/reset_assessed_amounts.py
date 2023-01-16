from kas.models import PolicyTaxYear, TaxYear
from django.core.management.base import BaseCommand
from django.db.models import Q, F


class Command(BaseCommand):
    """
    Searches for policies, where the assessed_amount == prefilled_amount_edited or
    prefilled_amount, AND where the taxable number_of_days < days_in_year.
    Passing the tag --execute resets the assessed amount to assessed_amount=None, and
    runs the get_base_calculation_amount() function.
    The motivation for this is a case, where the
    prefilled_amount_edited/prefilled_amount was copied into assessed_amount, while the
    taxable number_of_days < days_in_year meant that the prefilled_amount should be
    adjusted for days in year. When copied into assessed-amount, this adjustment never
    happened, leading to an incorrect sum usedfor tax calculations.
    """

    help = """
    Searches for policies, where the assessed_amount == prefilled_amount_edited or 
    prefilled_amount, AND where the taxable number_of_days < days_in_year.
    Passing the tag --execute resets the assessed amount to assessed_amount=None, and
    runs the get_base_calculation_amount() function.

    Returns:
        Running as-is will return a list of [PolicyTaxYear.pk], for PolicyTaxYears that
        fullfill the criteria.

    Tags:
        --execute : Sets assessed_amount=None and
        base_calculation_amount=get_base_calculation_amount() for each PolicyTaxYear
        that fullfills the criteria.
    """

    def add_arguments(self, parser):

        parser.add_argument(
            "--execute",
            action="store_true",
            help=" For each policy found, set assessed_amount=None and base_calculation_amount=get_base_calculation_amount()",
        )

    def handle(self, *args, **options) -> None:
        policytaxyear_pk_list = []

        # Create dict of days in year, since this can't be queried in the ORM
        year_days = {}
        for taxyear in TaxYear.objects.all():
            year_days[taxyear.year] = taxyear.days_in_year

        for year, days in year_days.items():
            policytaxyears = PolicyTaxYear, objects.filter(
                Q(assessed_amount=F("prefilled_amount_edited"))
                | Q(assessed_amount=F("prefilled_amount")),
                Q(person_tax_year__tax_year__year=year)
                & Q(person_tax_year__number_of_days__lt=days),
                Q(active=True),
            ).exclude(assessed_amount=None)
            for policy in policytaxyears:
                assert (
                    policy.assessed_amount == policy.prefilled_amount_edited
                    or policy.assessed_amount == policy.prefilled_amount
                ), f"Policy with pk={policy.pk} has (assessed_amount != prefilled_amount_edited) or (assessed_amount != prefilled_amount AND prefilled_amount_edited = None)"
                assert (
                    policy.person_tax_year.tax_year.number_of_days
                    < policy.person_tax_year.tax_year.days_in_year
                ), f"Policy with pk={policy.pk} has (number_of_days>=days_in_year)"
                policytaxyear_pk_list.append(policy.pk)
                if options["execute"]:
                    policy.assessed_amount = None
                    policy.base_calculation_amount = (
                        policy.get_base_calculation_amount()
                    )
                    policy._change_reason = "Reset af assessed_amount"
                    policy.save()

        print(policytaxyear_pk_list)

        return
