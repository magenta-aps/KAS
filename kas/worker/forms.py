from django import forms
from django.conf import settings
from worker.job_registry import get_job_types
from kas.forms_mixin import BootstrapForm
from django.utils.translation import gettext as _
from kas.models import TaxYear


class JobTypeSelectForm(BootstrapForm):
    job_type = forms.ChoiceField(choices=[], required=True, label=_('Job type'))

    def __init__(self, *args, **kwargs):
        super(JobTypeSelectForm, self).__init__(*args, **kwargs)
        self.fields['job_type'].choices = ((k, v['label'])for k, v in get_job_types().items())


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


class YearAndSourceForm(YearForm):
    source_model = forms.ChoiceField(
        label=_('Datakilde'),
        choices=(
            ('mockup', _('Mock-up data')),
            ('eskat', _('Den rigtige eSkat database')),
        )
    )

    def __init__(self, *args, **kwargs):
        super(YearAndSourceForm, self).__init__(*args, **kwargs)

        if settings.ENVIRONMENT == "production":
            self.fields['source_model'].widget.choices = (
                ('eskat', _('Den rigtige eSkat database')),
            )


class MandtalImportJobForm(YearAndSourceForm):
    pass


class R75ImportJobForm(YearAndSourceForm):
    pass


class YearPkForm(BootstrapForm):
    year_pk = forms.ChoiceField(choices=[], required=True)

    def __init__(self, *args, **kwargs):
        super(YearPkForm, self).__init__(*args, **kwargs)
        self.fields['year_pk'].choices = ((year.pk, str(year)) for year in TaxYear.objects.all())


class DispatchTaxYearForm(BootstrapForm):
    title = forms.CharField(label=_('Titel'), help_text=_('Vil blive brugt som title feltet i e-boks'))


# A simple form with just confirm or cancel submit buttons
class ConfirmForm(BootstrapForm):
    # A simple form with just confirm or cancel submit buttons
    pass
