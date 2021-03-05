from eskat.models import ImportedKasMandtal
from eskat.models import get_kas_mandtal_model
from kas.models import Person, PersonTaxYear, TaxYear
from worker.models import job_decorator


@job_decorator
def import_mandtal(job):
    year = job.arguments['year']
    tax_year = TaxYear.objects.get(year=year)
    number_of_progress_segments = 2
    progress_factor = 1 / number_of_progress_segments
    ImportedKasMandtal.import_year(year, job, progress_factor, 0)

    qs = get_kas_mandtal_model().objects.filter(skatteaar=year)
    count = qs.count()
    progress_start = 0.5

    for i, item in enumerate(qs):

        person_data = {
            'cpr': item.cpr,
            'municipality_name': item.kommune,
            'municipality_code': item.kommune_no,
            'address_line_1': item.adresselinje1,
            'address_line_2': item.adresselinje2,
            'address_line_3': item.adresselinje3,
            'address_line_4': item.adresselinje4,
            'address_line_5': item.adresselinje5,
            'full_address': item.fuld_adresse,
        }

        person = Person.update_or_create(person_data, 'cpr')

        person_tax_year_data = {
            'person': person,
            'tax_year': tax_year,
            'number_of_days': item.skattedage,
            'fully_tax_liable': item.skatteomfang is not None and item.skatteomfang.lower() == 'fuld skattepligtig',
        }

        PersonTaxYear.update_or_create(person_tax_year_data, 'tax_year', 'person')
        job.set_progress_pct(progress_start + (i / count) * (100 * progress_factor))
        job.result = {'number_of_elements_updated': 200}
