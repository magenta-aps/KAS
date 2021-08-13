from functools import cached_property
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator
from django.db import models
from django.template.defaultfilters import date as _date
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext as _

from prisme.tenQ.writer import TenQTransactionWriter

transaction_status = (
    ('created', _('Oprettet')),
    ('ready', _('Klar til overførsel')),
    ('transferred', _('Overført')),
    ('cancelled', _('Annulleret')),
)
transaction_types = (
    ('prisme10q', _('Prisme opkrævning / tilbagebetaling')),
    ('prepayment', _('Forudindbetaling'))
)


class Transaction(models.Model):
    class Meta:
        ordering = ['created_at', 'uuid']
        verbose_name = _('transaktion')
        verbose_name_plural = _('transaktionr')

    uuid = models.UUIDField(primary_key=True, default=uuid4)
    person_tax_year = models.ForeignKey('kas.PersonTaxYear', null=False, db_index=True, on_delete=models.PROTECT)
    # Positive amount means something the person must pay, negative means something that should be paid back to the user
    amount = models.IntegerField(null=False, blank=False)  # prisme only uses negative og positive integers not decimals.
    status = models.TextField(choices=transaction_status, default='created', blank=True)
    type = models.TextField(choices=transaction_types)
    created_at = models.DateTimeField(auto_now_add=True)
    source_content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)  # Model class of the source
    object_id = models.TextField()  # id of the sources
    source_object = GenericForeignKey('source_content_type', 'object_id')  # FK to the object who created the transaction

    # The batch of Prisme 10Q transactions this belongs to
    prisme10Q_batch = models.ForeignKey('Prisme10QBatch', null=True, default=None, on_delete=models.PROTECT)
    # A summary of how the amount was calculated, used for debug puposes
    summary = models.TextField(blank=True, default='')
    # The three 10Q transaction lines generated for this transaction
    prisme10Q_content = models.TextField(blank=True, default='')

    def update_prisme10Q_content(self):

        if self.type != 'prisme10q':
            raise ValueError("Cannot update 10Q content for transaction that is not of type 'prisme10q'")

        transaction_writer = self.prisme10Q_batch.transaction_writer

        self.prisme10Q_content = transaction_writer.serialize_transaction(
            cpr_nummer=self.person_tax_year.person.cpr,
            amount_in_dkk=self.amount,
            afstem_noegle=str(self.uuid).replace('-', '')
        )

    def __str__(self):
        return '{type} for {person} på {amount} i {year}'.format(type=self.get_type_display(),
                                                                 person=self.person_tax_year.person.name,
                                                                 amount=self.amount,
                                                                 year=self.person_tax_year.tax_year.year)


def payment_file_by_year(instance, filename):
    # uploaded_at is not set yet hence we use timezone.now()
    return 'pre_payments/{year}/{pk}'.format(year=timezone.now().year, pk=instance.pk)


class PrePaymentFile(models.Model):
    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=payment_file_by_year,
                            validators=[FileExtensionValidator(allowed_extensions=['csv'])])

    def __str__(self):
        return 'Forudindbetalingsfil uploadet {date} af {by}'.format(date=date_format(self.uploaded_at, 'SHORT_DATETIME_FORMAT'),
                                                                     by=self.uploaded_by)


batch_destinations_all = (
    ('10q_development', _('Undervisningssystem')),
    ('10q_production', _('Produktionssystem')),
)

# Which destinations should be available for each of our environments
batch_destinations_available = tuple([
    tuple([destination_id, label])
    for destination_id, label in batch_destinations_all
    if destination_id in settings.TENQ['destinations'][settings.ENVIRONMENT]
])


class Prisme10QBatch(models.Model):
    class Meta:
        ordering = ['created']
        verbose_name = _('prisme 10Q batch')
        verbose_name_plural = _('prisme 10Q batches')

    _cached_transaction_writer = None

    # When was the batch created
    created = models.DateTimeField(auto_now=True)
    # Who created the batch
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='created_prisme_batches',
    )
    # When was the batch delivered
    delivered = models.DateTimeField(blank=True, null=True)
    # Who delivered the batch
    delivered_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='delivered_prisme_batches',
    )
    # Any error encountered while trying to deliver the batch
    delivery_error = models.TextField(blank=True, default='')

    collect_date = models.DateTimeField(null=True)

    # Status for delivery
    STATUS_CREATED = 'created'
    STATUS_DELIVERING = 'delivering'
    STATUS_DELIVERY_FAILED = 'failed'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    status_choices = (
        (STATUS_CREATED, _('Ikke afsendt')),
        (STATUS_DELIVERING, _('Afsender')),
        (STATUS_DELIVERY_FAILED, _('Afsendelse fejlet')),
        (STATUS_DELIVERED, _('Afsendt')),
        (STATUS_CANCELLED, _('Annulleret'))
    )

    status = models.CharField(
        choices=status_choices,
        default=STATUS_CREATED,
        max_length=15
    )

    tax_year = models.ForeignKey('kas.TaxYear', on_delete=models.PROTECT)

    @property
    def active_transactions_qs(self):
        return self.transaction_set.exclude(
            status='cancelled'
        ).exclude(
            amount__gt=-100,
            amount__lt=100
        )

    def get_content(self, max_entries=None):
        qs = self.active_transactions_qs
        if max_entries is not None:
            qs = qs[:max_entries]
        return '\r\n'.join([
            x.prisme10Q_content for x in qs
        ])

    def add_transaction(self, final_settlement):
        if final_settlement.person_tax_year.tax_year != self.tax_year:
            raise ValueError(
                "Cannot add final settlement to 10Q batch: Wrong tax year {tax_year}".format(
                    tax_year=final_settlement.person_tax_year.tax_year.year
                )
            )

        new_entry = Transaction(
            person_tax_year=final_settlement.person_tax_year,
            amount=final_settlement.get_transaction_amount(),
            type='prisme10q',
            source_object=final_settlement,
            prisme10Q_batch=self,
            summary=final_settlement.get_transaction_summary(),
        )

        new_entry.update_prisme10Q_content()

        new_entry.save()

    @cached_property
    def transaction_writer(self):
        return TenQTransactionWriter(
            collect_date=self.collect_date or self.created,
            year=self.tax_year.year,
        )

    def __str__(self) -> str:
        return _('Prisme 10Q bunke {tidsstempel} ({status})').format(
            tidsstempel=_date(self.created, "SHORT_DATETIME_FORMAT"),
            status=self.get_status_display()
        )
