from django import forms
from django.utils.translation import gettext as _

from kas.forms_mixin import BootstrapForm
from kas.models import TaxYear
from worker.job_registry import get_job_types


class JobTypeSelectForm(BootstrapForm):
    job_type = forms.ChoiceField(choices=[], required=True, label=_('Job type'))

    def __init__(self, *args, **kwargs):
        super(JobTypeSelectForm, self).__init__(*args, **kwargs)
        self.fields['job_type'].choices = [(k, v['label']) for k, v in get_job_types().items()
                                           if not v.get('not_in_dropdown')]


class YearForm(BootstrapForm):
    year = forms.IntegerField(
        label=_('År'),
        widget=forms.Select(choices=[(2006, 2006)])
    )

    class Meta:
        fields = ('year', )

    def __init__(self, *args, **kwargs):
        super(YearForm, self).__init__(*args, **kwargs)

        self.fields['year'].widget.choices = [
            (x.year, x.year) for x in TaxYear.objects.all().order_by("year")
        ]


class YearFormWithAll(BootstrapForm):
    year = forms.CharField(
        label=_('År'),
        widget=forms.Select(choices=[(2006, 2006)])
    )

    class Meta:
        fields = ('year', )

    def __init__(self, *args, **kwargs):
        super(YearFormWithAll, self).__init__(*args, **kwargs)

        self.fields['year'].widget.choices = [
            (x.year, x.year) for x in TaxYear.objects.all().order_by("year")
        ] + [
            ('all', _('Alle år'))
        ]


class MandtalImportJobForm(YearForm):
    pass


class R75ImportJobForm(YearForm):
    pass


class YearPkForm(BootstrapForm):
    year_pk = forms.ChoiceField(choices=[], required=True, label=_('År'))

    def __init__(self, *args, **kwargs):
        super(YearPkForm, self).__init__(*args, **kwargs)
        self.fields['year_pk'].choices = ((year.pk, str(year.year)) for year in TaxYear.objects.all())


class AutoligningsYearForm(BootstrapForm):
    year_pk = forms.ChoiceField(choices=[], required=True, label=_('År'))

    def __init__(self, *args, **kwargs):
        super(AutoligningsYearForm, self).__init__(*args, **kwargs)
        self.fields['year_pk'].choices = ((year.pk, '{} ({})'.format(year.year, year.year_part)) for year
                                          in TaxYear.objects.filter(year_part='selvangivelse'))


class YearAndTitleForm(YearPkForm):
    title = forms.CharField(label=_('Titel'), help_text=_('Vil blive brugt som titelfeltet i e-boks'))


# A simple form with just confirm or cancel submit buttons
class ConfirmForm(BootstrapForm):
    # A simple form with just confirm or cancel submit buttons
    pass
