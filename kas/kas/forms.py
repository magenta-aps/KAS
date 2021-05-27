import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms import CheckboxInput
from django.utils import timezone
from django.utils.translation import gettext as _
from kas.forms_mixin import BootstrapForm
from kas.models import PersonTaxYear, PolicyTaxYear, Note, PolicyDocument, PensionCompany, TaxYear
from kas.fields import PensionCompanyChoiceField, DateInput


class PersonListFilterForm(BootstrapForm):

    year = forms.IntegerField(label=_('År'), required=False, widget=forms.Select())
    cpr = forms.CharField(label=_('Personnummer'), required=False)
    name = forms.CharField(label=_('Navn'), required=False)
    municipality_code = forms.IntegerField(label=_('Kommunekode'), required=False)
    municipality_name = forms.CharField(label=_('Kommunenavn'), required=False)
    address = forms.CharField(label=_('Adresse'), required=False)
    tax_liability = forms.NullBooleanField(
        label=_('Skattepligt'),
        widget=forms.Select(  # NullBooleanSelect doesn't quite give us what we need
            choices=[(False, _('Ikke fuldt skattepligtig')), (True, _('Fuldt skattepligtig')), (None, _('Alle'))],
        )
    )
    foreign_pension_notes = forms.NullBooleanField(
        label=_('Noter om indbetaling i udlandet'),
        widget=forms.Select(  # NullBooleanSelect doesn't quite give us what we need
            choices=[(False, _('Har ikke noter')), (True, _('Har noter')), (None, _('Alle'))],
        )
    )

    def __init__(self, *args, **kwargs):
        super(PersonListFilterForm, self).__init__(*args, **kwargs)
        years = [tax_year.year for tax_year in TaxYear.objects.order_by('year')]
        self.fields['year'].widget.choices = [
            (year, year) for year in years
        ]
        current_year = timezone.now().year
        self.fields['year'].initial = current_year \
            if current_year in years \
            else max([y for y in years if y < current_year])
        self.fields['tax_liability'].initial = None
        self.fields['foreign_pension_notes'].initial = None

    def clean_cpr(self):
        cpr = self.cleaned_data['cpr']
        if cpr and not re.match(r'\d', cpr):
            raise ValidationError(_('Ugyldigt cpr-nummer'))
        cpr = re.sub(r'\D', '', cpr)
        return cpr


class PolicyListFilterForm(BootstrapForm):

    year = forms.IntegerField(label=_('År'), required=False, widget=forms.Select())
    pension_company = forms.CharField(label=_('Pensionsselskab'), required=False)
    policy_number = forms.CharField(label=_('Policenummer'), required=False)

    def __init__(self, *args, **kwargs):
        super(PolicyListFilterForm, self).__init__(*args, **kwargs)
        years = [tax_year.year for tax_year in TaxYear.objects.order_by('year')]
        self.fields['year'].widget.choices = [
            (year, year) for year in years
        ]


class PersonNotesAndAttachmentForm(forms.ModelForm, BootstrapForm):
    note = forms.CharField(widget=forms.Textarea(attrs={'placeholder': _('Nyt notat')}), required=False, )
    attachment = forms.FileField(required=False)
    attachment_description = forms.CharField(required=False,
                                             widget=forms.TextInput(attrs={'placeholder': _('Fil-beskrivelse')}))

    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        self.user = user

    class Meta:
        model = PersonTaxYear
        fields = []

    def save(self, commit=True):
        instance = super().save(False)  # no reason to trigger a re-save when nothing was changed
        if self.cleaned_data['note']:
            Note(
                person_tax_year=instance,
                author=self.user,
                content=self.cleaned_data['note']
            ).save()
        if self.cleaned_data['attachment']:
            PolicyDocument.objects.create(person_tax_year=instance,
                                          description=self.cleaned_data.get('attachment_description', ''),
                                          name=self.cleaned_data['attachment'].name,
                                          uploaded_by=self.user,
                                          file=self.cleaned_data['attachment'])
        return instance


class PolicyNotesAndAttachmentForm(forms.ModelForm, BootstrapForm):
    attachment = forms.FileField(required=False)
    attachment_description = forms.CharField(required=False,
                                             widget=forms.TextInput(attrs={'placeholder': _('Fil-beskrivelse')}))
    note = forms.CharField(widget=forms.Textarea(attrs={'placeholder': _('Nyt notat')}),
                           required=False)

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user')
        year_part = kwargs.pop('year_part')
        super().__init__(**kwargs)
        if year_part in ('ligning', 'genoptagelsesperiode'):
            # add slutlignet checkbox
            self.fields['slutlignet'] = forms.BooleanField(required=False, label=_('Markér som slutlignet'),
                                                           widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
        if year_part == 'ligning':
            self.fields['efterbehandling'] = forms.BooleanField(required=False, label=_('Markér til efterbehandling'),
                                                                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def save(self, commit=True):
        instance = super().save(commit)
        if self.cleaned_data['note']:
            Note(
                person_tax_year=instance.person_tax_year,
                policy_tax_year=instance,
                author=self.user,
                content=self.cleaned_data['note']
            ).save()
        if self.cleaned_data['attachment']:
            PolicyDocument.objects.create(policy_tax_year=instance,
                                          person_tax_year=instance.person_tax_year,
                                          description=self.cleaned_data.get('attachment_description', ''),
                                          name=self.cleaned_data['attachment'].name,
                                          uploaded_by=self.user,
                                          file=self.cleaned_data['attachment'])
        return instance

    class Meta:
        model = PolicyTaxYear
        fields = ['slutlignet', 'efterbehandling', 'next_processing_date']
        widgets = {
            'slutlignet': CheckboxInput(attrs={'class': 'form-check-input'}),
            'next_processing_date': DateInput()
        }


class PolicyTaxYearActivationForm(forms.ModelForm):
    class Meta:
        model = PolicyTaxYear
        fields = ['active']


class NoteForm(forms.ModelForm, BootstrapForm):
    content = forms.CharField(required=False,
                              label=_('Notat'),
                              widget=forms.Textarea(attrs={'placeholder': _('Nyt notat'),
                                                           'autocomplete': 'off'}))

    class Meta:
        model = Note
        fields = ('content', )


class PolicyDocumentForm(forms.ModelForm, BootstrapForm):
    file = forms.FileField(required=True)
    description = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={'placeholder': _('Fil-beskrivelse'),
                                                                'autocomplete': 'off'}))

    class Meta:
        model = PolicyDocument
        fields = ('file', 'description')


class SelfReportedAmountForm(forms.ModelForm, BootstrapForm):
    self_reported_amount = forms.IntegerField(required=True,
                                              label=_('Selvangivet beløb'),
                                              widget=forms.NumberInput(attrs={'placeholder': _('Selvangivet beløb')}))

    class Meta:
        model = PolicyTaxYear
        fields = ('self_reported_amount', 'next_processing_date')
        widgets = {'next_processing_date': DateInput()}


class EditAmountsUpdateForm(forms.ModelForm, BootstrapForm):

    def __init__(self, *args, **kwargs):
        super(EditAmountsUpdateForm, self).__init__(*args, **kwargs)
        self.original_efterbehandling = self.instance.efterbehandling
        if self.instance.efterbehandling is True:
            self.fields['efterbehandling'].disabled = True
            # add tooltip
            self.fields['efterbehandling'].widget.attrs['title'] = _('Fjern markering ved at slutligne.')
            self.fields['efterbehandling'].widget.attrs['data-toggle'] = 'tooltip'
            self.fields['efterbehandling'].widget.attrs['data-placement'] = 'top'

    def clean_efterbehandling(self):
        if self.original_efterbehandling is True:
            return True
        else:
            return self.cleaned_data['efterbehandling']

    def clean(self):
        if self.cleaned_data['slutlignet'] is True and 'slutlignet' in self.changed_data:
            if self.cleaned_data['efterbehandling']:
                self.cleaned_data['efterbehandling'] = False
        return self.cleaned_data

    class Meta:
        model = PolicyTaxYear
        fields = ('adjusted_r75_amount', 'self_reported_amount', 'assessed_amount', 'slutlignet', 'efterbehandling', 'next_processing_date')
        widgets = {'next_processing_date': DateInput()}


class PensionCompanySummaryFileForm(BootstrapForm):
    pension_company = PensionCompanyChoiceField(
        queryset=PensionCompany.objects.filter(agreement_present=True),
    )


class CreatePolicyTaxYearForm(forms.ModelForm, BootstrapForm):
    class Meta:
        model = PolicyTaxYear
        fields = [
            'pension_company',
            'policy_number',
            'self_reported_amount',
        ]
    pension_company = PensionCompanyChoiceField(
        queryset=PensionCompany.objects.all(),
        widget=forms.widgets.Select()
    )
