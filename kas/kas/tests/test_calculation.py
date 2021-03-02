from django.test import TestCase
from kas.models import PolicyTaxYear


class TestCalculationMath(TestCase):

    def test_with_no_adjustments(self):
        amount = 1000

        result = PolicyTaxYear.perform_calculation(amount)

        # The positive taxable amount should be equal to amount
        self.assertEquals(result["positive_amount"], amount)

        # Adjust factor for days in year should be 1
        self.assertEquals(result["tax_days_adjust_factor"], 1)

        # The amount adjust for days in year should be the initial amount
        self.assertEquals(result["year_adjusted_amount"], amount)

        # There should be no negative return
        self.assertEquals(result["available_negative_return"], 0)

        # There should be no spent negative return
        self.assertEquals(result["used_negative_return"], 0)

        # Taxable amount should be equal to initial amount
        self.assertEquals(result["taxable_amount"], amount)

        # Full tax should be equal to amount times the tax rate
        self.assertEquals(result["full_tax"], 153)

        # Tax with deductions should be equal to the full amount
        self.assertEquals(result["tax_with_deductions"], result["full_tax"])

    def test_negative_amount(self):
        amount = -1000

        result = PolicyTaxYear.perform_calculation(amount)

        # The positive taxable amount should be zero
        self.assertEquals(result["positive_amount"], 0)

        # Adjust factor for days in year should be 1
        self.assertEquals(result["tax_days_adjust_factor"], 1)

        # The amount adjust for days in year should be zero
        self.assertEquals(result["year_adjusted_amount"], 0)

        # Taxable amount should be equal to initial amount
        self.assertEquals(result["taxable_amount"], 0)

        # Full tax should be zero
        self.assertEquals(result["full_tax"], 0)

    def test_zero_amount(self):
        amount = 0

        result = PolicyTaxYear.perform_calculation(amount)

        # The positive taxable amount should be zero
        self.assertEquals(result["positive_amount"], 0)

        # The amount adjust for days in year should be zero
        self.assertEquals(result["year_adjusted_amount"], 0)

        # Taxable amount should be equal to initial amount
        self.assertEquals(result["taxable_amount"], 0)

        # Full tax should be zero
        self.assertEquals(result["full_tax"], 0)

    def test_days_adjustment(self):
        amount = 1000

        result = PolicyTaxYear.perform_calculation(
            amount,
            days_in_year=365,
            taxable_days_in_year=int(365/5),
        )

        self.assertEquals(result["tax_days_adjust_factor"], 0.2)

        # The amount adjust for days in year should be zero
        self.assertEquals(result["year_adjusted_amount"], 200)

        # Full tax should be 0.2 * 153 = 30,6 => 30
        self.assertEquals(result["full_tax"], 30)

    def test_foreign_adjustment(self):
        # This amount should make the tax exactly 1000
        amount = 6536

        self.assertEquals(PolicyTaxYear.perform_calculation(amount)["full_tax"], 1000)

        for foreign_paid, expected_result in (
            (0, 1000),
            (500, 500),
            (1000, 0),
            (2000, 0),
        ):
            result = PolicyTaxYear.perform_calculation(
                amount,
                foreign_paid_amount=foreign_paid,
            )

            self.assertEquals(result["tax_with_deductions"], expected_result)

    def test_input_validation(self):
        amount = 1000

        # Invalid number of days in year, only examine edge cases
        for days in (-1, 0, 1, 364):
            self.assertRaisesMessage(
                ValueError,
                "Days in year must be either 365 or 366",
                PolicyTaxYear.perform_calculation,
                amount,
                days_in_year=days
            )
        for days in (365, 366):
            try:
                PolicyTaxYear.perform_calculation(amount, days_in_year=days)
            except Exception as e:
                self.fail("Number of days %s raised exception %s" % (days, e))

        # Must have one or more taxable days in year
        self.assertRaisesMessage(
            ValueError,
            "Taxable days must be zero or higher",
            PolicyTaxYear.perform_calculation,
            amount,
            taxable_days_in_year=-1
        )
        for days in (0, 1, 365):
            try:
                PolicyTaxYear.perform_calculation(amount, taxable_days_in_year=days)
            except Exception as e:
                self.fail("Number of taxable days %s raised exception %s" % (days, e))

        # Taxable days must not be higher than days in year
        self.assertRaisesMessage(
            ValueError,
            "More taxable days than days in year",
            PolicyTaxYear.perform_calculation,
            amount,
            days_in_year=365,
            taxable_days_in_year=366
        )
        self.assertRaisesMessage(
            ValueError,
            "More taxable days than days in year",
            PolicyTaxYear.perform_calculation,
            amount,
            days_in_year=366,
            taxable_days_in_year=367
        )

        # Negative return must be positive:
        self.assertRaisesMessage(
            ValueError,
            "Negative return should be specified using a positive number",
            PolicyTaxYear.perform_calculation,
            amount,
            negative_return_last_ten_years=-1
        )
        for x in (0, 1, 1000):
            try:
                PolicyTaxYear.perform_calculation(amount, negative_return_last_ten_years=x)
            except Exception as e:
                self.fail("Negative return %s raised exception %s" % (x, e))

        # Used negative return must be positive:
        self.assertRaisesMessage(
            ValueError,
            "Used negative return must be zero or higher",
            PolicyTaxYear.perform_calculation,
            amount,
            used_negative_return_last_ten_years=-1
        )
        for x in (0, 1, 1000):
            try:
                PolicyTaxYear.perform_calculation(amount, used_negative_return_last_ten_years=x)
            except Exception as e:
                self.fail("Used negative return %s raised exception %s" % (x, e))

        # Foreign paid amount must be positive:
        self.assertRaisesMessage(
            ValueError,
            "Foreign paid amount must be zero or higher",
            PolicyTaxYear.perform_calculation,
            amount,
            foreign_paid_amount=-1
        )
        for x in (0, 1, 1000):
            try:
                PolicyTaxYear.perform_calculation(amount, foreign_paid_amount=x)
            except Exception as e:
                self.fail("Foreign paid amount %s raised exception %s" % (x, e))
