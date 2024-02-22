from django.core.management.base import BaseCommand

from kas.models import TaxYear


class Command(BaseCommand):
    help = "Creates the initial years used in the project (2018, 2019, 2020, 2021)"

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

    def handle(self, *args, **options):
        for year in (2018, 2019, 2020, 2021):
            year_part = "selvangivelse"

            # Older years should default to genoptagelsesperiode
            if year < 2021:
                year_part = "genoptagelsesperiode"

            TaxYear.objects.update_or_create(
                year=year,
                defaults={
                    "year_part": year_part,
                    "rate_text_for_transactions": self.rate_text % {"year": year},
                },
            )
