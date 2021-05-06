from django import forms
from django.utils.translation import gettext as _
from kas.forms_mixin import BootstrapForm
from kas.models import PersonTaxYear, PolicyTaxYear, Note, PolicyDocument, PensionCompany
from kas.fields import PensionCompanyChoiceField


class PersonListFilterForm(BootstrapForm):
    cpr = forms.CharField(label=_('Cpr'), required=False)
    name = forms.CharField(label=_('Navn'), required=False)


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
    attachment_description = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': _('Fil-beskrivelse')}))

    class Meta:
        model = PolicyTaxYear
        fields = []

    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        self.user = user

    note = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': _('Nyt notat')}),
        required=False,
    )

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
        fields = ('self_reported_amount', )


class EditAmountsUpdateFrom(forms.ModelForm, BootstrapForm):

    class Meta:
        model = PolicyTaxYear
        fields = ('adjusted_r75_amount', 'self_reported_amount', 'assessed_amount')


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
