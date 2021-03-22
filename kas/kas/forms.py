from django import forms
from kas.forms_mixin import BootstrapForm
from django.utils.translation import gettext as _


class PersonListFilterForm(BootstrapForm):
    cpr = forms.CharField(label=_('Cpr'), required=False)
    name = forms.CharField(label=_('Navn'), required=False)
