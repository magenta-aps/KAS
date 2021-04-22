from django.forms import ModelForm, ChoiceField

from kas.forms_mixin import BootstrapForm
from prisme.models import Transaction
from prisme.models import transaction_types


class TransActionForm(BootstrapForm, ModelForm):
    type = ChoiceField(choices=transaction_types)

    class Meta:
        model = Transaction
        fields = ('amount', 'type')
