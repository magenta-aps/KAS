from django.test import TestCase
from prisme.tenQ.dates import get_due_date, get_last_payment_date, \
    get_last_payment_date_from_due_date
from django.utils import timezone

import datetime


class Test10QDateCalculation(TestCase):
    # Test data in format:
    #   '<reference_date>': ('collect_date', 'last_payment_date')
    #
    # Rule for due date is "first day of next month plus 3 months".
    #
    # Rule for last payment date is first workday on or after the
    # 20th of the same month as the due date.
    #
    test_data = {
        # First of a month, non-dst => dst
        '2020-01-01': ('2020-05-01', '2020-05-20'),

        # Not first of a month
        '2020-01-02': ('2020-05-01', '2020-05-20'),

        # feb 29th in a leap year, skip saturday => monday
        '2020-02-29': ('2020-06-01', '2020-06-22'),

        # feb 28th in a non leap year, skip sunday => monday
        '2021-02-28': ('2021-06-01', '2021-06-21'),

        # Wrapping around end-of-year
        '2020-12-30': ('2021-04-01', '2021-04-20'),

        # dst => non-dst
        '2020-07-05': ('2020-11-01', '2020-11-20'),
    }

    def to_local_datetime(self, date_str):
        # We use midnight to make stuff will blow up if DST changes are not
        # handled correctly
        unaware_datetime = datetime.datetime.strptime(
            date_str + 'T00:00:00', '%Y-%m-%dT%H:%M:%S'
        )
        return timezone.make_aware(unaware_datetime)

    def test_10q_dates(self):
        for ref_date_str, target_dates in self.test_data.items():
            due_date_str, last_payment_date_str = target_dates

            ref_datetime = self.to_local_datetime(ref_date_str)
            due_datetime = self.to_local_datetime(due_date_str)
            last_payment_datetime = self.to_local_datetime(last_payment_date_str)

            calculated_due_date = get_due_date(ref_datetime)
            calculated_lpd = get_last_payment_date(ref_datetime)
            calculated_lpd2 = get_last_payment_date_from_due_date(calculated_due_date)

            self.assertEqual(
                calculated_due_date, due_datetime,
                'Ref date %s: Calculated due date correct' % ref_datetime.date().isoformat()
            )
            self.assertEqual(
                calculated_lpd, last_payment_datetime,
                'Ref date %s: Calculated last payment date correct' % ref_datetime.date().isoformat()
            )
            self.assertEqual(
                calculated_lpd, calculated_lpd2,
                'Ref date %s: Last payment date is the same when calculated '
                'from ref date and due date' % ref_datetime.date().isoformat()
            )
