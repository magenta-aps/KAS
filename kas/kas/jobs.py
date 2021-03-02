from django.forms.models import model_to_dict
from eskat.models import ImportedKasMandtal
from eskat.models import get_kas_mandtal_model
from kas.models import Person, PersonTaxYear, TaxYear


def migrate_mandtal(year):

    tax_year = TaxYear.objects.get(year=year)
    ImportedKasMandtal.import_year(year)

    for item in get_kas_mandtal_model().objects.filter(skatteaar=year):

        (person, created) = Person.objects.get_or_create(
            cpr=item.cpr,
            defaults={}
        )

        person_tax_year_data = {
            'person': person,
            'tax_year': tax_year,
            'number_of_days': item.skattedage,
            'municipality_name': item.kommune,
            'municipality_code': item.kommune_no,
            'address_line_1': item.adresselinje1,
            'address_line_2': item.adresselinje2,
            'address_line_3': item.adresselinje3,
            'address_line_4': item.adresselinje4,
            'address_line_5': item.adresselinje5,
            'full_address': item.fuld_adresse,
            'fully_tax_liable': item.skatteomfang is not None and item.skatteomfang.lower() == 'fuld skattepligtig',
        }

        try:
            existing = PersonTaxYear.objects.get(
                tax_year=tax_year,
                person=person
            )
            existing_dict = model_to_dict(existing)
            del existing_dict['id']
            new_dict = {**person_tax_year_data, 'person': person.id, 'tax_year': tax_year.id}
            if existing_dict != new_dict:
                for k, v in person_tax_year_data.items():
                    setattr(existing, k, v)
                existing._change_reason = "Updated by import"
                existing.save()

        except PersonTaxYear.DoesNotExist:
            person_tax_year = PersonTaxYear(**person_tax_year_data)
            person_tax_year.change_reason = "Created by import"
            person_tax_year.save()
