from datetime import datetime

import pytz
from django.test import TestCase
from kas.models import TaxYear
from prisme.tenQ.writer import TenQTransactionWriter


class Test10QDateCalculation(TestCase):

    def setUp(self):
        TaxYear.objects.get_or_create(
            year=2022,
            defaults={
                'rate_text_for_transactions': 'Testing\r\nwith\r\nlines'
            }
        )
        self.transaction_writer = TenQTransactionWriter(
            collect_date=datetime(2022, 2, 18, 12, 4, 14, tzinfo=pytz.utc),
            year=2022,
            time_stamp=datetime(2022, 2, 18, 12, 35, 57, tzinfo=pytz.utc)
        )

    def test_writer_successful(self):
        prisme10Q_content = self.transaction_writer.serialize_transaction(
            cpr_nummer='1234567890',
            amount_in_dkk=1000,
            afstem_noegle='e688d6a6fc65424483819520bbbe7745',
        )
        self.assertEquals(
            prisme10Q_content,
            '\r\n'.join([
                ' KAS100202202181235090002220920221234567890001234567890',
                ' KAS24020220218123509000222092022123456789000209990000100000+10000000000+'
                '120220620202202182022062020220620000                                       '
                '202202182022010120221231                                                   '
                '                                                        '
                'e688d6a6fc65424483819520bbbe7745',
                ' KAS2602022021812350900022209202212345678900020999000Testing',
                ' KAS2602022021812350900022209202212345678900020999001with',
                ' KAS2602022021812350900022209202212345678900020999002lines'
            ])
        )

    def test_writer_invalid_input(self):
        defaults = {
            'cpr_nummer': '1234567890',
            'amount_in_dkk': 1000,
            'afstem_noegle': 'e688d6a6fc65424483819520bbbe7745',
        }
        too_long = {
            'cpr_nummer': '12345678901',
            'amount_in_dkk': 1000000000,
            'afstem_noegle': 'e688d6a6fc65424483819520bbbe7745xxxx',
        }
        for key, value in too_long.items():
            with self.assertRaises(ValueError):
                self.transaction_writer.serialize_transaction(**{
                    **defaults,
                    key: value
                })
