from eskat.models import ImportedKasMandtal
from eskat.models import get_kas_mandtal_model
from kas.models import Person, PersonTaxYear, TaxYear
from worker.models import job_decorator


@job_decorator
def import_mandtal(job):
    year = job.arguments['year']
    tax_year = TaxYear.objects.get(year=year)
    ImportedKasMandtal.import_year(year)

    for item in get_kas_mandtal_model().objects.filter(skatteaar=year):

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
        job.result = {'number_of_elements_updated': 200}
