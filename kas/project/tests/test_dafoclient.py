from django.test import TestCase, override_settings

from project.dafo import DatafordelerClient


@override_settings(DAFO={"mock": True})
class TestDafoConnection(TestCase):
    def test_lookup_person_info(self):
        """
        Call the dafo-client to get a personinfo
        """
        dafo_client = DatafordelerClient.from_settings()
        dafo_client.set_mock_data(
            mock_data={
                "1111111111": {
                    "cprNummer": "1111111111",
                    "fornavn": "Anders",
                    "efternavn": "And",
                    "adresse": "Imaneq 32A, 3.",
                    "postnummer": 3900,
                    "bynavn": "Nuuk",
                },
                "1111111112": {
                    "cprNummer": "1111111112",
                    "fornavn": "Andersine",
                    "efternavn": "And",
                    "adresse": "Imaneq 32A, 3.",
                    "postnummer": 3900,
                    "bynavn": "Nuuk",
                },
            }
        )

        params = {"cpr": "1111111111,1111111112"}
        result = dafo_client.get_person_information(params)
        self.assertEqual(
            {
                "1111111111": {
                    "cprNummer": "1111111111",
                    "fornavn": "Anders",
                    "efternavn": "And",
                    "adresse": "Imaneq 32A, 3.",
                    "postnummer": 3900,
                    "bynavn": "Nuuk",
                },
                "1111111112": {
                    "cprNummer": "1111111112",
                    "fornavn": "Andersine",
                    "efternavn": "And",
                    "adresse": "Imaneq 32A, 3.",
                    "postnummer": 3900,
                    "bynavn": "Nuuk",
                },
            },
            result,
        )
