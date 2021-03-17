import itertools
from random import randint

from django.core.management.base import BaseCommand
from kas.models import PensionCompany, Person, PersonTaxYear, PolicyTaxYear, TaxYear


class Command(BaseCommand):
    help = 'Populates database with some dummy data'

    def handle(self, *args, **options):

        pension_companies = [
            PensionCompany.objects.get_or_create(res=10000000 + i, name=f"Pension Company {i}")[0]
            for i in range(1, 5)
        ]

        tax_years = [
            TaxYear.objects.get_or_create(year=year)[0]
            for year in range(2016, 2022)
        ]

        persons = [
            Person.objects.get_or_create(cpr=f"010101{str(i).zfill(4)}")[0]
            for i in range(1, 5)
        ]

        person_tax_years = [
            PersonTaxYear.objects.get_or_create(person=person, tax_year=tax_year, defaults={'number_of_days': tax_year.days_in_year})[0]
            for (person, tax_year) in itertools.product(persons, tax_years)
        ]

        p = 0
        for person_tax_year in person_tax_years:
            for pension_company in pension_companies:
                p += 1
                policy_number = f"{person_tax_year.person.cpr}-{person_tax_year.tax_year.year}-{p}"
                policy_tax_year, c = PolicyTaxYear.objects.get_or_create(
                    person_tax_year=person_tax_year,
                    pension_company=pension_company,
                    policy_number=policy_number,
                    defaults={
                        'prefilled_amount': randint(0, 50000)
                    }
                )
                policy_tax_year.recalculate()
