from uuid import uuid4

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from eskat.mockupdata import generate_persons
from eskat.models import (
    MockModels,
    get_kas_beregninger_x_model,
    ImportedKasBeregningerX,
    MockKasBeregningerX,
)
from kas.models import TaxYear
from worker.job_registry import resolve_job_function
from worker.models import job_decorator, Job

from kas.models import PersonTaxYear

rate_text = (
    "Pigisanit pissarsiat ilaasa akileraaruserneqartarnerat pil-\n"
    "lugu Inatsisartut Inatsisaat nr. 37, 23. november 2017-\n"
    "imeersoq naapertorlugu ukiumut isertitaqarfiusumut\n"
    "{year}-mut akileraarutissat sinnerinut akiligassat (KAS).\n"
    "Akiliinermi allaffissami allaguk KAS{year} kiisalu illit\n"
    "inuup nr.-mut\n"
    "\n"
    "Restkapitalafkastskat (KAS) for indkomståret {year} i\n"
    "henhold til Inatsisartutlov nr. 37 af 23. november 2017\n"
    "om beskatning af visse kapitalafkast.\n"
    "Ved indbetaling, skriv venligst KAS{year} samt\n"
    "dit cpr. nr. i tekstfeltet.\n"
)


def delete_protected(objects):
    """
    recursively delete all objects
    :param objects:
    :return:
    """
    try:
        objects.delete()
    except ProtectedError as e:
        for o in e.protected_objects:
            # protected objects is a set not a queryset
            delete_protected(o)
        delete_protected(objects)


@job_decorator
def generate_sample_data(job):
    if settings.ENVIRONMENT != "development":
        raise Exception("Will only generate sample data in development environments")

    # delete all data in kas
    for model in apps.all_models.get("kas").values():
        delete_protected(model.objects.all())

    # Clean out existing mockup data
    MockModels.MockR75Idx4500230.objects.all().delete()
    MockModels.MockKasMandtal.objects.all().delete()
    MockKasBeregningerX.objects.all().delete()
    # Make sure we have pension company data
    call_command("import_default_pension_companies")
    for year in (2018, 2019, 2020, 2021):
        year_part = "selvangivelse"

        # Older years should default to genoptagelsesperiode
        if year < 2021:
            # Add selvangivelse og slutopgørelser?
            year_part = "genoptagelsesperiode"

        TaxYear.objects.update_or_create(
            year=year,
            defaults={
                "year_part": year_part,
                "rate_text_for_transactions": rate_text % {"year": year},
            },
        )

    # This generates mock persons
    generate_persons()

    for tax_year in TaxYear.objects.all():
        # import R75
        mandtal_job = Job.schedule_job(
            function=resolve_job_function("kas.jobs.import_mandtal"),
            job_type="ImportMandtalJob",
            created_by=job.created_by,
            parent=job,
            depends_on=job,
            job_kwargs={"year": tax_year.year},
        )
        # import mandtal
        Job.schedule_job(
            function=resolve_job_function("kas.jobs.import_r75"),
            job_type="ImportR75Job",
            created_by=job.created_by,
            parent=job,
            depends_on=mandtal_job,
            job_kwargs={"year": tax_year.year},
        )
    # Generate mockkas beregninger
    for tax_year in settings.LEGACY_YEARS:
        for cpr in [
            "0101570010",
            "0101005089",
            "0103897769",
            "1509814844",
            "2512474856",
        ]:
            #  Ensure mandtal for the cpr
            MockModels.MockKasMandtal.objects.update_or_create(
                pt_census_guid=uuid4(), cpr=cpr, skatteaar=tax_year
            )
            # Create kas_beregning for cpr and year
            MockKasBeregningerX.objects.update_or_create(
                skatteaar=tax_year,
                pt_census_guid=uuid4(),
                pension_crt_calc_guid=uuid4(),
                cpr=cpr,
                reg_date=timezone.now(),
                capital_return_tax=100,
            )


@job_decorator
def importere_kas_beregninger_for_legacy_years(job):
    try:
        year = TaxYear.objects.get(pk=job.arguments["year_pk"])
    except TaxYear.DoesNotExist:
        raise Exception("skatteår eksisterer ikke")

    if year.year not in settings.LEGACY_YEARS:
        raise Exception("Kun import af tidligere år (2018/2019) er understøttet")

    source_model = get_kas_beregninger_x_model().objects.filter(skatteaar=year.year)
    fundet_beregninger = source_model.count()
    gemte_beregninger = 0
    for beregning in source_model.values(
        "cpr", "pension_crt_calc_guid", "capital_return_tax", "skatteaar"
    ):
        person_tax_year = PersonTaxYear.objects.get(
            person__cpr=beregning["cpr"],
            tax_year__year=beregning["skatteaar"],
        )

        try:
            imported_beregning = ImportedKasBeregningerX.objects.get(
                person_tax_year=person_tax_year,
            )
        except ImportedKasBeregningerX.DoesNotExist:
            imported_beregning = ImportedKasBeregningerX(
                **beregning, person_tax_year=person_tax_year
            )
            imported_beregning._change_reason = "Created by import"
        else:
            if imported_beregning.capital_return_tax != beregning["capital_return_tax"]:
                imported_beregning.capital_return_tax = beregning["capital_return_tax"]
                imported_beregning._change_reason = "Updated by import"
            else:
                continue
        imported_beregning.save()
        gemte_beregninger += 1

    job.result = {
        "message": f"Fandt {fundet_beregninger} beregninger og gemte {gemte_beregninger} beregninger"
    }
