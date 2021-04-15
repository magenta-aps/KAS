import calendar
import math

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.forms import model_to_dict
from django.utils.translation import gettext as _
from simple_history.models import HistoricalRecords
from eskat.models import ImportedR75PrivatePension


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

    class Meta:
        ordering = ['name']
        verbose_name = _('pensionsselskab')
        verbose_name_plural = _('pensionsselskaber')

    name = models.TextField(
        db_index=True,
        verbose_name=_('Navn'),
        help_text=_('Navn'),
        max_length=255,
        blank=True,
        null=True,
    )

    address = models.TextField(
        verbose_name=_('Adresse'),
        help_text=_('Adresse'),
        blank=True,
        null=True,
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

    res = models.IntegerField(
        verbose_name=_('Identificerende nummer (reg.nr. for banker, se-nr for pensionsselskaber)'),
        unique=True,
        null=True,  # This will be null when created as a self-reported company
        validators=(MinValueValidator(limit_value=1),),
    )

    agreement_present = models.BooleanField(
        default=False,
        verbose_name=_("Foreligger der en aftale med skattestyrelsen")
    )

    agreement_present = models.BooleanField(
        default=False,
        verbose_name=_("Foreligger der en aftale med skattestyrelsen")
    )

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name}, res={self.res})"


class TaxYear(models.Model):

    class Meta:
        ordering = ['-year']

    year = models.IntegerField(
        db_index=True,
        verbose_name=_('Skatteår'),
        help_text=_('Skatteår'),
        unique=True,
        null=False,
        blank=False,
        validators=(MinValueValidator(limit_value=2000),)
    )

    @property
    def is_leap_year(self):
        return calendar.isleap(self.year)

    @property
    def days_in_year(self):
        return 366 if self.is_leap_year else 365

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

    name = models.TextField(
        blank=True,
        null=True
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
        return f"{self.__class__.__name__}(cpr={self.cpr},municipality_code={self.municipality_code}," \
               f"municipality_name={self.municipality_name}," \
               f"address_line_1={self.address_line_1},address_line_2={self.address_line_2}," \
               f"address_line_3={self.address_line_1},address_line_4={self.address_line_2}," \
               f"address_line_5={self.address_line_2}," \
               f"full_address={self.full_address})"


tax_slip_statuses = (
    ('created', _('KAS Selvangivelse genereret')),
    ('sent', _('KAS Selvangivelse afsendt')),  # sent means that the processing is done
    ('post_processing', _('Afventer efterbehandling')),
    ('failed', _('Afsendelse fejlet'))
)
# final state is either sent or failed


def taxslip_path_by_year(instance, filename):
    return 'reports/{filename}'.format(filename=filename)


class TaxSlipGenerated(models.Model):
    file = models.FileField(upload_to=taxslip_path_by_year, null=True)
    status = models.TextField(choices=tax_slip_statuses, default='created', blank=True)
    post_processing_status = models.TextField(default='', blank=True)
    recipient_status = models.TextField(default='', blank=True)
    message_id = models.TextField(blank=True, default='')  # eboks message_id

    @property
    def delivery_method(self):
        if self.status == 'sent':
            if self.recipient_status == '':
                return _('E-boks')
            elif self.recipient_status == 'dead':
                return None
            else:
                # exempt, minor, invalid
                if self.post_processing_status in ('address resolved', 'remote printed'):
                    return _('Fjernprint')


class PersonTaxYear(HistoryMixin, models.Model):

    class Meta:
        ordering = ['-tax_year__year', 'person__name']
        unique_together = ['tax_year', 'person']

    history = HistoricalRecords()

    tax_slip = models.OneToOneField(
        TaxSlipGenerated,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    tax_year = models.ForeignKey(
        TaxYear,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
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

    foreign_pension_notes = models.TextField(
        verbose_name='Noter om pension i udlandet',
        null=True
    )

    general_notes = models.TextField(
        verbose_name='Yderligere noter',
        null=True
    )

    @property
    def year(self):
        return self.tax_year.year

    @classmethod
    def get_pdf_recipients_for_year_qs(cls, tax_year_obj_or_pk, exclude_already_generated=False):
        qs = cls.objects.filter(
            fully_tax_liable=True,
            number_of_days__isnull=False,
            number_of_days__gt=0,
            tax_year=tax_year_obj_or_pk
        )

        if exclude_already_generated:
            qs = qs.filter(tax_slip=None)

        return qs

    @property
    def days_in_year_factor(self):
        if self.number_of_days is None:
            return 1
        return self.number_of_days / self.tax_year.days_in_year

    def recalculate_mandtal(self):
        number_of_days = 0
        fully_tax_liable = False
        qs = self.persontaxyearcensus_set.filter(fully_tax_liable=True)
        for person_tax_year_census in qs:
            number_of_days += person_tax_year_census.number_of_days
            fully_tax_liable = True
        self.number_of_days = min(number_of_days, self.tax_year.days_in_year)
        self.fully_tax_liable = fully_tax_liable
        self.save()

    def __str__(self):
        return f"{self.__class__.__name__}(cpr={self.person.cpr}, year={self.tax_year.year})"


class PersonTaxYearCensus(HistoryMixin, models.Model):

    person_tax_year = models.ForeignKey(
        PersonTaxYear,
        null=False,
        on_delete=models.CASCADE
    )

    imported_kas_mandtal = models.UUIDField(
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


class PolicyTaxYear(HistoryMixin, models.Model):
    history = HistoricalRecords()

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
        verbose_name=_('Beløb rapporteret fra pensionsselskab'),
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

    active_amount_options = (
        (ACTIVE_AMOUNT_PREFILLED, prefilled_amount.verbose_name),
        (ACTIVE_AMOUNT_ESTIMATED, estimated_amount.verbose_name),
        (ACTIVE_AMOUNT_SELF_REPORTED, self_reported_amount.verbose_name),
    )

    active_amount = models.SmallIntegerField(
        verbose_name=_('Beløb brugt til beregning'),
        choices=active_amount_options,
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

    available_negative_return = models.BigIntegerField(
        verbose_name=_('Tilgængeligt fradrag fra andre år (beregnet ud fra andre data)'),
        blank=True,
        null=True,
        default=None,
        editable=False,
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

    @classmethod
    def perform_calculation(
        cls,
        initial_amount: int,                           # The full base amount for the whole tax year
        days_in_year: int = 365,                       # Days in the year of the calculation
        taxable_days_in_year: int = 365,               # Number of days the person is paying tax in Greenland
        available_deduction_data: dict = None,         # Dict of years to available deduction amounts
        foreign_paid_amount: int = 0,                  # Amount already paid in taxes in foreign country
        adjust_for_days_in_year: bool = True           # Perform adjustment for taxable days in year (false if self-reported)
    ) -> dict:

        if days_in_year not in (365, 366):
            raise ValueError("Days in year must be either 365 or 366")

        if taxable_days_in_year < 0:
            raise ValueError("Taxable days must be zero or higher")

        if taxable_days_in_year > days_in_year:
            raise ValueError("More taxable days than days in year")

        if available_deduction_data is None:
            available_deduction_data = {}

        for year, amount in available_deduction_data.items():
            if amount < 0:
                raise ValueError("Negative return should be specified using a positive number")

        if foreign_paid_amount < 0:
            raise ValueError("Foreign paid amount must be zero or higher")

        # Calculate taxable days adjust factor
        if adjust_for_days_in_year:
            tax_days_adjust_factor = taxable_days_in_year / days_in_year
        else:
            tax_days_adjust_factor = 1

        # Make sure initial amount is an integer
        initial_amount = int(initial_amount)

        # Adjust for taxable days. Round down because we only operate in integer amounts of money
        year_adjusted_amount = math.floor(initial_amount * tax_days_adjust_factor)

        taxable_amount = max(0, year_adjusted_amount)
        used_negative_return = 0
        desired_deduction_data = {}
        # Given the available_deduction_data dict, calculate how much deduction we want
        if taxable_amount > 0:
            for year, amount in sorted(available_deduction_data.items(), key=lambda kvp: kvp[0]):
                if amount > 0:
                    used_amount = min(amount, taxable_amount)
                    taxable_amount -= used_amount
                    used_negative_return += used_amount
                    desired_deduction_data[year] = used_amount
                    if taxable_amount == 0:
                        break

            # Taxable amount
            assert taxable_amount == year_adjusted_amount - used_negative_return

        # The amount of negative return that can actually be used
        available_negative_return = sum(available_deduction_data.values())

        # Calculate the tax
        full_tax = math.floor(taxable_amount * settings.KAS_TAX_RATE)

        tax_with_deductions = max(0, full_tax - max(0, foreign_paid_amount))

        return {
            "initial_amount": initial_amount,
            "days_in_year": days_in_year,
            "taxable_days_in_year": taxable_days_in_year,
            "foreign_paid_amount": foreign_paid_amount,
            "tax_days_adjust_factor": tax_days_adjust_factor,
            "year_adjusted_amount": year_adjusted_amount,
            "available_negative_return": available_negative_return,
            "used_negative_return": used_negative_return,
            "taxable_amount": taxable_amount,
            "full_tax": full_tax,
            "tax_with_deductions": tax_with_deductions,
            "desired_deduction_data": desired_deduction_data,
            "adjust_for_days_in_year": adjust_for_days_in_year,
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

    def get_calculation(self):
        return PolicyTaxYear.perform_calculation(
            self.initial_amount,
            days_in_year=self.tax_year.days_in_year,
            taxable_days_in_year=self.person_tax_year.number_of_days,
            available_deduction_data=self.calculate_available_yearly_deduction(),
            foreign_paid_amount=self.foreign_paid_amount_actual,
            adjust_for_days_in_year=self.active_amount != self.ACTIVE_AMOUNT_SELF_REPORTED
        )

    def calculate_available_yearly_deduction(self):
        available = {}
        qs = self.previous_years_qs().filter(year_adjusted_amount__lt=0).order_by('person_tax_year__tax_year__year')
        # Loop over prior years, using deductible amounts from them until either we have used it all, or nothing more is needed
        for policy in qs.iterator():
            result = policy.payouts_using.exclude(used_for=self.id).aggregate(Sum('transferred_negative_payout'))
            used = result['transferred_negative_payout__sum'] or 0
            available[policy.year] = (-policy.year_adjusted_amount) - used  # Positive value
        return available

    def recalculate(self):
        self.payouts_used.all().delete()
        result = self.get_calculation()

        other_policies = {policy.year: policy for policy in self.previous_years_qs()}
        for year, amount in result['desired_deduction_data'].items():
            other_policies[year].use_amount(amount, self)

        self.year_adjusted_amount = result["year_adjusted_amount"]
        self.calculated_full_tax = result["full_tax"]
        self.calculated_result = result["tax_with_deductions"]
        self.available_negative_return = result["available_negative_return"]
        self.save()

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

        available_to_be_used_amount = (-self.year_adjusted_amount) - self.sum_of_used_amount()
        to_be_used_amount = min(available_to_be_used_amount, use_up_to_amount)

        item, created = PreviousYearNegativePayout.objects.get_or_create(
            used_from=self,
            used_for=deducting_policy_tax_year
        )
        item.transferred_negative_payout += to_be_used_amount
        item.save()
        return to_be_used_amount

    @property
    def available_deduction_from_previous_years(self):
        if self.available_negative_return is None:
            self.available_negative_return = sum(self.calculate_available_yearly_deduction().values())
        return self.available_negative_return

    @property
    def applied_deduction_from_previous_years(self):
        # Return the amount of deductions used by this policy (losses from other years used as deductions in this year)
        result = self.payouts_used.aggregate(Sum('transferred_negative_payout'))
        return result['transferred_negative_payout__sum'] or 0

    @property
    def previous_year_deduction_table_data(self):
        years = []
        policy_pks = []
        available_by_year = {}
        used_by_year = {}
        for_year_total = {}

        for x in self.same_policy_qs.filter(person_tax_year__tax_year__year__lte=self.year).order_by('person_tax_year__tax_year__year'):
            years.append(x.year)
            policy_pks.append(x.pk)
            available_by_year[x.year] = min(x.year_adjusted_amount, 0) * -1
            used_by_year[x.year] = 0
            for_year_total[x.year] = 0

        used_matrix = {}

        for x in PreviousYearNegativePayout.objects.filter(used_from__in=policy_pks, used_for__person_tax_year__tax_year__year__lte=self.year):
            if x.from_year not in used_matrix:
                used_matrix[x.from_year] = {}

            # Store used amount in matrix
            used_matrix[x.from_year][x.for_year] = x.transferred_negative_payout
            # Adjust spent amount for the from year
            used_by_year[x.from_year] = used_by_year[x.from_year] + x.transferred_negative_payout
            # Adjust used amount for the for year
            for_year_total[x.for_year] = for_year_total[x.for_year] + x.transferred_negative_payout

        result = {}

        # create a year x year table
        for x in years:
            used_in = {}

            for y in years:
                if x >= y:
                    used_in[y] = "-"
                else:
                    used_in[y] = used_matrix.get(x, {}).get(y, 0)

            result[x] = {
                'available': available_by_year[x],
                'used_by_year': used_in,
                'remaining': available_by_year[x] - used_by_year[x],
                'used_total': for_year_total[x]
            }

        return result

    @property
    def sum_of_deducted_amount(self):
        # Return the amount of this years deduction (losses used as deductions in other years)
        result = self.payouts_using.aggregate(Sum('transferred_negative_payout'))
        return result['transferred_negative_payout__sum'] or 0

    # How much deduction is still available for use on this policy
    # Returns a positive number
    @property
    def remaining_negative_amount(self):
        return max(0, (-self.year_adjusted_amount) - self.sum_of_deducted_amount)

    def recalculate_from_r75(self):
        r75qs = ImportedR75PrivatePension.objects.filter(
            cpr=self.cpr,
            tax_year=self.year,
            res=self.pension_company.res,
            ktd=self.policy_number
        )
        self.prefilled_amount = sum([int(r['renteindtaegt']) for r in r75qs.values('renteindtaegt')])
        self.save()

    def __str__(self):
        return f"{self.__class__.__name__}(policy_number={self.policy_number}, cpr={self.person.cpr}, " \
               f"year={self.tax_year.year}), prefilled_amount={self.prefilled_amount}, " \
               f"estimated_amount={self.estimated_amount}, self_reported_amount={self.self_reported_amount}, " \
               f"calculations_model_options={self.calculations_model_options}, active_amount={self.active_amount}, " \
               f"year_adjusted_amount={self.year_adjusted_amount}, calculation_model={self.calculation_model}, " \
               f"preliminary_paid_amount={self.preliminary_paid_amount}, from_pension={self.from_pension}, " \
               f"foreign_paid_amount_self_reported={self.foreign_paid_amount_self_reported}, " \
               f"foreign_paid_amount_actual={self.foreign_paid_amount_actual}, " \
               f"applied_deduction_from_previous_years={self.applied_deduction_from_previous_years}"


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

    @property
    def from_year(self):
        return self.used_from.year

    @property
    def for_year(self):
        return self.used_for.year

    def __str__(self):
        return f'used from :{self.used_from} used for :{self.used_for} payout :{self.transferred_negative_payout}'


class PolicyDocument(models.Model):
    person_tax_year = models.ForeignKey(PersonTaxYear, null=False, db_index=True, on_delete=models.PROTECT)
    uploaded_by = models.ForeignKey(get_user_model(), null=True, on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    policy_tax_year = models.ForeignKey(
        PolicyTaxYear,
        on_delete=models.PROTECT,
        null=True,
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


class Note(models.Model):

    class Meta:
        ordering = ['date']

    person_tax_year = models.ForeignKey(
        PersonTaxYear,
        null=False,
        on_delete=models.CASCADE,
        related_name='notes',
    )

    policy_tax_year = models.ForeignKey(
        PolicyTaxYear,
        null=True,
        on_delete=models.SET_NULL,
        related_name='notes',
    )

    date = models.DateTimeField(
        auto_now_add=True,
    )

    author = models.ForeignKey(
        User,
        null=False,
        on_delete=models.PROTECT,
    )

    content = models.TextField(
        verbose_name=_('Tekst'),
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
