import math

from django.conf import settings
from django.test import TestCase
from kas.models import PolicyTaxYear, PersonTaxYear, TaxYear, Person, PensionCompany


class TestCalculationMath(TestCase):

    def test_with_no_adjustments(self):
        amount = 1000

        result = PolicyTaxYear.perform_calculation(amount)

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
        self.assertEquals(result["full_tax"], amount * settings.KAS_TAX_RATE)

        # Tax with deductions should be equal to the full amount
        self.assertEquals(result["tax_with_deductions"], result["full_tax"])

    def test_negative_amount(self):
        amount = -1000

        result = PolicyTaxYear.perform_calculation(amount)

        # Adjust factor for days in year should be 1
        self.assertEquals(result["tax_days_adjust_factor"], 1)

        # The amount adjust for days in year should be -1000
        self.assertEquals(result["year_adjusted_amount"], -1000)

        # Taxable amount should be 0
        self.assertEquals(result["taxable_amount"], 0)

        # Full tax should be zero
        self.assertEquals(result["full_tax"], 0)

    def test_zero_amount(self):
        amount = 0

        result = PolicyTaxYear.perform_calculation(amount)

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

    def test_days_adjustment_self_reported(self):
        amount = 1000

        result = PolicyTaxYear.perform_calculation(
            amount,
            days_in_year=365,
            taxable_days_in_year=int(365/5),
            adjust_for_days_in_year=False,
        )

        self.assertEquals(result["tax_days_adjust_factor"], 1)
        self.assertEquals(result["year_adjusted_amount"], 1000)
        self.assertEquals(result["full_tax"], 153)

    def test_deductions(self):

        # Test with available deductions that fully cover the income
        result = PolicyTaxYear.perform_calculation(
            1000,
            available_deduction_data={'2017': 300, '2016': 500, '2018': 400, '2014': 300}
        )
        self.assertEquals(result['desired_deduction_data'], {'2014': 300, '2016': 500, '2017': 200})
        self.assertEquals(result['available_negative_return'], 1500)
        self.assertEquals(result['used_negative_return'], 1000)
        self.assertEquals(result['taxable_amount'], 0)
        self.assertEquals(result['full_tax'], 0)

        # Test with available deductions that don't fully cover the income
        result = PolicyTaxYear.perform_calculation(
            1000,
            available_deduction_data={'2019': 300, '2016': 500}
        )
        self.assertEquals(result['desired_deduction_data'], {'2016': 500, '2019': 300})
        self.assertEquals(result['available_negative_return'], 800)
        self.assertEquals(result['used_negative_return'], 800)
        self.assertEquals(result['taxable_amount'], 200)
        self.assertEquals(result['full_tax'], math.floor(200*settings.KAS_TAX_RATE))

        # Test with a negative income
        result = PolicyTaxYear.perform_calculation(
            -1000,
            available_deduction_data={'2019': 500, '2016': 700}
        )
        self.assertEquals(result['desired_deduction_data'], {})
        self.assertEquals(result['available_negative_return'], 1200)
        self.assertEquals(result['used_negative_return'], 0)
        self.assertEquals(result['taxable_amount'], 0)
        self.assertEquals(result['full_tax'], 0)

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
            available_deduction_data={'2015': -1}
        )
        for x in (0, 1, 1000):
            try:
                PolicyTaxYear.perform_calculation(amount, available_deduction_data={'2015': x})
            except Exception as e:
                self.fail("Negative return %s raised exception %s" % (x, e))

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

    def test_model_calculation(self):

        # Set up two older policies with losses, and one new policy that will deduct those losses
        person = Person.objects.create(cpr='0101010101')
        pension_company = PensionCompany.objects.create(res=12345678)
        older_policy_1 = PolicyTaxYear.objects.create(
            person_tax_year=PersonTaxYear.objects.create(
                person=person,
                tax_year=TaxYear.objects.create(year=2018),
                number_of_days=365,
            ),
            pension_company=pension_company,
            policy_number='1234',
            prefilled_amount=-2000,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED
        )
        older_policy_2 = PolicyTaxYear.objects.create(
            person_tax_year=PersonTaxYear.objects.create(
                person=person,
                tax_year=TaxYear.objects.create(year=2019),
                number_of_days=365,
            ),
            pension_company=pension_company,
            policy_number='1234',
            prefilled_amount=-4000,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
        )
        policy = PolicyTaxYear.objects.create(
            person_tax_year=PersonTaxYear.objects.create(
                person=person,
                tax_year=TaxYear.objects.create(year=2020),
                number_of_days=366,
            ),
            pension_company=pension_company,
            policy_number='1234',
            prefilled_amount=10000,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
            foreign_paid_amount_actual=200,
        )
        older_policy_1.recalculate()
        older_policy_2.recalculate()
        calculation_results = policy.get_calculation()
        self.assertEquals(calculation_results['available_negative_return'], 6000)
        self.assertEquals(calculation_results['used_negative_return'], 6000)
        self.assertEquals(calculation_results['taxable_amount'], 4000)
        self.assertEquals(calculation_results['tax_with_deductions'], 412)
        self.assertDictEqual(calculation_results['desired_deduction_data'], {2018: 2000, 2019: 4000})

        policy.recalculate()
        self.assertEquals(policy.calculated_full_tax, 612)
        self.assertEquals(policy.year_adjusted_amount, 10000)
        self.assertEquals(policy.calculated_result, 412)

        # Create a new policy that cannot use those deductions because they are already taken
        new_policy = PolicyTaxYear.objects.create(
            person_tax_year=PersonTaxYear.objects.create(
                person=person,
                tax_year=TaxYear.objects.create(year=2021),
                number_of_days=365,
            ),
            pension_company=pension_company,
            policy_number='1234',
            prefilled_amount=15000,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
        )
        calculation_results = new_policy.get_calculation()
        self.assertEquals(calculation_results['available_negative_return'], 0)
        self.assertEquals(calculation_results['used_negative_return'], 0)
        self.assertEquals(calculation_results['taxable_amount'], 15000)
        self.assertEquals(calculation_results['tax_with_deductions'], 2295)
        self.assertDictEqual(calculation_results['desired_deduction_data'], {})

        new_policy.recalculate()
        self.assertEquals(new_policy.calculated_full_tax, 2295)
        self.assertEquals(new_policy.year_adjusted_amount, 15000)
        self.assertEquals(new_policy.calculated_result, 2295)
