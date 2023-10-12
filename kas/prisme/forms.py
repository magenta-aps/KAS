from django.forms import ChoiceField, FileField, FileInput, Form, ModelForm
from django.utils.translation import gettext as _

from kas.forms_mixin import BootstrapForm

from prisme.models import (  # isort: skip
    PrePaymentFile,
    Transaction,
    batch_destinations_available,
    transaction_types,
)


class TransActionForm(BootstrapForm, ModelForm):
    type = ChoiceField(choices=transaction_types)

    class Meta:
        model = Transaction
        fields = ("amount", "type")


class PrePaymentFileModelForm(BootstrapForm, ModelForm):
    file = FileField(widget=FileInput(attrs={"accept": "text/csv"}))

    class Meta:
        model = PrePaymentFile
        fields = ("file",)


class BatchSendForm(BootstrapForm, Form):
    destination = ChoiceField(
        label=_("Destination"), choices=batch_destinations_available
    )
