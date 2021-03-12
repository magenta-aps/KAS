from eskat.models import ImportedKasMandtal, ImportedR75PrivatePension
from eskat.models import get_kas_mandtal_model, get_r75_private_pension_model
from kas.models import Person, PersonTaxYear, TaxYear, PolicyTaxYear, PensionCompany
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


@job_decorator
def import_r75(job):
    year = job.arguments['year']
    tax_year = TaxYear.objects.get(year=year)
    number_of_progress_segments = 2
    progress_factor = 1 / number_of_progress_segments
    (r75_created, r75_updated) = ImportedR75PrivatePension.import_year(year, job, progress_factor, 0)

    progress_start = 0.5
    persons_created = 0
    person_tax_years_created = 0
    (policies_created, policies_updated) = (0, 0)

    qs = get_r75_private_pension_model().objects.filter(tax_year=year)
    count = qs.count()
    for i, item in enumerate(qs):

        person, c = Person.objects.get_or_create(cpr=item.cpr)
        if c:
            persons_created += 1
        person_tax_year, c = PersonTaxYear.objects.get_or_create(person=person, tax_year=tax_year)
        if c:
            person_tax_years_created += 1

        res = int(item.res)
        pension_company, c = PensionCompany.objects.get_or_create(**{'res': res})

        policy_data = {
            'person_tax_year': person_tax_year,
            'pension_company': pension_company,
            'policy_number': item.pkt,
            'prefilled_amount': item.beloeb,
        }
        (policy_tax_year, status) = PolicyTaxYear.update_or_create(policy_data, 'person_tax_year', 'pension_company', 'policy_number')

        if status in (PersonTaxYear.CREATED, PersonTaxYear.UPDATED):
            policy_tax_year.recalculate()
            if status == PersonTaxYear.CREATED:
                policies_created += 1
            elif status == PersonTaxYear.UPDATED:
                policies_updated += 1

        job.set_progress_pct(progress_start + (i / count) * (100 * progress_factor))

    job.result = {'summary': [
        {'label': 'Rå R75-objekter', 'value': [
            {'label': 'Tilføjet', 'value': r75_created},
            {'label': 'Opdateret', 'value': r75_updated}
        ]},
        {'label': 'Policeskatteår-objekter', 'value': [
            {'label': 'Tilføjet', 'value': policies_created},
            {'label': 'Opdateret', 'value': policies_updated}
        ]}
    ]}
