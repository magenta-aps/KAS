from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from eskat.jobs import generate_sample_data
from eskat.jobs import importere_kas_beregninger_for_legacy_years
from kas.jobs import import_r75
from kas.jobs import import_mandtal
from kas.jobs import generate_pseudo_settlements_and_transactions_for_legacy_years
from worker.models import Job
from django.conf import settings


class Command(BaseCommand):
    help = "Populates database with some dummy data"

    def handle(self, *args, **options):
        if settings.ENVIRONMENT in ("production", "staging"):
            raise Exception(f"Will not create dummy data in {settings.ENVIRONMENT}")

        admin_user, _ = get_user_model().objects.get_or_create(username="admin")

        prev = Job.schedule_job(
            generate_sample_data,
            "GenerateSampleData",
            admin_user,
        )

        # Run jobs specified in https://git.magenta.dk/gronlandsprojekter/kas/-/merge_requests/355
        for year in [2018, 2019]:

            # Import mandtal
            prev = Job.schedule_job(
                import_mandtal,
                "ImportMandtalJob",
                admin_user,
                job_kwargs={
                    "year": year,
                },
                depends_on=prev,
            )

            # Import af data fra R75 - 2019
            prev = Job.schedule_job(
                import_r75,
                "ImportR75Job",
                admin_user,
                job_kwargs={
                    "year": year,
                },
                depends_on=prev,
            )

            # Importere kas beregninger for tidligere år (2018/2019)
            prev = Job.schedule_job(
                importere_kas_beregninger_for_legacy_years,
                "ImportLegacyCalculations",
                admin_user,
                job_kwargs={
                    "year": year,
                },
                depends_on=prev,
            )

        # Generering af pseudo slutopgørelser (2018/2019)
        Job.schedule_job(
            generate_pseudo_settlements_and_transactions_for_legacy_years,
            "GeneratePseudoFinalSettlements",
            admin_user,
            depends_on=prev,
        )
