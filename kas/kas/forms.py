import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _

from kas.fields import PensionCompanyChoiceField, DateInput
from kas.forms_mixin import BootstrapForm
from kas.models import PersonTaxYear, PolicyTaxYear, Note, PolicyDocument, PensionCompany, TaxYear, FinalSettlement


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
    finalized = forms.ChoiceField(
        label=_('Slutlignede policer'),
        choices=[
            (None, _('Alle')),
            ('mangler_ikkeslutlignede', _('Slutlignet')),
            ('har_ikkeslutlignede', _('Ikke-slutlignet')),
            # ('har_slutlignede', _('Har slutlignede policer')),
            # ('mangler_slutlignede', _('Har ingen slutlignede policer')),
        ],
        required=False
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
    finalized = forms.NullBooleanField(
        label=_('Slutlignet'),
        widget=forms.Select(  # NullBooleanSelect doesn't quite give us what we need
            choices=[(True, _('Slutlignet')), (False, _('Ikke slutlignet')), (None, _('Alle'))],
        )
    )

    def __init__(self, *args, **kwargs):
        super(PolicyListFilterForm, self).__init__(*args, **kwargs)
        years = [tax_year.year for tax_year in TaxYear.objects.order_by('year')]
        self.fields['year'].widget.choices = [
            (year, year) for year in years
        ]


class NoteUpdateForm(forms.ModelForm, BootstrapForm):
    class Meta:
        model = Note
        fields = ('content',)

    def __init__(self, user, **kwargs):
        super().__init__(**kwargs)
        self.user = user

    def save(self, commit=True):
        instance = super().save(False)
        instance.author = self.user
        if commit:
            instance.save()
        return instance


class PersonNotesAndAttachmentForm(forms.ModelForm, BootstrapForm):
    note = forms.CharField(widget=forms.Textarea(attrs={'placeholder': _('Nyt notat')}), required=False, )
    attachment = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'custom-file-input'}))
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
    attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'custom-file-input'})
    )
    attachment_description = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Fil-beskrivelse')})
    )
    note = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': _('Nyt notat')}),
        required=False
    )

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(**kwargs)

    def save(self, commit=True):
        instance = super().save(False)  # avoid saving the instance twice.
        if self.cleaned_data['note'] or self.cleaned_data['attachment'] or 'next_processing_date' in self.changed_data:
            # save the instance if either one of the 2 fields where set or 'next_processing_date' where changed
            # this ensures we dont do spurious saves when none of the fields are set
            # (but validates) and the user clicks save to go back
            instance.efterbehandling = True
            instance.slutlignet = False
            instance.save()

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
        fields = ['next_processing_date']
        widgets = {
            'next_processing_date': DateInput()
        }


class PolicyTaxYearActivationForm(forms.ModelForm):
    class Meta:
        model = PolicyTaxYear
        fields = ['active']


class PolicyTaxYearCompanyForm(forms.ModelForm, BootstrapForm):
    class Meta:
        model = PolicyTaxYear
        fields = ('pension_company',)


class FinalStatementForm(forms.ModelForm, BootstrapForm):
    class Meta:
        model = FinalSettlement
        fields = [
            'interest_on_remainder',
            'extra_payment_for_previous_missing',
            'text_used_for_payment',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove the default choice used for bulk settlements
        self.fields['text_used_for_payment'].choices = [
            x for x in self.fields['text_used_for_payment'].choices
            if x[0] != FinalSettlement.PAYMENT_TEXT_BULK
        ]


class NoteForm(forms.ModelForm, BootstrapForm):
    content = forms.CharField(required=False,
                              label=_('Notat'),
                              widget=forms.Textarea(attrs={'placeholder': _('Nyt notat'),
                                                           'autocomplete': 'off'}))

    class Meta:
        model = Note
        fields = ('content', )


class PolicyDocumentForm(forms.ModelForm, BootstrapForm):
    file = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'custom-file-input'})
    )
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

    def save(self, commit=True):

        # Recalculate amounts before saving
        instance = super(SelfReportedAmountForm, self).save(commit=False)
        instance.recalculate()

        if commit:
            instance.save()

        return instance


class EditAmountsUpdateForm(forms.ModelForm, BootstrapForm):

    class Meta:
        model = PolicyTaxYear
        fields = ('adjusted_r75_amount', 'self_reported_amount', 'assessed_amount', 'slutlignet', 'next_processing_date')
        widgets = {'next_processing_date': DateInput()}

    def save(self, commit=True):

        # Recalculate amounts before saving
        instance = super(EditAmountsUpdateForm, self).save(commit=False)
        instance.recalculate()

        if commit:
            instance.save()

        return instance


class PaymentOverrideUpdateForm(forms.ModelForm, BootstrapForm):

    class Meta:
        model = PolicyTaxYear
        fields = ('citizen_pay_override', )


class PensionCompanySummaryFileForm(BootstrapForm):
    pension_company = PensionCompanyChoiceField(
        queryset=PensionCompany.objects.all(),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['self_reported_amount'].required = True


class PensionCompanyModelForm(forms.ModelForm, BootstrapForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off'}),
                           label=_('Navn'),
                           help_text=_('Pensionselskabets navn'))
    email = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    phone = forms.CharField(required=False,
                            label=_('Tlf nr'),
                            widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    agreement_present = forms.BooleanField(required=False,
                                           widget=forms.CheckboxInput(attrs={'class': 'not-form-check-input'}),
                                           label=_('Aftale'))
    agreement = forms.FileField(required=False,
                                widget=forms.FileInput())

    class Meta:
        model = PensionCompany
        fields = ('res', 'name', 'address', 'email', 'phone', 'agreement_present', 'agreement')


class PensionCompanyMergeForm(BootstrapForm):
    target = PensionCompanyChoiceField(queryset=PensionCompany.objects.all(),
                                       label=('Flet selskaber'))
    to_be_merged = forms.ModelMultipleChoiceField(queryset=PensionCompany.objects.all())

    def clean(self):
        cleaned_data = super().clean()
        if 'target' in cleaned_data and 'to_be_merged' in cleaned_data:
            if cleaned_data['target'] in cleaned_data['to_be_merged']:
                raise ValidationError(_('Du kan ikke flette %s ind i sig selv.' % cleaned_data['target'].name))
