from django.forms import ModelForm, ChoiceField, FileField, FileInput, Form
from django.utils.translation import gettext as _

from kas.forms_mixin import BootstrapForm
from prisme.models import Transaction, PrePaymentFile
from prisme.models import transaction_types, batch_destinations_available


class TransActionForm(BootstrapForm, ModelForm):
    type = ChoiceField(choices=transaction_types)

    class Meta:
        model = Transaction
        fields = ('amount', 'type')


class PrePaymentFileModelForm(BootstrapForm, ModelForm):
    file = FileField(widget=FileInput(attrs={'accept': 'text/csv'}))

    class Meta:
        model = PrePaymentFile
        fields = ('file', )


class BatchSendForm(BootstrapForm, Form):

    destination = ChoiceField(
        label=_('Destination'),
        choices=batch_destinations_available
    )
