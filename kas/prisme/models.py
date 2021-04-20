from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _

from kas.models import PersonTaxYear

transaction_status = (
    ('created', _('Oprettet')),
    ('ready', _('Klar til overførsel')),
    ('transferred', _('Overført'))
)
transaction_types = (
    ('charge', _('opkrævning')),
    ('repayment', _('tilbagebetaling')),
    ('adjustment', _('justering'))
)


class Transaction(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    person_tax_year = models.ForeignKey(PersonTaxYear, null=False, db_index=True, on_delete=models.PROTECT)
    amount = models.IntegerField(null=False, blank=False)  # prisme only uses negative og positive integers not decimals.
    status = models.TextField(choices=transaction_status, default='created', blank=True)
    type = models.TextField(choices=transaction_types)
    created_by = models.ForeignKey(get_user_model(), null=True, on_delete=models.PROTECT,
                                   related_name='created_transactions')  # if nulle the transaction was created by prisme.
    created_at = models.DateTimeField(auto_now_add=True)
    transferred_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True,
                                       related_name='transfered_transactions')  # Who transfered this to prisme
    transferred_at = models.DateTimeField(null=True, blank=True)
