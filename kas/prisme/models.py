from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext as _

from kas.models import PersonTaxYear
from prisme.10Q.writer import TransactionWriter

transaction_status = (
    ('created', _('Oprettet')),
    ('ready', _('Klar til overførsel')),
    ('transferred', _('Overført'))
)
transaction_types = (
    ('charge', _('Opkrævning')),
    ('repayment', _('Tilbagebetaling')),
    ('adjustment', _('Justering')),
    ('prepayment', _('Forudindbetaling'))
)


class Transaction(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    person_tax_year = models.ForeignKey(PersonTaxYear, null=False, db_index=True, on_delete=models.PROTECT)
    amount = models.IntegerField(null=False, blank=False)  # prisme only uses negative og positive integers not decimals.
    status = models.TextField(choices=transaction_status, default='created', blank=True)
    type = models.TextField(choices=transaction_types)
    created_at = models.DateTimeField(auto_now_add=True)
    transferred_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True,
                                       related_name='transfered_transactions')  # Who transfered this to prisme
    transferred_at = models.DateTimeField(null=True, blank=True)
    source_content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)  # Model class of the source
    object_id = models.TextField()  # id of the sources
    source_object = GenericForeignKey('source_content_type', 'object_id')  # FK to the object who created the transaction

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


class Prisme10QBatch(models.Model):
    class Meta:
        ordering = ['created']
        verbose_name = _('prisme 10Q batch')
        verbose_name_plural = _('prisme 10Q batches')


    _cached_transaction_writer = None

    # When was the batch created
    created = models.DateTimeField(auto_now=True)
    # When was the batch delivered
    delivered = models.DateTimeField(blank=True, none=True)
    # Any error encountered while trying to deliver the batch
    delivery_error = models.TextField(blank=True, default='')

    # Status for delivery
    STATUS_CREATED = 1
    STATUS_DELIVERY_FAILED = 1
    STATUS_DELIVERED = 1

    status_choices = (
        (STATUS_CREATED, _('Oprettet')),
        (STATUS_DELIVERY_FAILED, _('Afsendelse fejlet')),
        (STATUS_DELIVERED, _('Afsendt'))
    )

    status = models.IntegerField(
        choices=status_choices,
        default=STATUS_CREATED
    )

    tax_year = models.IntegerField()

    def add_entry(self, final_settlement, transaction_writer=None):
        if final_settlement.person_tax_year.tax_year.year != self.tax_year:
            raise ValueError(
                "Cannot add final settlement to 10Q batch: Wrong tax year %s" % (
                    final_settlement.person_tax_year.tax_year.year
                )
            )

        new_entry = Prisme10QTransactionEntry(
            final_settlement=final_settlement,
            batch=self,
            amount=final_settlement.get_transaction_amount(),
            summary=final_settlement.get_transaction_summary(),
        )
        new_entry.update_content()
        new_entry.save()


    def get_transaction_writer(self):
        if self._cached_transaction_writer is None:
            self._cached_transaction_writer = TransactionWriter(
                ref_timestamp=self.created,
                tax_year=self.tax_year,
            )

        return self._cached_transaction_writer


class Prisme10QTransactionEntry(models.Model):
    class Meta:
        ordering = ['pk']
        verbose_name = _('prisme 10Q transaktion')
        verbose_name_plural = _('prisme 10Q transaktioner')

    # The final settlement this is the transaction for
    final_settlement = models.ForeignKey('kas.FinalSettlement')
    # The batch of Prisme 10Q transactions this belongs to
    batch = models.ForeignKey(Prisme10QBatch)
    # The amount needed to be paid / refunded
    amount = models.IntegerField()
    # A summary of how the amount was calculated, used for debug puposes
    summary = models.TextField(blank=True, default='')
    # The three 10Q transaction lines generated for this transaction
    content = models.TextField(blank=True, default='')

    def update_content(self):
        transaction_writer = self.batch.get_transaction_writer()

        self.content = transaction_writer.make_transaction(
            cpr_nummer=self.final_settlement.person_tax_year.person.cpr,
            rate_beloeb=self.amount,
            afstem_noegle=self.final_settlement.uuid
        )
