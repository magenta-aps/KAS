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
    mandtal_created, mandtal_updated = ImportedKasMandtal.import_year(year, job, progress_factor, 0)

    qs = get_kas_mandtal_model().objects.filter(skatteaar=year)
    count = qs.count()
    progress_start = 0.5
    (persons_created, persons_updated) = (0, 0)
    (persontaxyears_created, persontaxyears_updated) = (0, 0)

    for i, item in enumerate(qs.iterator()):

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

        (person, status) = Person.update_or_create(person_data, 'cpr')
        if status == Person.CREATED:
            persons_created += 1
        elif status == Person.UPDATED:
            persons_updated += 1

        person_tax_year_data = {
            'person': person,
            'tax_year': tax_year,
            'number_of_days': item.skattedage,
            'fully_tax_liable': item.skatteomfang is not None and item.skatteomfang.lower() == 'fuld skattepligtig',
        }

        (person_tax_year, status) = PersonTaxYear.update_or_create(person_tax_year_data, 'tax_year', 'person')
        if status == PersonTaxYear.CREATED:
            persontaxyears_created += 1
        elif status == PersonTaxYear.UPDATED:
            persontaxyears_updated += 1

        job.set_progress_pct(progress_start + (i / count) * (100 * progress_factor))

    job.result = {'summary': [
        {'label': 'Rå Mandtal-objekter', 'value': [
            {'label': 'Tilføjet', 'value': mandtal_created},
            {'label': 'Opdateret', 'value': mandtal_updated}
        ]},
        {'label': 'Person-objekter', 'value': [
            {'label': 'Tilføjet', 'value': persons_created},
            {'label': 'Opdateret', 'value': persons_updated}
        ]},
        {'label': 'Personskatteår-objekter', 'value': [
            {'label': 'Tilføjet', 'value': persontaxyears_created},
            {'label': 'Opdateret', 'value': persontaxyears_updated}
        ]}
    ]}
