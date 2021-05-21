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
