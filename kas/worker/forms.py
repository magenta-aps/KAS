from django import forms

from kas.forms_mixin import BootstrapModelForm
from worker.models import job_types, Job
from django.utils.translation import gettext as _


class JobTypeSelectForm(forms.Form):
    job_type = forms.ChoiceField(choices=((k, v) for k, v in job_types.items()))


class MandtalImportJobForm(BootstrapModelForm):
    year = forms.IntegerField(min_value=2000, label=_('År'))

    class Meta:
        model = Job
        fields = ('year', )
