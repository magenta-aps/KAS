# -*- coding: utf-8 -*-


from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from kas.models import (
    TaxYear,
    PensionCompany,
    Person,
    PolicyTaxYear,
    PersonTaxYear,
    PreviousYearNegativePayout,
)


class BaseNegativePayoutTestCase(TestCase):
    def pretty_print_table(self, table):
        print("=" * 50)
        for key in table:
            print("%s: {" % key)
            for key2 in table[key]:
                print("    '%s': %s" % (key2, table[key][key2]))
            print("}")
        print("=" * 50)

    def setUp(self) -> None:
        self.year_adjusted_amount = -1000
        self.assessed_amount = 2000
        self.username = "admin"
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = "admin"
        self.user.set_password(self.password)
        self.user.save()
        self.administrator_group = Group.objects.get(name="administrator")
        self.user.groups.set([self.administrator_group])
        self.person = Person.objects.create(cpr="1234567890", name="TestPerson")
        self.pension_company = PensionCompany.objects.create()
        self.tax_year = TaxYear.objects.create(year=2021)
        self.person_tax_year = PersonTaxYear.objects.create(
            tax_year=self.tax_year,
            person=self.person,
            number_of_days=self.tax_year.days_in_year,
        )
        self.policy_tax_year = PolicyTaxYear.objects.create(
            person_tax_year=self.person_tax_year,
            pension_company=self.pension_company,
            prefilled_amount=35,
            policy_number="1234",
            assessed_amount=self.assessed_amount,
            year_adjusted_amount=self.year_adjusted_amount,
        )

        # =============================================================================
        # Make a negative payout table
        # =============================================================================
        self.from_years = [2016, 2017, 2018, 2019, 2020]
        self.for_years = [2017, 2018, 2019, 2020, 2021]

        # Note1: We need a zero in this list - so the loop skips some objects
        # And does not create them but rather shows them with their default values
        #
        # Note2: The sum of this list cannot be larger than self.year_adjusted_amount
        self.for_year_values = [100, 200, 300, 400, 0]

        self.negative_payouts = []
        self.number_of_history_items = 0

        self.debug = False

        for from_year in self.from_years:
            from_tax_year, created = TaxYear.objects.get_or_create(year=from_year)
            from_person_tax_year, created = PersonTaxYear.objects.get_or_create(
                tax_year=from_tax_year,
                person=self.person,
                number_of_days=from_tax_year.days_in_year,
            )

            from_policy_tax_year, created = PolicyTaxYear.objects.get_or_create(
                person_tax_year=from_person_tax_year,
                pension_company=self.pension_company,
                prefilled_amount=35,
                policy_number="1234",
                assessed_amount=self.assessed_amount,
                year_adjusted_amount=self.year_adjusted_amount,
            )

            for for_year, for_year_value in zip(self.for_years, self.for_year_values):

                # for year needs to be equal or smaller than from year;
                # It is not possible to transfer negative payout to years in the past
                if for_year <= from_year:
                    continue

                # If the value is zero we do not need to create an object -
                # The default value is zero.
                if for_year_value == 0:
                    continue

                for_tax_year, created = TaxYear.objects.get_or_create(year=for_year)
                for_person_tax_year, created = PersonTaxYear.objects.get_or_create(
                    tax_year=for_tax_year,
                    person=self.person,
                    number_of_days=for_tax_year.days_in_year,
                )

                for_policy_tax_year, created = PolicyTaxYear.objects.get_or_create(
                    person_tax_year=for_person_tax_year,
                    pension_company=self.pension_company,
                    prefilled_amount=35,
                    policy_number="1234",
                    assessed_amount=self.assessed_amount,
                    year_adjusted_amount=self.year_adjusted_amount,
                )

                del created

                self.negative_payouts.extend(
                    [
                        PreviousYearNegativePayout.objects.create(
                            used_from=from_policy_tax_year,
                            used_for=for_policy_tax_year,
                            transferred_negative_payout=for_year_value,
                        )
                    ]
                )
                self.number_of_history_items += 1
        # =============================================================================
        # This is what the test data looks like
        #
        # 2016: {
        #     'available': 1000
        #     'used_by_year': {2016: '-', 2017: 100, 2018: 200, 2019: 300, 2020: 400, 2021: 0}
        #     'used_max_by_year': {2017: 100, 2018: 200, 2019: 300, 2020: 400, 2021: 0}
        #     'remaining': 0
        #     'used_total': 0
        #     'used_max': 2000
        # }
        # 2017: {
        #     'available': 1000
        #     'used_by_year': {2016: '-', 2017: '-', 2018: 200, 2019: 300, 2020: 400, 2021: 0}
        #     'used_max_by_year': {2018: 300, 2019: 400, 2020: 500, 2021: 100}
        #     'remaining': 100
        #     'used_total': 100
        #     'used_max': 2000
        # }
        # 2018: {
        #     'available': 1000
        #     'used_by_year': {2016: '-', 2017: '-', 2018: '-', 2019: 300, 2020: 400, 2021: 0}
        #     'used_max_by_year': {2019: 600, 2020: 700, 2021: 300}
        #     'remaining': 300
        #     'used_total': 400
        #     'used_max': 2000
        # }
        # 2019: {
        #     'available': 1000
        #     'used_by_year': {2016: '-', 2017: '-', 2018: '-', 2019: '-', 2020: 400, 2021: 0}
        #     'used_max_by_year': {2020: 800, 2021: 600}
        #     'remaining': 600
        #     'used_total': 900
        #     'used_max': 2000
        # }
        # 2020: {
        #     'available': 1000
        #     'used_by_year': {2016: '-', 2017: '-', 2018: '-', 2019: '-', 2020: '-', 2021: 0}
        #     'used_max_by_year': {2021: 1000}
        #     'remaining': 1000
        #     'used_total': 1600
        #     'used_max': 2000
        # }
        # 2021: {
        #     'available': 1000
        #     'used_by_year': {2016: '-', 2017: '-', 2018: '-', 2019: '-', 2020: '-', 2021: '-'}
        #     'used_max_by_year': {}
        #     'remaining': 1000
        #     'used_total': 0
        #     'used_max': 2000
        # }
        #
        # =============================================================================

        # And this is how to print it
        if self.debug:
            table = self.policy_tax_year.previous_year_deduction_table_data
            self.pretty_print_table(table)


class NegativePayoutTestCase(BaseNegativePayoutTestCase):
    def setUp(self) -> None:
        super(NegativePayoutTestCase, self).setUp()
        self.debug = False
        self.client.login(username=self.username, password=self.password)

    def get_table_from_context_data(self, return_request_object=False):
        r = self.client.get(
            reverse(
                "kas:policy_tabs",
                kwargs={"year": self.policy_tax_year.year, "person_id": self.person.id},
            )
        )

        if not return_request_object:
            return r.context["policy"].previous_year_deduction_table_data
        else:
            return (r.context["policy"].previous_year_deduction_table_data, r)

    def pretty_print_context_data(self, context_data):
        for key in context_data.keys():
            print("%s: %s" % (key, context_data[key]))

    def test_update_negative_payout(self):
        """
        Test if we can update a negative payout value and see if the table updates properly
        """

        context_data = None
        test_cases = (
            # Put a value on a year which has the default value (i.e. no object exists)
            {"from_year": 2020, "to_year": 2021, "value": 123},
            # Now try to change that value again
            {"from_year": 2020, "to_year": 2021, "value": 124},
            # Put a value on a year which already has a value (i.e. an object exists)
            {"from_year": 2018, "to_year": 2020, "value": 17},
            # Puta value which equals the maximum allowed value
            {"from_year": 2017, "to_year": 2018, "value": 300},
            # Put a value which equals the minimum allowed value
            {"from_year": 2019, "to_year": 2020, "value": 0},
        )

        for counter, test_case in enumerate(test_cases):

            if self.debug:
                print("Testing the following case:")
                print(test_case)

            from_year = test_case["from_year"]
            to_year = test_case["to_year"]
            test_value = test_case["value"]

            if counter == 0:
                # Retrieve original negative payout table from context data
                virgin_context_data = self.get_table_from_context_data()
            else:
                # Or just use the one which was retrieved in the previous iteration
                virgin_context_data = context_data.copy()

            if self.debug:
                print("virgin_context_data:")
                self.pretty_print_context_data(virgin_context_data)

            response = self.client.post(
                reverse(
                    "kas:define-negative-policy-payout",
                    kwargs={
                        "pk": self.policy_tax_year.pk,
                        "from": from_year,
                        "to": to_year,
                    },
                ),
                data={"transferred_negative_payout": test_value},
                follow=True,
            )

            # Check if the response was successful
            self.assertEqual(response.status_code, 200)

            context_data = self.get_table_from_context_data()

            if self.debug:
                print("context_data:")
                self.pretty_print_context_data(context_data)

            # Check if the value got updated
            value_from_context = context_data[from_year]["used_by_year"][to_year]

            self.assertEqual(value_from_context, test_value)

            # Check if the 'remaining' value got updated
            virgin_value_from_context = virgin_context_data[from_year]["used_by_year"][
                to_year
            ]
            remaining_value_from_context = context_data[from_year]["remaining"]
            remaining_value_from_virgin_context = virgin_context_data[from_year][
                "remaining"
            ]

            target_remaining = (
                remaining_value_from_virgin_context
                - test_value
                + virgin_value_from_context
            )

            self.assertEqual(target_remaining, remaining_value_from_context)

            # Check if the 'used_total' value got updated
            virgin_used_total = virgin_context_data[to_year]["used_total"]
            used_total = context_data[to_year]["used_total"]

            diff_used_total = used_total - virgin_used_total
            diff_value = test_value - virgin_value_from_context

            self.assertEqual(diff_used_total, diff_value)

    def test_to_year_before_from_year(self):
        """
        Test if we can post a value for a from/for year combination that is not allowed
        """

        response = self.client.post(
            reverse(
                "kas:define-negative-policy-payout",
                kwargs={"pk": self.policy_tax_year.pk, "from": 2020, "to": 2019},
            ),
            data={"transferred_negative_payout": 5},
            follow=True,
        )

        self.assertEqual(response.status_code, 400)

    def test_to_year_equal_to_from_year(self):
        """
        Test if we can post a value for a from/for year combination that is not allowed
        """

        response = self.client.post(
            reverse(
                "kas:define-negative-policy-payout",
                kwargs={"pk": self.policy_tax_year.pk, "from": 2019, "to": 2019},
            ),
            data={"transferred_negative_payout": 5},
            follow=True,
        )

        self.assertEqual(response.status_code, 400)

    def test_post_value_above_or_below_limit(self):
        """
        Test if we can post a value above the upper limit or below zero
        """

        test_cases = (
            {"value": 10, "should_update": True},
            {"value": 10_000, "should_update": False},
            {"value": -10, "should_update": False},
        )

        negative_payout = self.negative_payouts[0]
        from_year = negative_payout.from_year
        to_year = negative_payout.for_year

        for test_case in test_cases:
            initial_value = negative_payout.transferred_negative_payout
            test_value = test_case["value"]
            should_update = test_case["should_update"]

            if self.debug:
                self.pretty_print_context_data(self.get_table_from_context_data())

            response = self.client.post(
                reverse(
                    "kas:define-negative-policy-payout",
                    kwargs={
                        "pk": self.policy_tax_year.pk,
                        "from": from_year,
                        "to": to_year,
                    },
                ),
                data={"transferred_negative_payout": test_value},
                follow=True,
            )

            if self.debug:
                self.pretty_print_context_data(self.get_table_from_context_data())

            negative_payout.refresh_from_db()

            # Check if the response was successful
            self.assertEqual(response.status_code, 200)

            # Check if the value got updated
            updated_value = negative_payout.transferred_negative_payout
            if should_update:
                self.assertEqual(updated_value, test_value)
            else:
                self.assertEqual(updated_value, initial_value)

    def test_edit_links(self):
        """
        Check that values which cannot be modified do not have 'edit' links
        """
        test_cases = (
            # Post nothing
            None,
            # Change the value for 2017,2018 to 300. In that case all other values in 2017
            # become un-editable
            {"from_year": 2017, "to_year": 2018, "value": 300},
            # Change 2019,2020 to 800. In that case all other values in 2020
            # become un-editable
            {"from_year": 2019, "to_year": 2020, "value": 800},
        )

        for test_case in test_cases:

            if test_case is not None:
                self.client.post(
                    reverse(
                        "kas:define-negative-policy-payout",
                        kwargs={
                            "pk": self.policy_tax_year.pk,
                            "from": test_case["from_year"],
                            "to": test_case["to_year"],
                        },
                    ),
                    data={"transferred_negative_payout": test_case["value"]},
                    follow=True,
                )

            context_data, r = self.get_table_from_context_data(
                return_request_object=True
            )
            if self.debug:
                self.pretty_print_context_data(context_data)

            # Find tuple of years which should be editable
            editable_years = []

            for year_from, value_from in context_data.items():
                for year_to, value_to in value_from["used_by_year"].items():
                    if type(value_to) != str:
                        limit = context_data[year_from]["used_max_by_year"][year_to]
                    else:
                        continue

                    if limit > 0:
                        editable_years.extend([(year_from, year_to)])

            # Find tuple of years which are editable
            editable_years_from_html = []
            for line in r.rendered_content.split("\n"):
                # If href is in the line, it means that the year can be edited
                if (
                    ("negativepayoutdefined" in line)
                    and ("href" in line)
                    and ("history" not in line)
                ):
                    year_from = int(line.split(r"/")[4])
                    year_to = int(line.split(r"/")[5])
                    editable_years_from_html.extend([(year_from, year_to)])

            if self.debug:
                print("Editable years:")
                print(editable_years_from_html)

                print("Years which should be editable:")
                print(editable_years)

            # Check if we have the same amount of editable years
            self.assertEqual(len(editable_years), len(editable_years_from_html))

            # Check if the editable years are the same
            editable_years_set = set(editable_years)
            editable_years_from_html_set = set(editable_years_from_html)

            for entry1, entry2 in zip(editable_years_set, editable_years_from_html_set):
                self.assertEqual(entry1, entry2)

    def test_history_404(self):
        """
        Test if the history throws 404 if there is no history
        """

        response = self.client.get(
            reverse(
                "kas:define-negative-policy-payout-history",
                kwargs={"pk": self.policy_tax_year.pk, "from": 2020, "to": 2021},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_history_contents(self):
        """
        Test if we can see applied changes in the history
        """
        values_to_put_into_history = [1, 2]
        year_from = 2020
        year_to = 2021

        # Put some values in the history
        for value in values_to_put_into_history:
            self.client.post(
                reverse(
                    "kas:define-negative-policy-payout",
                    kwargs={
                        "pk": self.policy_tax_year.pk,
                        "from": year_from,
                        "to": year_to,
                    },
                ),
                data={"transferred_negative_payout": value},
                follow=True,
            )

        # Get history
        response = self.client.get(
            reverse(
                "kas:define-negative-policy-payout-history",
                kwargs={
                    "pk": self.policy_tax_year.pk,
                    "from": year_from,
                    "to": year_to,
                },
            )
        )

        values_in_history = [
            o.transferred_negative_payout for o in response.context_data["objects"]
        ]

        change_timestamps = [o.history_date for o in response.context_data["objects"]]

        values_in_history_sorted = [
            x for _, x in sorted(zip(change_timestamps, values_in_history))
        ]

        self.assertEqual(values_to_put_into_history, values_in_history_sorted)

    def test_history_links(self):
        """
        Check that a history link appears after modifying a value
        """

        from_year = 2020
        to_year = 2021

        def get_years_with_history(request):
            # Find tuple of years which have history links
            years_with_history_from_html = []
            for line in request.rendered_content.split("\n"):
                if (
                    ("negativepayoutdefined" in line)
                    and ("href" in line)
                    and ("history" in line)
                ):
                    year_from = int(line.split(r"/")[4])
                    year_to = int(line.split(r"/")[5])
                    years_with_history_from_html.extend([(year_from, year_to)])
            return years_with_history_from_html

        virgin_context_data, virgin_request = self.get_table_from_context_data(
            return_request_object=True
        )
        years_with_history = get_years_with_history(virgin_request)

        # Check if we have the correct number of history links
        self.assertEqual(len(years_with_history), self.number_of_history_items)

        # Check if the history link which we are going to make is not there
        self.assertNotIn((from_year, to_year), years_with_history)

        # Change a value which was not changed. A history link should now appear
        self.client.post(
            reverse(
                "kas:define-negative-policy-payout",
                kwargs={
                    "pk": self.policy_tax_year.pk,
                    "from": from_year,
                    "to": to_year,
                },
            ),
            data={"transferred_negative_payout": 1000},
            follow=True,
        )

        context_data, request = self.get_table_from_context_data(
            return_request_object=True
        )

        # Check if the history link is there
        years_with_history = get_years_with_history(request)
        self.assertIn((from_year, to_year), years_with_history)

    def test_protected_value_recalculate(self):
        """
        Check that a protected value does not get updated when recalculating
        """

        test_cases = (
            # Case 1: The protected value remains unchanged
            {
                "assessed_amount": 1000,
                "from_year": 2019,
                "to_year": 2020,
                "transferred_negative_payout": 800,
                "target_value": 800,
            },
            # Case 2: The protected value needs to be changed
            {
                "assessed_amount": 700,
                "from_year": 2019,
                "to_year": 2020,
                "transferred_negative_payout": 800,
                "target_value": 700,
            },
        )

        for test_case in test_cases:

            assessed_amount = test_case["assessed_amount"]
            from_year = test_case["from_year"]
            to_year = test_case["to_year"]
            transferred_negative_payout = test_case["transferred_negative_payout"]
            target_value = test_case["target_value"]

            # Update the negative payout value
            self.client.post(
                reverse(
                    "kas:define-negative-policy-payout",
                    kwargs={
                        "pk": self.policy_tax_year.pk,
                        "from": from_year,
                        "to": to_year,
                    },
                ),
                data={
                    "transferred_negative_payout": transferred_negative_payout,
                    "protected_against_recalculations": True,
                },
                follow=True,
            )

            # Update the assessed amount
            policy = self.policy_tax_year.same_policy_qs.get(
                person_tax_year__tax_year__year=to_year
            )

            policy.assessed_amount = assessed_amount
            policy.save()
            policy.refresh_from_db()

            # Recalculate the policy
            policy.recalculate()

            # Check that the values sum to the proper amount
            values = []
            table = self.get_table_from_context_data()
            for key in table.keys():
                value = table[key]["used_by_year"][to_year]
                if value != "-":
                    values.extend([value])

            self.assertEqual(sum(values), assessed_amount)

            # Check that the protected value is unaffected
            self.assertEqual(table[from_year]["used_by_year"][to_year], target_value)

    def test_protected_value_adjust_payout(self):
        """
        Check that a protected value does not get updated when adjusting negative payout
        """

        # Protect 2 years in 2017 - giving a protected amount of 600 kr.
        from_year = 2017

        for to_year in [2018, 2020]:
            self.client.post(
                reverse(
                    "kas:define-negative-policy-payout",
                    kwargs={
                        "pk": self.policy_tax_year.pk,
                        "from": from_year,
                        "to": to_year,
                    },
                ),
                data={"protected_against_recalculations": True},
                follow=True,
            )

        # change the available amount for 2017 to 900
        policy = self.policy_tax_year.same_policy_qs.get(
            person_tax_year__tax_year__year=from_year
        )
        policy.year_adjusted_amount = -900
        policy.save()

        # Check that nothing happens
        table = self.get_table_from_context_data()
        self.assertEqual(table[from_year]["used_by_year"][2018], 200)
        self.assertEqual(table[from_year]["used_by_year"][2019], 300)
        self.assertEqual(table[from_year]["used_by_year"][2020], 400)

        # change the available amount for 2017 to 800
        policy.year_adjusted_amount = -800
        policy.save()

        # Check that 100 kr. is deducted from the unprotected year
        table = self.get_table_from_context_data()
        self.assertEqual(table[from_year]["used_by_year"][2019], 200)

        # change the available amount for 2017 to 500
        policy.year_adjusted_amount = -500
        policy.save()

        # Check that 100 kr. is deducted from one of the protected years
        table = self.get_table_from_context_data()
        self.assertEqual(table[from_year]["used_by_year"][2019], 0)
        try:
            self.assertEqual(table[from_year]["used_by_year"][2020], 300)
        except AssertionError:
            self.assertEqual(table[from_year]["used_by_year"][2018], 100)
