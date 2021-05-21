

from django.forms import ModelForm, ChoiceField, FileField, FileInput

from kas.forms_mixin import BootstrapForm
from prisme.models import Transaction
from prisme.models import transaction_types, PrePaymentFile


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
