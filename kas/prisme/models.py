from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator
from django.db import models
from django.template.defaultfilters import date as _date
from django.urls import reverse
from django.utils import timezone, dateformat
from django.utils.formats import date_format
from django.utils.translation import gettext as _

from prisme.tenQ.writer import TransactionWriter

transaction_status = (
    ('created', _('Oprettet')),
    ('ready', _('Klar til overførsel')),
    ('transferred', _('Overført')),
    ('cancelled', _('Annuleret')),
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

        transaction_writer = self.prisme10Q_batch.get_transaction_writer()

        self.prisme10Q_content = transaction_writer.make_transaction(
            cpr_nummer=self.person_tax_year.person.cpr,
            amount_in_dkk=self.amount,
            afstem_noegle=str(self.uuid).replace('-', '')
        )

    def get_batch_link(self):
        if self.type == 'prisme10q':
            return '<a href="{link}">{batch}</a>'.format(
                link=reverse('prisme:prisme-batch', kwargs={'pk': self.prisme10Q_batch.pk}),
                batch=self.prisme10Q_batch
            )
        return None

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

    # Status for delivery
    STATUS_CREATED = 1
    STATUS_DELIVERY_FAILED = 2
    STATUS_DELIVERED = 3

    status_choices = (
        (STATUS_CREATED, _('Ikke afsendt')),
        (STATUS_DELIVERY_FAILED, _('Afsendelse fejlet')),
        (STATUS_DELIVERED, _('Afsendt'))
    )

    status = models.IntegerField(
        choices=status_choices,
        default=STATUS_CREATED
    )

    tax_year = models.ForeignKey('kas.TaxYear', on_delete=models.PROTECT)

    @property
    def active_transactions_qs(self):
        return self.transaction_set.exclude(
            status='cancelled'
        )

    def get_content(self):
        return '\r\n'.join([
            x.prisme10Q_content for x in self.active_transactions_qs
        ])

    def add_transaction(self, final_settlement, transaction_writer=None):
        if final_settlement.person_tax_year.tax_year != self.tax_year:
            raise ValueError(
                "Cannot add final settlement to 10Q batch: Wrong tax year %s" % (
                    final_settlement.person_tax_year.tax_year.year
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

    def get_transaction_writer(self):
        if self._cached_transaction_writer is None:
            self._cached_transaction_writer = TransactionWriter(
                ref_timestamp=self.created,
                tax_year=self.tax_year.year,
            )

        return self._cached_transaction_writer


    def __str__(self) -> str:
        return _('Prisme 10Q bunke %s (%s)') % (
            _date(self.created, "SHORT_DATETIME_FORMAT"),
            self.get_status_display()
        )