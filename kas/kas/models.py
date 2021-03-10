import math

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.forms import model_to_dict
from django.utils.translation import gettext as _
from simple_history.models import HistoricalRecords
from django.db.models import Sum


class HistoryMixin(object):

    UNCHANGED = 0
    UPDATED = 1
    CREATED = 2

    """
    :param data: dict to populate model instance
    :param keys: keys in dict that define how to look for an existing instance. KvPs in data are extracted by keys for the lookup
    Updates an existing instance, or creates a new one if one doesn't exist.
    """
    @classmethod
    def update_or_create(cls, data, *keys):
        status = HistoryMixin.UNCHANGED
        try:
            item = cls.objects.get(**{k: v for k, v in data.items() if k in keys})
            existing_dict = model_to_dict(item)
            del existing_dict['id']
            new_dict = {
                k: v.pk if isinstance(v, models.Model) else v
                for k, v in data.items()
            }
            if existing_dict != new_dict:
                for k, v in data.items():
                    setattr(item, k, v)
                item._change_reason = "Updated by import"
                item.save()
                status = HistoryMixin.UPDATED
        except cls.DoesNotExist:
            item = cls(**data)
            item.change_reason = "Created by import"
            item.save()
            status = HistoryMixin.CREATED
        return item, status


class PensionCompany(models.Model):

    name = models.TextField(
        db_index=True,
        verbose_name=_('Navn'),
        help_text=_('Navn'),
        max_length=255,
        blank=True
    )

    address = models.TextField(
        verbose_name=_('Adresse'),
        help_text=_('Adresse'),
        blank=True
    )

    email = models.TextField(
        verbose_name=_('Email'),
        help_text=_('Email'),
        blank=True,
        null=True
    )

    phone = models.TextField(
        verbose_name=_('Telefon'),
        help_text=_('Telefon'),
        blank=True,
        null=True
    )

    cvr = models.IntegerField(
        unique=True,
        validators=(
            MinValueValidator(limit_value=1),
            MaxValueValidator(limit_value=99999999)
        )
    )

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name}, cvr={self.cvr})"


class TaxYear(models.Model):

    year = models.IntegerField(
        db_index=True,
        verbose_name=_('Skatteår'),
        help_text=_('Skatteår'),
        unique=True,
        null=False,
        validators=(MinValueValidator(limit_value=2000),)
    )

    def __str__(self):
        return f"{self.__class__.__name__}(year={self.year})"


class Person(HistoryMixin, models.Model):

    history = HistoricalRecords()

    cpr = models.TextField(
        db_index=True,
        verbose_name=_('CPR nummer'),
        help_text=_('CPR nummer'),
        unique=True,
        null=False,
        max_length=10,
        validators=(RegexValidator(regex=r'\d{10}'),)
    )

    municipality_code = models.IntegerField(
        blank=True,
        null=True
    )
    municipality_name = models.TextField(
        blank=True,
        null=True
    )
    address_line_1 = models.TextField(
        blank=True,
        null=True
    )
    address_line_2 = models.TextField(
        blank=True,
        null=True
    )
    address_line_3 = models.TextField(
        blank=True,
        null=True
    )
    address_line_4 = models.TextField(
        blank=True,
        null=True
    )
    address_line_5 = models.TextField(
        blank=True,
        null=True
    )
    full_address = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.__class__.__name__}(cpr={self.cpr})"


class PersonTaxYear(HistoryMixin, models.Model):

    class Meta:
        unique_together = ['tax_year', 'person']

    history = HistoricalRecords()

    tax_year = models.ForeignKey(
        TaxYear,
        on_delete=models.PROTECT,
        null=False
    )

    person = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        null=False
    )

    number_of_days = models.IntegerField(
        verbose_name='Antal dage',
        null=True
    )

    fully_tax_liable = models.BooleanField(
        verbose_name='Fuldt skattepligtig',
        default=True
    )

    def __str__(self):
        return f"{self.__class__.__name__}(cpr={self.person.cpr}, year={self.tax_year.year})"


class PolicyTaxYear(models.Model):

    class Meta:
        unique_together = ['person_tax_year', 'pension_company', 'policy_number']

    person_tax_year = models.ForeignKey(
        PersonTaxYear,
        on_delete=models.PROTECT,
        null=False,
        blank=True,
    )

    pension_company = models.ForeignKey(
        PensionCompany,
        on_delete=models.PROTECT,
        null=False,
        blank=True,
    )

    policy_number = models.CharField(
        max_length=40,
        blank=False,
    )

    prefilled_amount = models.BigIntegerField(
        verbose_name=_('Beløb rapporteret fra forsikringsselskab'),
        blank=True,
        null=True
    )

    estimated_amount = models.BigIntegerField(
        verbose_name=_('Skønsbeløb angivet af Skattestyrelsen'),
        default=0
    )

    self_reported_amount = models.BigIntegerField(
        verbose_name=_('Selvangivet beløb'),
        blank=False,
        null=True
    )

    ACTIVE_AMOUNT_PREFILLED = 1
    ACTIVE_AMOUNT_ESTIMATED = 2
    ACTIVE_AMOUNT_SELF_REPORTED = 3

    calculations_model_options = (
        (ACTIVE_AMOUNT_PREFILLED, prefilled_amount.verbose_name),
        (ACTIVE_AMOUNT_ESTIMATED, estimated_amount.verbose_name),
        (ACTIVE_AMOUNT_SELF_REPORTED, self_reported_amount.verbose_name),
    )

    active_amount = models.SmallIntegerField(
        verbose_name=_('Beløb brugt til beregning'),
        choices=calculations_model_options,
        default=ACTIVE_AMOUNT_PREFILLED
    )

    year_adjusted_amount = models.BigIntegerField(
        verbose_name=_('Beløb justeret for dage i skatteår'),
        default=0
    )

    CALCULATION_MODEL_DEFAULT = 1
    CALCULATION_MODEL_ALTERNATIVE = 2
    # TODO: Find the right terms here
    calculations_model_options = (
        (CALCULATION_MODEL_DEFAULT, _('Standard')),
        (CALCULATION_MODEL_ALTERNATIVE, _('Alternativ')),
    )
    calculation_model = models.SmallIntegerField(
        verbose_name=_('Beregningsmodel'),
        choices=calculations_model_options,
        default=CALCULATION_MODEL_DEFAULT
    )

    preliminary_paid_amount = models.BigIntegerField(
        verbose_name=_('Foreløbigt betalt kapitalafkast'),
        blank=True,
        null=True,
        validators=(MinValueValidator(limit_value=0),),
    )

    from_pension = models.BooleanField(
        default=False,
        verbose_name=_("Er kapitalafkastskatten hævet fra pensionsordning")
    )

    foreign_paid_amount_self_reported = models.BigIntegerField(
        verbose_name=_('Selvangivet beløb for betalt kapitalafkastskat i udlandet'),
        blank=True,
        default=0,
        validators=(MinValueValidator(limit_value=0),)
    )

    foreign_paid_amount_actual = models.BigIntegerField(
        verbose_name=_('Faktisk betalt kapitalafkastskat i udlandet'),
        blank=True,
        default=0,
        validators=(MinValueValidator(limit_value=0),)
    )

    # TODO: This needs to be handled with a relation stating which
    # amount was used from which year.
    applied_deduction_from_previous_years = models.BigIntegerField(
        verbose_name=_('Anvendt fradrag fra tidligere år'),
        blank=True,
        default=0,
        validators=(MinValueValidator(limit_value=0),)
    )

    calculated_full_tax = models.BigIntegerField(
        verbose_name=_('Beregnet skat uden fradrag'),
        blank=True,
        default=0,
    )

    calculated_result = models.BigIntegerField(
        verbose_name=_('Beregnet resultat'),
        blank=True,
        default=0,
    )

    modified_by = models.CharField(
        max_length=255,
        verbose_name=_('Modificeret af'),
        default='unknown'
    )

    locked = models.BooleanField(
        verbose_name=_('Låst'),
        help_text=_('Låst'),
        default=False
    )

    note = models.TextField(
        verbose_name=_('Note'),
        null=True
    )

    @classmethod
    def perform_calculation(
        cls,
        initial_amount: int,                           # The full base amount for the whole tax year
        days_in_year: int = 365,                       # Days in the year of the calculation
        taxable_days_in_year: int = 365,               # Number of days the person is paying tax in Greenland
        negative_return_last_ten_years: int = 0,       # Sum of negative return last 10 years (as a positive integer)
        used_negative_return_last_ten_years: int = 0,  # Spent negative return from last 10 years
        foreign_paid_amount: int = 0,                  # Amount already paid in taxes in foreign country
    ) -> dict:

        if days_in_year not in (365, 366):
            raise ValueError("Days in year must be either 365 or 366")

        if taxable_days_in_year < 0:
            raise ValueError("Taxable days must be zero or higher")

        if taxable_days_in_year > days_in_year:
            raise ValueError("More taxable days than days in year")

        if negative_return_last_ten_years < 0:
            raise ValueError("Negative return should be specified using a positive number")

        if used_negative_return_last_ten_years < 0:
            raise ValueError("Used negative return must be zero or higher")

        if foreign_paid_amount < 0:
            raise ValueError("Foreign paid amount must be zero or higher")

        positive_amount = max(0, initial_amount)

        # Calculate taxable days adjust factor
        tax_days_adjust_factor = taxable_days_in_year / days_in_year

        # Adjust for taxable days. Round down because we only operate in integer amounts of money
        year_adjusted_amount = math.floor(positive_amount * tax_days_adjust_factor)

        # The amount of negative return that can actually be used
        available_negative_return = max(0, used_negative_return_last_ten_years - negative_return_last_ten_years)

        # Used negative return
        used_negative_return = min(available_negative_return, year_adjusted_amount)

        # Taxable amount
        taxable_amount = year_adjusted_amount - used_negative_return

        # Calculate the tax
        full_tax = math.floor(taxable_amount * settings.KAS_TAX_RATE)

        tax_with_deductions = max(0, full_tax - max(0, foreign_paid_amount))

        return {
            "initial_amount": initial_amount,
            "days_in_year": days_in_year,
            "taxable_days_in_year": taxable_days_in_year,
            "negative_return_last_ten_years": negative_return_last_ten_years,
            "used_negative_return_last_ten_years": used_negative_return_last_ten_years,
            "foreign_paid_amount": foreign_paid_amount,
            "positive_amount": positive_amount,
            "tax_days_adjust_factor": tax_days_adjust_factor,
            "year_adjusted_amount": year_adjusted_amount,
            "available_negative_return": available_negative_return,
            "used_negative_return": used_negative_return,
            "taxable_amount": taxable_amount,
            "full_tax": full_tax,
            "tax_with_deductions": tax_with_deductions,
        }

    @property
    def initial_amount(self):
        if self.active_amount == self.ACTIVE_AMOUNT_PREFILLED:
            return self.prefilled_amount
        if self.active_amount == self.ACTIVE_AMOUNT_ESTIMATED:
            return self.estimated_amount
        if self.active_amount == self.ACTIVE_AMOUNT_SELF_REPORTED:
            return self.self_reported_amount

    @property
    def person(self):
        return self.person_tax_year.person

    @property
    def tax_year(self):
        return self.person_tax_year.tax_year

    @property
    def year(self):
        return self.tax_year.year

    @property
    def cpr(self):
        return self.person.cpr

    @property
    def same_policy_qs(self):
        return PolicyTaxYear.objects.filter(
            person_tax_year__person__cpr=self.cpr,
            pension_company=self.pension_company,
            policy_number=self.policy_number,
        )

    def previous_years_qs(self, years=10):

        # Finds posts for the last ten years with the same
        # cpr, pension company and policy number
        return self.same_policy_qs.filter(
            person_tax_year__tax_year__year__lt=self.year,
            person_tax_year__tax_year__year__gte=self.year - years,
        )

    @property
    def negative_return_last_ten_years(self):
        # Sum up negative amounts from last ten years
        result = self.previous_years_qs(years=10).filter(
            year_adjusted_amount__lt=0
        ).aggregate(models.Sum('year_adjusted_amount'))

        return result["year_adjusted_amount_sum"] * -1

    @property
    def used_negative_return_last_ten_years(self):

        # Sum up applied deductions from last nine years
        # Has to be nine instead of ten as deductions are used the year
        # after the negative return is present.
        result = self.previous_years_qs(years=9).aggregate(
            models.Sum('applied_deduction_from_previous_years')
        )

        return result['applied_deduction_from_previous_years__sum']

    def get_calculation(self):
        return PolicyTaxYear.perform_calculation(
            self.initial_amount,
            days_in_year=self.tax_year.days_in_year,
            taxable_days_in_year=self.person_tax_year.number_of_days,
            negative_return_last_ten_years=self.negative_return_last_ten_years,
            used_negative_return_last_ten_years=self.used_negative_return_last_ten_years,
            foreign_paid_amount=self.foreign_paid_amount_actual,
        )

    def recalculate(self):
        result = self.get_calculation()

        self.year_adjusted_amount = result["year_adjusted_amount"]
        self.applied_deduction_from_previous_years = result["used_negative_return"]
        self.calculated_full_tax = result["full_tax"]
        self.calculated_result = result["tax_with_deductions"]

    def sum_of_used_amount(self):
        # Deliver the amount of this years loss used in other years deduction
        result = self.payouts_using.aggregate(Sum('transferred_negative_payout'))

        value = result['transferred_negative_payout__sum']
        if value is None:
            return 0

        return value

    # Make a registration that we use some ot self's loss as deductoin on 'deducting_policy_tax_year'
    def use_amount(self, use_up_to_amount, deducting_policy_tax_year):
        # Create a relation of usage of this years loss as deduction in other years
        if self.year_adjusted_amount >= 0:
            return 0

        if self.sum_of_used_amount() >= -self.year_adjusted_amount:
            return 0

        available_to_be_used_amount = -self.year_adjusted_amount - self.sum_of_used_amount()
        to_be_used_amount = min(available_to_be_used_amount, use_up_to_amount)

        item, created = PreviousYearNegativePayout.objects.get_or_create(used_from=self,
                                                                         used_for=deducting_policy_tax_year)
        item.transferred_negative_payout += to_be_used_amount
        item.save()
        return to_be_used_amount

    def sum_of_deducted_amount(self):
        # Deliver the amount of this years deduction
        result = self.payouts_used.aggregate(Sum('transferred_negative_payout'))
        return result['transferred_negative_payout__sum']

    def __str__(self):
        return f"{self.__class__.__name__}(policy_number={self.policy_number}, cpr={self.person.cpr}, year={self.tax_year.year})"


class PreviousYearNegativePayout(models.Model):

    used_from = models.ForeignKey(
        PolicyTaxYear,
        related_name='payouts_using',
        null=True,
        on_delete=models.PROTECT
    )

    used_for = models.ForeignKey(
        PolicyTaxYear,
        related_name='payouts_used',
        null=True,
        on_delete=models.PROTECT
    )

    transferred_negative_payout = models.BigIntegerField(
        verbose_name=_('Overført negativt afkast'),
        blank=True,
        default=0,
    )

    def __str__(self):
        return f'used from :{self.used_from} used for :{self.used_for} payout :{self.transferred_negative_payout}'


class PolicyDocument(models.Model):

    policy_tax_year = models.ForeignKey(
        PolicyTaxYear,
        on_delete=models.PROTECT,
        null=False,
        related_name='policy_documents'
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_('Navn'),
        blank=False
    )

    description = models.TextField(
        verbose_name=_('Beskrivelse'),
        blank=True,
    )

    file = models.FileField(
        verbose_name=_('Fil'),
        blank=False
    )


class R75(models.Model):

    person_tax_year = models.ForeignKey(
        PersonTaxYear,
        on_delete=models.PROTECT,
    )

    preprinted_net_return = models.BigIntegerField(
        verbose_name=_('Fortrykt nettoafkast'),
        default=0
    )


class PriorYear(models.Model):

    person = models.ForeignKey(
        Person,
        on_delete=models.PROTECT
    )

    tax_paid_in_prior_years = models.BigIntegerField(
        db_index=True,
        verbose_name=_('Skat betalt i tidligere år'),
        help_text=_('Skat betalt i tidligere år')
    )


class Payment(models.Model):

    days = models.IntegerField(
        db_index=True,
        verbose_name=_('Antal dage'),
        help_text=_('Antal dage')
    )


def add_all_user_permission_if_staff(sender, instance, **kwargs):
    if instance.is_staff is True and instance.is_superuser is False:
        content_type = ContentType.objects.get_for_model(type(instance))
        # allow staff users to create, view and edit users, but not delete!.
        instance.user_permissions.set(Permission.objects.filter(content_type=content_type).exclude(codename='delete_user'))


post_save.connect(add_all_user_permission_if_staff, get_user_model(), dispatch_uid='User.permissions')


def add_skatteaar_to_queue(sender, instance, **kwargs):
    """
    for every change add an entry to the queue
    """
    # Queue.objects.create(item=instance, inserted_at=timezone.now())
    pass


post_save.connect(add_skatteaar_to_queue, TaxYear, dispatch_uid='Skatteaar.add_to_queue')
