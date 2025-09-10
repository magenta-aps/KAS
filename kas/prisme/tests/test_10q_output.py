from datetime import date, datetime, timezone

from django.test import TestCase
from tenQ.writer import TenQTransactionWriter


class Test10QDateCalculation(TestCase):
    def setUp(self):
        self.transaction_writer = TenQTransactionWriter(
            due_date=date(2022, 2, 18),
            year=2022,
            timestamp=datetime(2022, 2, 18, 12, 35, 57, tzinfo=timezone.utc),
            leverandoer_ident="KAS",
        )

    def test_writer_successful(self):
        prisme10q_content = self.transaction_writer.serialize_transaction(
            cpr_nummer="1234567890",
            amount_in_dkk=1000,
            afstem_noegle="e688d6a6fc65424483819520bbbe7745",
            rate_text="Testing\r\nwith\r\nlines",
        )
        print(prisme10q_content)
        self.assertEqual(
            prisme10q_content,
            "\r\n".join(
                [
                    " KAS100202202181235090002220920221234567890001234567890",
                    " KAS24020220218123509000222092022123456789000209990000100000+10000000000+"
                    "120220221202202182022022120220221000                                       "
                    "202202182022010120221231                                                   "
                    "                                                        "
                    "e688d6a6fc65424483819520bbbe7745",
                    " KAS2602022021812350900022209202212345678900020999001Testing",
                    " KAS2602022021812350900022209202212345678900020999002with",
                    " KAS2602022021812350900022209202212345678900020999003lines",
                ]
            ),
        )

    def test_writer_invalid_input(self):
        defaults = {
            "cpr_nummer": "1234567890",
            "amount_in_dkk": 1000,
            "afstem_noegle": "e688d6a6fc65424483819520bbbe7745",
            "rate_text": "hephey",
        }
        too_long = {
            "cpr_nummer": "12345678901",
            "amount_in_dkk": 1000000000,
            "afstem_noegle": "e688d6a6fc65424483819520bbbe7745xxxx",
        }
        for key, value in too_long.items():
            with self.assertRaises(ValueError):
                self.transaction_writer.serialize_transaction(
                    **{
                        **defaults,
                        key: value,
                    }
                )
