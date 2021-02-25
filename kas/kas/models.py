from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, RegexValidator, \
    MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext as _


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


class Person(models.Model):

    cpr = models.TextField(
        db_index=True,
        verbose_name=_('CPR nummer'),
        help_text=_('CPR nummer'),
        unique=True,
        null=False,
        max_length=10,
        validators=(RegexValidator(regex=r'\d{10}'),)
    )

    def __str__(self):
        return f"{self.__class__.__name__}(cpr={self.cpr})"


class PersonTaxYear(models.Model):

    class Meta:
        unique_together = ['tax_year', 'person']

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

    start_date = models.DateField(
        verbose_name='Startdato',
        null=True
    )

    end_date = models.DateField(
        verbose_name='Slutdato',
        null=True
    )

    number_of_days = models.IntegerField(
        verbose_name='Antal dage',
        null=True
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

    deduction_from_previous_years = models.BigIntegerField(
        verbose_name=_('Fradrag fra tidligere år'),
        blank=True,
        default=0,
        validators=(MinValueValidator(limit_value=0),)
    )

    applied_deduction_from_previous_years = models.BigIntegerField(
        verbose_name=_('Anvendt fradrag fra tidligere år'),
        blank=True,
        default=0,
        validators=(MinValueValidator(limit_value=0),)
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

    @property
    def person(self):
        return self.person_tax_year.person

    @property
    def tax_year(self):
        return self.person_tax_year.tax_year

    def __str__(self):
        return f"{self.__class__.__name__}(policy_number={self.policy_number}, cpr={self.person.cpr}, year={self.tax_year.year})"


class PolicyDocument(models.Model):

    policy_tax_year = models.ForeignKey(
        PolicyTaxYear,
        on_delete=models.PROTECT,
        null=False
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_('Navn'),
        blank=False
    )

    description = models.TextField(
        verbose_name=_('Beskrivelse'),
    )

    file = models.FileField(
        verbose_name=_('Fil'),
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
