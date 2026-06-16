import numpy as np
from django.conf import settings
from django.core.management import BaseCommand
from pandas import DataFrame, Series

from kas.models import PensionCompany, PolicyTaxYear


class Command(BaseCommand):
    help = """
        Calculates a summarized overview for all PensionCompanies
        and returns a .csv table
    """

    def add_arguments(self, parser):
        parser.add_argument("year", type=int)

    def handle(self, *args, **options):
        year = options["year"]
        pensioncompanies = PensionCompany.objects.filter(
            policytaxyear__person_tax_year__tax_year__year=year,
        ).distinct()
        dtypes = {
            "Pensionskasse": str,
            "Antal": float,
            "Afkast": float,
            "Modregnet negativt afkast tidl. år": float,
            "Beregningsgrundlag": float,
            "Forudbetaling": float,
            "Kapitalafkastskat": float,
        }
        columns = list(dtypes.keys())
        df = DataFrame(
            np.nan,
            index=range(len(pensioncompanies)),
            columns=columns,
        ).astype(dtypes)

        for idx, pc in enumerate(pensioncompanies):
            ptys = PolicyTaxYear.objects.filter(
                pension_company=pc,
                person_tax_year__tax_year__year=year,
            )
            pty_calcs = [
                {
                    "preliminary_paid_amount": pty.preliminary_paid_amount,
                    "foreign_paid_amount_actual": pty.foreign_paid_amount_actual,
                    **pty.get_calculation(),
                }
                for pty in ptys
            ]
            if not pty_calcs:
                continue

            pc_df = DataFrame(pty_calcs)
            pc_df["prepaid"] = (
                pc_df["preliminary_paid_amount"] + pc_df["foreign_paid_amount_actual"]
            )
            pc_df.loc[
                pc_df["tax_with_deductions"] < settings.TRANSACTION_INDIFFERENCE_LIMIT,
                "tax_with_deductions",
            ] = 0
            row = Series(
                {
                    "Pensionskasse": pc.name,
                    "Antal": ptys.values("person_tax_year__person").distinct().count(),
                    "Afkast": pc_df["year_adjusted_amount"].sum(),
                    "Modregnet negativt afkast tidl. år": pc_df[
                        "used_negative_return"
                    ].sum(),
                    "Beregningsgrundlag": pc_df["taxable_amount"].sum(),
                    "Forudbetaling": pc_df["prepaid"].sum(),
                    "Kapitalafkastskat": pc_df["tax_with_deductions"].sum(),
                }
            )
            df.loc[idx] = row
        df.dropna(how="all", inplace=True)
        df.to_excel(
            settings.MEDIA_ROOT
            + "pensioncompany_summary/pensioncompany_summary_list_"
            + str(year)
            + ".xlsx",
            index=False,
        )
