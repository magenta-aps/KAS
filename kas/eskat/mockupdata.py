import uuid

from eskat.models import MockModels
from kas.models import TaxYear

unique_res_counter = 0
fictitious_cprs = [  # noqa
    # if you need a fictive cpr number use one of these and remove it from the list
    "0902410058",
    "2509474829",
    "1105801064",
    "3105841026",
    "0101570088",
    "2505811057",
    "0601980010",
    "1111111113",
    "0101005038",
    "1111111111",
    "2301175038",
    "1111111112",
    "0106664862",
    "0312600013",
    "1102640019",
    "0112977724",
    "0103232759",
    "0904410039",
    "0112947728",
    "1502122777",
    "0707610042",
]


def next_unique_res():
    global unique_res_counter
    unique_res_counter = unique_res_counter + 1
    return "%010d" % (unique_res_counter)


def person_uuid(cpr, year):
    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            "https://test.kas.aka.nanoq.gl/mockupdata/cpr/%s/%s" % (cpr, year),
        )
    )


def r75_sekvens_uuid(cpr, year, ktd, res):
    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            "https://test.aka.nanoq.gl/mockupdata/r75/sekvens/%s/%s/%s/%s"
            % (cpr, year, res, ktd),
        )
    )


def r75_indeks_uuid(cpr, year, ktd, res):
    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            "https://test.aka.nanoq.gl/mockupdata/r75/index/%s/%s/%s/%s"
            % (cpr, year, res, ktd),
        )
    )


def create_person(
    name: str,
    cpr: str,
    adresselinje1: str = None,
    adresselinje2: str = "Mut aqqut 1",
    adresselinje3: str = None,
    adresselinje4: str = "3900 Nuuk",
    adresselinje5: str = None,
    person_extra: dict = None,
    person_years: dict = None,
    policies=[],
):
    if person_extra is None:
        person_extra = {}
    if person_years is None:
        person_years = {}
    # TODO: A better way to mock municipality data
    # TODO: A way to add bank data
    # TODO: More realistict addresses
    person_defaults = {
        "cpr": cpr,
        "bank_reg_nr": None,
        "bank_konto_nr": None,
        "kommune_no": 956,
        "kommune": "Sermersooq",
        "navn": name,
        "adresselinje1": adresselinje1,
        "adresselinje2": adresselinje2,
        "adresselinje3": adresselinje3,
        "adresselinje4": adresselinje4,
        "adresselinje5": adresselinje5,
        "skatteomfang": "fuld skattepligtig",
        **person_extra,
    }
    person_defaults["fuld_adresse"] = ", ".join(
        [
            person_defaults[x]
            for x in (
                "adresselinje1",
                "adresselinje2",
                "adresselinje3",
                "adresselinje4",
                "adresselinje5",
            )
            if person_defaults[x]
        ]
    )

    for policy in policies:
        if "res" not in policy:
            policy["res"] = "19676889"

        if "ktd" not in policy:
            policy["ktd"] = next_unique_res()

        for year, beloeb in policy["years"].items():
            # Make sure we create a mandtal entry for the person for this year
            if int(year) not in person_years:
                person_years[year] = {}

            policy_data = {
                "pt_census_guid": person_uuid(cpr, year),
                # tax_year added below
                # cpr added below
                "r75_ctl_sekvens_guid": r75_sekvens_uuid(
                    cpr, year, policy["res"], policy["ktd"]
                ),
                "r75_ctl_indeks_guid": r75_indeks_uuid(
                    cpr, year, policy["res"], policy["ktd"]
                ),
                "idx_nr": 4500230,
                "res": policy["res"],
                "ktd": policy["ktd"],
                "ktt": "KTT",
                "kontotype": 22,
                "ibn": None,
                "esk": "ESK",
                "ejerstatuskode": 1,
                "indestaaende": 0,
                "renteindtaegt": beloeb,
                "r75_dato": "%04d0116" % (year),
            }

            MockModels.MockR75Idx4500230.objects.update_or_create(
                defaults=policy_data,
                tax_year=year,
                cpr=cpr,
                ktd=policy["ktd"],
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


def generate_persons():

    create_person(
        "Borger med 0 afkast",
        cpr="0101570010",
        adresselinje2="Imaneq 32A, 3. sal.",
        adresselinje4="3900 Nuuk",
        policies=[{"res": 19676889, "years": {2020: 0, 2021: 0}}],
    )

    create_person(
        "Borger med ikke dækkende negativt afkast",
        cpr="0101005089",
        adresselinje2="Imaneq 32A, 2. sal.",
        adresselinje4="3900 Nuuk",
        policies=[
            {
                "res": 19676889,
                "years": {
                    2020: 2500,
                    2021: 0,
                },
            }
        ],
    )

    create_person(
        "Borger med dækkende negativt afkast",
        cpr="0103897769",
        adresselinje2="Imaneq 32A, 1. sal.",
        adresselinje4="3900 Nuuk",
        policies=[{"res": 19676889, "years": {2020: 2500, 2021: 0}}],
    )

    create_person(
        "Borger uden negativt afkast",
        cpr="1509814844",
        adresselinje2="Imaneq 32A, 3. sal.",
        adresselinje4="3900 Nuuk",
        policies=[{"res": 19676889, "years": {2020: 3000, 2021: 0}}],
    )

    create_person(
        "Borger med police hos PFA + andre",
        cpr="2512474856",
        adresselinje2="Imaneq 32A, 2. sal.",
        adresselinje4="3900 Nuuk",
        policies=[
            {"res": 19676889, "years": {2020: 3000, 2021: 0}},
            # 55143315 is PFA
            {"res": 55143315, "years": {2020: 2000, 2021: 0}},
        ],
    )

    create_person(
        "Borger uden policer",
        cpr="2512484916",
        adresselinje2="Imaneq 32A, 1. sal.",
        adresselinje4="3900 Nuuk",
        person_years={2020: {}, 2021: {}},
        policies=[],
    )

    create_person(
        "Borger med kun positivt afkast i 2021",
        cpr="3105781007",
        adresselinje2="Imaneq 32A, 3. sal.",
        adresselinje4="3900 Nuuk",
        policies=[
            {
                "res": 19676889,
                "years": {
                    2021: 3000,
                },
            },
        ],
    )

    create_person(
        "Borger med kun negativt afkast i 2021",
        cpr="1105015018",
        adresselinje2="Imaneq 32A, 2. sal.",
        adresselinje4="3900 Nuuk",
        policies=[
            {
                "res": 19676889,
                "years": {
                    2021: -3000,
                },
            },
        ],
    )

    create_person(
        "Borger der ikke er fuldt skattepligtig",
        person_extra={"skatteomfang": "ikke fuld skattepligtig"},
        cpr="0708614866",
        adresselinje2="Imaneq 32A, 1. sal.",
        adresselinje4="3900 Nuuk",
        policies=[
            {
                "res": 19676889,
                "years": {
                    2020: 3000,
                    2021: 4000,
                },
            },
        ],
    )

    create_person(
        "Borger med 0 skattepligtige dage",
        cpr="0206025050",
        adresselinje3="Imaneq 32A, 3. sal.",
        adresselinje5="3900 Nuuk",
        person_years={2021: {"skattedage": 0}},
        policies=[
            {
                "res": 19676889,
                "years": {
                    2021: 3000,
                },
            },
        ],
    )

    create_person(
        "Borger der ikke er skattepligtig hele 2021",
        cpr="0101055035",
        adresselinje2="Imaneq 32A, 2. sal.",
        adresselinje4="3900 Nuuk",
        person_years={2021: {"skattedage": 150}},
        policies=[
            {
                "res": 19676889,
                "years": {
                    2020: 3000,
                    2021: 4000,
                },
            },
        ],
    )

    create_person(
        "Borger med negativt afkast påvirket af antal dage",
        cpr="0401570020",
        adresselinje2="Imaneq 32A, 1. sal.",
        adresselinje4="3900 Nuuk",
        person_years={2020: {"skattedage": 73}},
        policies=[
            {
                "res": 19676889,
                "years": {
                    2020: -5000,
                    2021: 1000,
                },
            },
        ],
    )

    create_person(
        "Borger med positivt afkast påvirket af antal dage",
        cpr="0401570805",
        adresselinje2="Imaneq 32A, 1. sal.",
        adresselinje4="3900 Nuuk",
        person_years={2020: {"skattedage": 73}},
        policies=[
            {
                "res": 19676889,
                "years": {
                    2020: 5000,
                    2021: 1000,
                },
            },
        ],
    )

    create_person(
        "Borger med negativt afkast og nuværende år påvirket af antal dage",
        cpr="1105550193",
        adresselinje2="Imaneq 32A, 3. sal.",
        adresselinje4="3900 Nuuk",
        person_years={2020: {"skattedage": 146}, 2021: {"skattedage": 102}},
        policies=[
            {
                "res": 19676889,
                "years": {
                    2020: 3000,
                    2021: 500,
                },
            },
        ],
    )

    create_person(
        "Borger med negativt afkast for mere end 10 år siden",
        cpr="0209025000",
        adresselinje2="Imaneq 32A, 2. sal.",
        adresselinje4="3900 Nuuk",
        person_years={2020: {"skattedage": 73}, 2021: {"skattedage": 146}},
        policies=[
            {
                "res": 19676889,
                "years": {
                    2020: 1000,
                    2021: 1000,
                },
            },
        ],
    )

    # Kan logges ind på test med certifikat fra
    # https://www.nets.eu/dk-da/kundeservice/nemid-tjenesteudbyder/Documents/TU-pakken/Tools/Testcertifikater/OCES%20II/MOCES_cpr_gyldig_2022.p12
    # Password: Test1234
    # Dette er ikke hemmeligt
    create_person(
        "Person som kan logges ind på test",
        cpr="1802602810",
        adresselinje2="Imaneq 32A, 1. sal.",
        adresselinje4="3900 Nuuk",
        policies=[
            {
                "ktd": 19676889,
                "years": {
                    2018: 1000,
                    2019: 2000,
                    2020: 2500,
                    2021: 5000,
                },
            },
            {
                "ktd": 55143315,
                "years": {
                    2018: -1000,
                    2019: -2500,
                    2020: 3000,
                    2021: 4000,
                },
            },
        ],
    )

    create_person(
        "Borger med negativt afkast fordelt over flere år",
        cpr="1105520049",
        adresselinje2="Imaneq 32A, 3. sal.",
        adresselinje4="3900 Nuuk",
        policies=[
            {
                "res": 19676889,
                "years": {
                    2018: -600,
                    2019: -1000,
                    2020: 3000,
                    2021: 2500,
                },
            },
        ],
    )

    create_person(
        "Borger med negativt afkast fra 2010 til 2020",
        cpr="1502062774",
        adresselinje2="Imaneq 32A, 3. sal.",
        adresselinje4="3900 Nuuk",
        policies=[
            {
                "res": 19676889,
                "years": {
                    2010: -300,
                    2011: -400,
                    2012: -500,
                    2013: 600,
                    2014: 0,
                    2015: 100,
                    2016: -30_000_000,
                    2017: -300,
                    2018: -600,
                    2019: 1000,
                    2020: -3000,
                    2021: 0,
                },
            },
        ],
    )
