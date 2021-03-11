from django import forms
from worker.job_registry import get_job_types
from kas.forms_mixin import BootstrapForm
from django.utils.translation import gettext as _


class JobTypeSelectForm(BootstrapForm):
    job_type = forms.ChoiceField(choices=[], required=True, label=_('Job type'))

    def __init__(self, *args, **kwargs):
        super(JobTypeSelectForm, self).__init__(*args, **kwargs)
        self.fields['job_type'].choices = ((k, v['label'])for k, v in get_job_types().items())


class YearForm(BootstrapForm):
    year = forms.IntegerField(min_value=2000, label=_('År'))

    class Meta:
        fields = ('year', )


class MandtalImportJobForm(YearForm):
    pass


class R75ImportJobForm(YearForm):
    pass
