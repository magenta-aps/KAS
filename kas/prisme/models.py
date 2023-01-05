import uuid
from functools import cached_property
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator
from django.db import models
from django.template.defaultfilters import date as _date
from django.utils.formats import date_format
from django.utils.translation import gettext as _
from tenQ.writer import TenQTransactionWriter


def filefield_path(instance, filename):
    return filename


transaction_status = (
    ("created", _("Oprettet")),
    ("ready", _("Klar til overførsel")),
    ("transferred", _("Overført")),
    ("cancelled", _("Annulleret")),
    ("indifferent", _("Afregnes ikke")),
)
transaction_types = (
    ("prisme10q", _("Prisme opkrævning / tilbagebetaling")),
    ("prepayment", _("Forudindbetaling")),
)


class Transaction(models.Model):
    class Meta:
        ordering = ["created_at", "uuid"]
        verbose_name = _("transaktion")
        verbose_name_plural = _("transaktioner")

    uuid = models.UUIDField(primary_key=True, default=uuid4)
    person_tax_year = models.ForeignKey(
        "kas.PersonTaxYear", null=False, db_index=True, on_delete=models.PROTECT
    )
    # Positive amount means something the person must pay, negative means something that should be paid back to the user
    amount = models.IntegerField(
        null=False, blank=False
    )  # prisme only uses negative og positive integers not decimals.
    status = models.TextField(choices=transaction_status, default="created", blank=True)
    type = models.TextField(choices=transaction_types)
    created_at = models.DateTimeField(auto_now_add=True)
    source_content_type = models.ForeignKey(
        ContentType, on_delete=models.PROTECT
    )  # Model class of the source
    object_id = models.TextField()  # id of the sources
    source_object = GenericForeignKey(
        "source_content_type", "object_id"
    )  # FK to the object who created the transaction

    # The batch of Prisme 10Q transactions this belongs to
    prisme10q_batch = models.ForeignKey(
        "Prisme10QBatch", null=True, default=None, on_delete=models.PROTECT
    )
    # A summary of how the amount was calculated, used for debug puposes
    summary = models.TextField(blank=True, default="")
    # The three 10Q transaction lines generated for this transaction
    prisme10q_content = models.TextField(blank=True, default="")

    def update_prisme10q_content(self):

        if self.type != "prisme10q":
            raise ValueError(
                "Cannot update 10Q content for transaction that is not of type 'prisme10q'"
            )

        transaction_writer = self.prisme10q_batch.transaction_writer

        self.prisme10q_content = transaction_writer.serialize_transaction(
            cpr_nummer=self.person_tax_year.person.cpr,
            amount_in_dkk=self.amount,
            afstem_noegle=str(self.uuid).replace("-", ""),
            rate_text=self.prisme10q_batch.tax_year.rate_text_for_transactions,
        )

    def get_10q_status_display(self):
        # TODO: Have to use special case here since we do not send all transactions
        # in a batch when sending the batch. Therefore we have to use individual
        # status for the transactions when batch status is delivered.
        if self.prisme10q_batch.status == Prisme10QBatch.STATUS_DELIVERED:
            return self.get_status_display()
        else:
            return self.prisme10q_batch.get_status_display()

    def __str__(self):
        return "{type} for {person} på {amount} i {year}".format(
            type=self.get_type_display(),
            person=self.person_tax_year.person.name,
            amount=self.amount,
            year=self.person_tax_year.tax_year.year,
        )


def payment_file_by_year(instance, filename):
    return f"pre_payments/{instance.uploaded_at.year}/{uuid.uuid4()}.csv"


class PrePaymentFile(models.Model):
    class Meta:
        ordering = ["uploaded_at"]

    uploaded_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(
        upload_to=payment_file_by_year,
        validators=[FileExtensionValidator(allowed_extensions=["csv"])],
    )

    def __str__(self):
        return "Forudindbetalingsfil uploadet {date} af {by}".format(
            date=date_format(self.uploaded_at, "SHORT_DATETIME_FORMAT"),
            by=self.uploaded_by,
        )


batch_destinations_all = (
    ("10q_development", _("Undervisningssystem")),
    ("10q_production", _("Produktionssystem")),
    ("10q_mocking", _("Mocking")),
)

# Which destinations should be available for each of our environments
batch_destinations_available = tuple(
    [
        tuple([destination_id, label])
        for destination_id, label in batch_destinations_all
        if destination_id in settings.TENQ["destinations"][settings.ENVIRONMENT]
    ]
)


class Prisme10QBatch(models.Model):
    class Meta:
        ordering = ["created"]
        verbose_name = _("prisme 10Q batch")
        verbose_name_plural = _("prisme 10Q batches")

    _cached_transaction_writer = None

    # When was the batch created
    created = models.DateTimeField(auto_now=True)
    # Who created the batch
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="created_prisme_batches",
    )
    # When was the batch delivered
    delivered = models.DateTimeField(blank=True, null=True)
    # Who delivered the batch
    delivered_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="delivered_prisme_batches",
    )
    # Any error encountered while trying to deliver the batch
    delivery_error = models.TextField(blank=True, default="")

    collect_date = models.DateField(null=True)

    # Status for delivery
    STATUS_CREATED = "created"
    STATUS_DELIVERING = "delivering"
    STATUS_DELIVERY_FAILED = "failed"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    status_choices = (
        (STATUS_CREATED, _("Ikke afsendt")),
        (STATUS_DELIVERING, _("Afsender")),
        (STATUS_DELIVERY_FAILED, _("Afsendelse fejlet")),
        (STATUS_DELIVERED, _("Afsendt")),
        (STATUS_CANCELLED, _("Annulleret")),
    )

    status = models.CharField(
        choices=status_choices, default=STATUS_CREATED, max_length=15
    )

    tax_year = models.ForeignKey("kas.TaxYear", on_delete=models.PROTECT)

    @property
    def all_transactions_except_cancelled_qs(self):
        """Return all transactions which are ready to be sent"""
        return self.transaction_set.exclude(status=["cancelled"])

    @property
    def active_transactions_qs(self):
        """Return all transactions which are ready to be sent, and which are not below the indifferent limit
        Amounts below abs(TRANSACTION_INDIFFERENCE_LIMIT) are considered indifferent, and are not sent to prisme"""
        return self.transaction_set.exclude(
            status=["cancelled", "indifferent"]
        ).exclude(
            amount__gt=-settings.TRANSACTION_INDIFFERENCE_LIMIT,
            amount__lt=settings.TRANSACTION_INDIFFERENCE_LIMIT,
        )

    @property
    def transactions_below_abs100_qs(self):
        """Return all transactions which are ready to be sent, and which are below the indifferent limit
        Small amounts below abs(100) are considered indifferent and should be marked for that
        """
        return self.transaction_set.exclude(status=["cancelled", "indifferent"]).filter(
            amount__gt=-settings.TRANSACTION_INDIFFERENCE_LIMIT,
            amount__lt=settings.TRANSACTION_INDIFFERENCE_LIMIT,
        )

    def get_content(self, max_entries=None):
        qs = self.active_transactions_qs
        if max_entries is not None:
            qs = qs[:max_entries]
        return "\r\n".join([x.prisme10q_content for x in qs])

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
            type="prisme10q",
            source_object=final_settlement,
            prisme10q_batch=self,
            summary=final_settlement.get_transaction_summary(),
        )

        new_entry.update_prisme10q_content()
        new_entry.save()

    @cached_property
    def transaction_writer(self):
        due_date = self.collect_date or self.created.date()
        return TenQTransactionWriter(
            due_date=due_date,
            creation_date=due_date,
            year=self.tax_year.year,
            leverandoer_ident=settings.TENQ["project_id"],
        )

    def __str__(self) -> str:
        return _("Prisme 10Q bunke {tidsstempel} ({status})").format(
            tidsstempel=_date(self.created, "SHORT_DATETIME_FORMAT"),
            status=self.get_status_display(),
        )
