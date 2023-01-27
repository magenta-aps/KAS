from django.core.management.base import BaseCommand

from kas.models import FinalSettlement


class Command(BaseCommand):
    help = "List taxpayers who received a final settlement with payable KAS"

    def add_arguments(self, parser):
        parser.add_argument("year", type=int)

    def handle(self, *args, **options):

        year = options["year"]
        print(";".join(["CPR", "Navn", "KAS", "Skattepligtigt beløb"]))
        for final_settlement in FinalSettlement.objects.filter(
            person_tax_year__tax_year__year=year, invalid=False
        ):
            transaction = final_settlement.get_transaction()
            person_tax_year = final_settlement.person_tax_year
            if transaction is not None and transaction.amount > 100:
                tax_calculations = (
                    pty.get_calculation()
                    for pty in person_tax_year.policytaxyear_set.all()
                )
                taxable = sum(tc["taxable_amount"] for tc in tax_calculations)
                print(
                    ";".join(
                        [
                            final_settlement.person_tax_year.person.cpr,
                            final_settlement.person_tax_year.person.name,
                            transaction.amount,
                            taxable,
                        ]
                    )
                )
