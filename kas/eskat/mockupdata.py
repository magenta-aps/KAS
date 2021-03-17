from eskat.models import MockModels
from kas.management.commands.import_default_pension_companies import Command as PensionCompanyImport
from kas.models import TaxYear

import uuid


unique_res_counter = 0
cpr_counter = 1111810000


def next_unique_res():
    global unique_res_counter
    unique_res_counter = unique_res_counter + 1
    return '%010d' % (unique_res_counter)


def next_unique_cpr():
    global cpr_counter
    cpr_counter = cpr_counter + 1
    return cpr_counter


def person_uuid(cpr, year):
    return str(uuid.uuid5(
        uuid.NAMESPACE_URL,
        'https://test.kas.aka.nanoq.gl/mockupdata/cpr/%s/%s' % (cpr, year)
    ))


def r75_sekvens_uuid(cpr, year, pkt, res):
    return str(uuid.uuid5(
        uuid.NAMESPACE_URL,
        'https://test.aka.nanoq.gl/mockupdata/r75/sekvens/%s/%s/%s/%s' % (cpr, year, res, pkt)
    ))


def r75_indeks_uuid(cpr, year, pkt, res):
    return str(uuid.uuid5(
        uuid.NAMESPACE_URL,
        'https://test.aka.nanoq.gl/mockupdata/r75/indekx/%s/%s/%s/%s' % (cpr, year, res, pkt)
    ))


def create_person(
    name: str,
    cpr: str = None,
    person_extra: dict = {},
    person_years: dict = {},
    policies=[]
):

    if cpr is None:
        cpr = next_unique_cpr()

    # TODO: A better way to mock municipality data
    # TODO: A way to add bank data
    # TODO: More realistict addresses
    person_defaults = {
        "cpr": cpr,
        "bank_reg_nr": None,
        "bank_konto_nr": None,
        "kommune_no": 32,
        "kommune": "Sermersooq",
        "navn": name,
        "adresselinje1": None,
        "adresselinje2": name + "adresse 1",
        "adresselinje3": None,
        "adresselinje4": "3900 Sermersooq",
        "adresselinje5": None,
        "skatteomfang": "fuld skattepligtig",
        **person_extra
    }

    for policy in policies:
        if "res" not in policy:
            policy["res"] = "6471"

        if "pkt" not in policy:
            policy["pkt"] = next_unique_res()

        for year, beloeb in policy["years"].items():
            # Make sure we create a mandtal entry for the person for this year
            if int(year) not in person_years:
                person_years[year] = {}

            policy_data = {
                "pt_census_guid": person_uuid(cpr, year),
                "r75_ctl_sekvens_guid": r75_sekvens_uuid(cpr, year, policy["res"], policy["pkt"]),
                "r75_ctl_indeks_guid": r75_indeks_uuid(cpr, year, policy["res"], policy["pkt"]),
                "idx_nr": 5500121,
                "dato": "%04d0116" % (year),
                "pkt": policy["pkt"],
                "res": policy["res"],
                "beloeb": beloeb,
            }

            MockModels.MockR75PrivatePension.objects.update_or_create(
                defaults=policy_data,
                tax_year=year,
                cpr=cpr,
                pkt=policy["pkt"],
                res=policy["res"],
            )

    for year, person_year_data in person_years.items():
        # Make sure we have a taxyear for the given year
        taxyear, _ = TaxYear.objects.get_or_create(year=year)

        persondata = person_defaults.copy()
        persondata.update(person_year_data)

        persondata["pt_census_guid"] = person_uuid(cpr, year)

        if "skattedage" not in persondata:
            persondata["skattedage"] = taxyear.days_in_year

        MockModels.MockKasMandtal.objects.update_or_create(
            defaults=persondata,
            skatteaar=year,
            cpr=cpr,
        )


def import_default_mockup_data():
    # Make sure we have pension company data
    PensionCompanyImport().handle()

    # Clean out existing mockup data
    MockModels.MockR75PrivatePension.objects.all().delete()
    MockModels.MockKasMandtal.objects.all().delete()

    create_person(
        "Borger med 0 afkast",
        policies=[
            {"res": 6471, "years": {
                2018: 0,
                2019: 0,
                2020: 0
            }}
        ]
    )

    create_person(
        "Borger med ikke dækkende negativt afkast",
        policies=[
            {"res": 6471, "years": {
                2018: -2000,
                2019: 1000,
                2020: 2500,
            }}
        ]
    )

    create_person(
        "Borger med dækkende negativt afkast",
        policies=[
            {"res": 6471, "years": {
                2018: -5000,
                2019: 1000,
                2020: 2500,
            }}
        ]
    )

    create_person(
        "Borger uden negativt afkast",
        policies=[
            {"res": 6471, "years": {
                2018: 1000,
                2019: 2000,
                2020: 3000,
            }}
        ]
    )

    create_person(
        "Borger med police hos PFA + andre",
        policies=[
            {"res": 6471, "years": {
                2018: 1000,
                2019: 2000,
                2020: 3000,
            }},
            # 55143315 is PFA
            {"res": 55143315, "years": {
                2018: 1000,
                2019: 2000,
                2020: 3000,
            }},
        ]
    )

    create_person(
        "Borger uden policer",
        person_years={2018: {}, 2019: {}, 2020: {}},
        policies=[]
    )

    create_person(
        "Borger med kun positivt afkast i 2020",
        policies=[
            {"res": 6471, "years": {
                2020: 3000,
            }},
        ]
    )

    create_person(
        "Borger med kun negativt afkast i 2020",
        policies=[
            {"res": 6471, "years": {
                2020: -3000,
            }},
        ]
    )

    create_person(
        "Borger der ikke er fuldt skattepligtig",
        person_extra={"skatteomfang": "ikke fuld skattepligtig"},
        policies=[
            {"res": 6471, "years": {
                2018: 1000,
                2019: 2000,
                2020: 3000,
            }},
        ]
    )

    create_person(
        "Borger der ikke er skattepligtig hele 2020",
        person_extra={"skatteomfang": "ikke fuld skattepligtig"},
        person_years={2020: {"skattedage": 150}},
        policies=[
            {"res": 6471, "years": {
                2018: 1000,
                2019: 2000,
                2020: 3000,
            }},
        ]
    )

    create_person(
        "Borger med negativt afkast påvirket af antal dage",
        person_extra={"skatteomfang": "ikke fuld skattepligtig"},
        person_years={2019: {"skattedage": 73}},
        policies=[
            {"res": 6471, "years": {
                2019: -5000,
                2020: 3000,
            }},
        ]
    )

    create_person(
        "Borger med negativt afkast og nuværende år påvirket af antal dage",
        person_extra={"skatteomfang": "ikke fuld skattepligtig"},
        person_years={2019: {"skattedage": 73}, 2020: {"skattedage": 146}},
        policies=[
            {"res": 6471, "years": {
                2019: -5000,
                2020: 3000,
            }},
        ]
    )

    create_person(
        "Borger med negativt afkast for mere end 10 år siden",
        person_extra={"skatteomfang": "ikke fuld skattepligtig"},
        person_years={2018: {"skattedage": 73}, 2019: {"skattedage": 146}},
        policies=[
            {"res": 6471, "years": {
                2009: -100000,
                2018: 1000,
                2019: 1000,
                2020: 1000,
            }},
        ]
    )

    # Kan logges ind på test med certifikat fra
    # https://www.nets.eu/dk-da/kundeservice/nemid-tjenesteudbyder/Documents/TU-pakken/Tools/Testcertifikater/OCES%20II/MOCES_cpr_gyldig_2022.p12
    # Password: Test1234
    # Dette er ikke hemmeligt
    create_person(
        "Person som kan logges ind på test",
        cpr='1802602810',
        policies=[
            {"pkt": 6471, "years": {
                2018: 1000,
                2019: 2000,
                2020: 3000,
            }},
            {"pkt": 55143315, "years": {
                2018: -1000,
                2019: -2500,
                2020: 3000,
            }},
        ]
    )

    create_person(
        "Borger med negativt afkast fordelt over flere år",
        policies=[
            {"res": 6471, "years": {
                2018: -600,
                2019: -1000,
                2020: 3000,
            }},
        ]
    )
