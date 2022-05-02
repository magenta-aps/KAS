from eskat.mockupdata import generate_persons
from eskat.models import MockModels
from worker.job_registry import resolve_job_function
from worker.models import job_decorator, Job
from kas.models import TaxYear
from django.core.management import call_command
from django.conf import settings
from django.apps import apps
from django.db.models.deletion import ProtectedError


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
    for model in apps.all_models.get('kas').values():
        delete_protected(model.objects.all())

    # Clean out existing mockup data
    MockModels.MockR75Idx4500230.objects.all().delete()
    MockModels.MockKasMandtal.objects.all().delete()
    # Make sure we have pension company data
    call_command('import_default_pension_companies')
    for year in (2018, 2019, 2020, 2021):
        year_part = 'selvangivelse'

        # Older years should default to genoptagelsesperiode
        if year < 2021:
            # Add selvangivelse og slutopgørelser?
            year_part = 'genoptagelsesperiode'

        TaxYear.objects.update_or_create(
            year=year,
            defaults={
                'year_part': year_part,
                'rate_text_for_transactions': rate_text % {'year': year}
            }
        )

    # This generates mock persons
    generate_persons()

    for tax_year in TaxYear.objects.all():
        # import R75
        mandtal_job = Job.schedule_job(
            function=resolve_job_function('kas.jobs.import_mandtal'),
            job_type='ImportMandtalJob',
            created_by=job.created_by,
            parent=job,
            depends_on=job,
            job_kwargs={'year': tax_year.year}
        )
        # import mandtal
        Job.schedule_job(
            function=resolve_job_function('kas.jobs.import_r75'),
            job_type='ImportR75Job',
            created_by=job.created_by,
            parent=job,
            depends_on=mandtal_job,
            job_kwargs={'year': tax_year.year}
        )
