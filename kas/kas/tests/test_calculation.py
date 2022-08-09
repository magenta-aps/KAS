import math
import uuid
from unittest.mock import patch

import django_rq
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test import override_settings
from fakeredis import FakeStrictRedis

from eskat.jobs import generate_sample_data
from kas.models import PersonTaxYearCensus
from kas.models import PolicyTaxYear, PersonTaxYear, TaxYear, Person, PensionCompany, FinalSettlement
from kas.tests.test_mixin import create_admin_user
from prisme.models import Transaction, Prisme10QBatch
from rq import Queue
from worker.models import Job
from kas.jobs import import_mandtal


@override_settings(FEATURE_FLAGS={'enable_dafo_override_of_address': False})
class TestCalculationMath(TestCase):

    def setUp(self):
        super().setUp()
        create_admin_user()

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

    def create_test_person_data(self, **policy_kwargs):
        person = Person.objects.create(cpr='0101010101')
        pension_company = PensionCompany.objects.create(res=12345678)
        tax_year, _ = TaxYear.objects.get_or_create(year=2020)
        person_tax_year = PersonTaxYear.objects.create(
            person=person,
            tax_year=tax_year,
            number_of_days=366,
        )
        policy_tax_year = PolicyTaxYear.objects.create(
            **{
                'person_tax_year': person_tax_year,
                'pension_company': pension_company,
                'policy_number': '1234',
                'prefilled_amount': 10000,
                'active_amount': PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
                'foreign_paid_amount_actual': 0,
                **policy_kwargs
            }
        )
        policy_tax_year.recalculate()
        policy_tax_year.save()
        return (person, pension_company, person_tax_year, policy_tax_year)

    def test_model_calculation(self):

        # Set up two older policies with losses, and one new policy that will deduct those losses
        person, pension_company, person_tax_year, policy = self.create_test_person_data(foreign_paid_amount_actual=200)
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
        older_policy_1.recalculate()
        older_policy_1.save()
        older_policy_2.recalculate()
        older_policy_2.save()
        calculation_results = policy.get_calculation()
        self.assertEquals(calculation_results['available_negative_return'], 6000)
        self.assertEquals(calculation_results['used_negative_return'], 6000)
        self.assertEquals(calculation_results['taxable_amount'], 4000)
        self.assertEquals(calculation_results['tax_with_deductions'], 412)
        self.assertDictEqual(calculation_results['desired_deduction_data'], {2018: 2000, 2019: 4000})

        policy.recalculate()
        policy.save()
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
        new_policy.save()
        self.assertEquals(new_policy.calculated_full_tax, 2295)
        self.assertEquals(new_policy.year_adjusted_amount, 15000)
        self.assertEquals(new_policy.calculated_result, 2295)

        # Deactivate one older policy; it should be excluded from calculation
        older_policy_2.active = False
        older_policy_2.save()
        calculation_results = policy.get_calculation()
        self.assertEquals(calculation_results['available_negative_return'], 2000)
        self.assertEquals(calculation_results['used_negative_return'], 2000)
        self.assertEquals(calculation_results['taxable_amount'], 8000)
        self.assertEquals(calculation_results['tax_with_deductions'], 1024)
        self.assertDictEqual(calculation_results['desired_deduction_data'], {2018: 2000})

        policy.recalculate()
        policy.save()
        self.assertEquals(policy.calculated_full_tax, 1224)
        self.assertEquals(policy.year_adjusted_amount, 10000)
        self.assertEquals(policy.calculated_result, 1024)

    def test_interest_calculation(self):
        person, pension_company, person_tax_year, policy = self.create_test_person_data()

        policy_calculation = policy.get_calculation()

        self.assertEquals(policy_calculation['tax_with_deductions'], 1530)

        Transaction.objects.create(
            person_tax_year=person_tax_year,
            status='transferred',
            type='prepayment',
            source_content_type=ContentType.objects.get_for_model(FinalSettlement),
            amount=-100
        )

        final_statement = FinalSettlement(
            person_tax_year=person_tax_year,
            interest_on_remainder=10,
            extra_payment_for_previous_missing=500,
            lock=person_tax_year.tax_year.get_current_lock
        )
        final_statement.save()

        calculation = final_statement.get_calculation_amounts()
        # No previous transactions, and 500 as extra payments, tax of 10.000
        self.assertDictEqual(calculation, {
            'applicable_previous_statements_exist': False,
            'previous_transactions_sum': 0,
            'total_tax': 1530,
            'prepayment': -100,
            'remainder': 1430,
            'interest_percent': 10,
            'interest_factor': 0.1,
            'interest_amount_on_remainder': 0,
            'remainder_with_interest': 1430,
            'extra_payment_for_previous_missing': 500,
            'total_payment': 1930
        })

        # Put result in a transaction
        prisme10Q_batch = Prisme10QBatch.objects.create(tax_year=person_tax_year.tax_year)
        prisme10Q_batch.add_transaction(final_statement)
        transaction = Transaction.objects.get(prisme10Q_batch=prisme10Q_batch)
        transaction.status = 'transferred'
        transaction.save()

        # Now create a new statement that should consider the previous statement and transaction in its calculations
        final_statement = FinalSettlement(
            person_tax_year=person_tax_year,
            interest_on_remainder=20,
            extra_payment_for_previous_missing=200,
            lock=person_tax_year.tax_year.get_current_lock
        )
        final_statement.save()

        calculation = final_statement.get_calculation_amounts()
        self.assertDictEqual(calculation, {
            'applicable_previous_statements_exist': True,
            'previous_transactions_sum': 1430,  # What the previous statement ended up with  1430
            'total_tax': 1530,  # Tax based on current statement
            'prepayment': -100,
            'remainder': 0,  # difference
            'interest_percent': 20,
            'interest_factor': 0.2,
            'interest_amount_on_remainder': 0,
            'remainder_with_interest': 0,
            'extra_payment_for_previous_missing': 200,
            'total_payment': 200
        })

    def test_prior_transactions(self):
        person, pension_company, person_tax_year, policy = self.create_test_person_data()
        policy_calculation = policy.get_calculation()
        self.assertEquals(policy_calculation['tax_with_deductions'], 1530)

        final_statement = FinalSettlement(
            person_tax_year=person_tax_year,
            interest_on_remainder=10,
            extra_payment_for_previous_missing=500,
            lock=person_tax_year.tax_year.get_current_lock
        )
        final_statement.save()
        final_statement = FinalSettlement(
            person_tax_year=person_tax_year,
            interest_on_remainder=20,
            extra_payment_for_previous_missing=200,
            lock=person_tax_year.tax_year.get_current_lock
        )
        final_statement.save()

        Transaction.objects.create(
            person_tax_year=person_tax_year,
            status='transferred',
            type='prisme10q',
            source_content_type=ContentType.objects.get_for_model(FinalSettlement),
            amount=1000
        )
        calculation = final_statement.get_calculation_amounts()
        # previous transactions of 1000, and 200 as extra payments, tax of 10.000
        self.assertDictEqual(calculation, {
            'applicable_previous_statements_exist': True,
            'previous_transactions_sum': 1000,
            'total_tax': 1530,
            'remainder': 530,
            'prepayment': 0,
            'interest_percent': 20,
            'interest_factor': 0.2,
            'interest_amount_on_remainder': 106,
            'remainder_with_interest': 636,
            'extra_payment_for_previous_missing': 200,
            'total_payment': 836
        })

        Transaction.objects.create(
            person_tax_year=person_tax_year,
            status='transferred',
            type='prisme10q',
            source_content_type=ContentType.objects.get_for_model(FinalSettlement),
            amount=1000
        )
        calculation = final_statement.get_calculation_amounts()
        # previous transactions of 2000, and 200 as extra payments, tax of 1000, resulting in negative payment
        self.assertDictEqual(calculation, {
            'applicable_previous_statements_exist': True,
            'previous_transactions_sum': 2000,
            'prepayment': 0,
            'total_tax': 1530,
            'remainder': -470,
            'interest_percent': 20,
            'interest_factor': 0.2,
            'interest_amount_on_remainder': -94,
            'remainder_with_interest': -564,
            'extra_payment_for_previous_missing': 200,
            'total_payment': -364
        })

    def test_mandtal_update_recalculate(self):
        person, pension_company, person_tax_year, policy_tax_year = self.create_test_person_data()
        self.assertEquals(policy_tax_year.calculated_result, 1530)

        PersonTaxYearCensus.objects.create(
            person_tax_year=person_tax_year,
            imported_kas_mandtal=uuid.uuid4(),
            number_of_days=200,
            fully_tax_liable=True,
        )
        person_tax_year.refresh_from_db()
        person_tax_year.recalculate_mandtal()
        policy_tax_year.refresh_from_db()
        self.assertEquals(policy_tax_year.calculated_result, 835)

        self.assertEquals(person_tax_year.notes.count(), 1)
        self.assertEquals(
            person_tax_year.notes.first().content,
            "Personens antal skattedage i 2020 er blevet opdateret; denne police er blevet påvirket af ændringen, "
            "og beregningen kan afvige fra en evt. oprettet slutopgørelse."
        )

    def test_mandtal_update_cascade(self):
        person, pension_company, person_tax_year1, policy_tax_year1 = self.create_test_person_data(prefilled_amount=-10000)
        person_tax_year2 = PersonTaxYear.objects.create(
            person=person,
            tax_year=TaxYear.objects.create(year=2021),
            number_of_days=365,
        )
        policy_tax_year2 = PolicyTaxYear.objects.create(
            person_tax_year=person_tax_year2,
            pension_company=pension_company,
            policy_number='1234',
            prefilled_amount=10000,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
            foreign_paid_amount_actual=0,
        )
        policy_tax_year2.recalculate()
        policy_tax_year2.save()

        PersonTaxYearCensus.objects.create(
            person_tax_year=person_tax_year1,
            imported_kas_mandtal=uuid.uuid4(),
            number_of_days=200,
            fully_tax_liable=True,
        )
        person_tax_year1.refresh_from_db()

        person_tax_year1.recalculate_mandtal()
        person_tax_year2.refresh_from_db()
        policy_tax_year2.refresh_from_db()

        self.assertEquals(policy_tax_year2.notes.count(), 1)
        self.assertEquals(person_tax_year2.notes.count(), 1)
        self.assertEquals(
            person_tax_year2.notes.first().content,
            "Policen for 2020 er blevet opdateret; denne police kan være påvirket af ændringen."
        )

    @patch.object(django_rq, 'get_queue', return_value=Queue(is_async=False, connection=FakeStrictRedis()))
    def test_mandtal_update_flags(self, django_rq):
        Job.schedule_job(
            generate_sample_data,
            'GenerateSampleData',
            get_user_model().objects.get(username='admin'),
        )
        year2020, _ = TaxYear.objects.get_or_create(year=2020)
        year2021, _ = TaxYear.objects.get_or_create(year=2021)

        person = Person.objects.create(cpr='1802602810')
        pension_company = PensionCompany.objects.create(res=12345678)
        person_tax_year1 = PersonTaxYear.objects.create(
            person=person,
            tax_year=year2020,
            number_of_days=200,
        )
        policy_tax_year1 = PolicyTaxYear.objects.create(
            **{
                'person_tax_year': person_tax_year1,
                'pension_company': pension_company,
                'policy_number': '1234',
                'prefilled_amount': -10000,
                'active_amount': PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
                'foreign_paid_amount_actual': 0,
            }
        )
        policy_tax_year1.recalculate()
        policy_tax_year1.save()

        person_tax_year2 = PersonTaxYear.objects.create(
            person=person,
            tax_year=year2021,
            number_of_days=365,
        )
        policy_tax_year2 = PolicyTaxYear.objects.create(
            person_tax_year=person_tax_year2,
            pension_company=pension_company,
            policy_number='1234',
            prefilled_amount=12345,
            active_amount=PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED,
            foreign_paid_amount_actual=0,
        )
        # Mandtal import will update number of days on person_tax_year1 and initiate a recalculation
        # that cascades and updates deductible amount and `efterbehandling`-flag on policy_tax_year2
        Job.schedule_job(
            import_mandtal,
            job_type='ImportMandtalJob',
            job_kwargs={'source_model': 'mockup', 'year': person_tax_year1.year, 'cpr': person.cpr},
            created_by=get_user_model().objects.get(username='admin')
        )
        policy_tax_year1.refresh_from_db()
        policy_tax_year2.refresh_from_db()
        self.assertFalse(policy_tax_year1.efterbehandling)
        self.assertTrue(policy_tax_year2.efterbehandling)
