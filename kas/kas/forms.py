from django import forms
from django.utils.translation import gettext as _
from kas.forms_mixin import BootstrapForm
from kas.models import PersonTaxYear, PolicyTaxYear, Note, PolicyDocument


class PersonListFilterForm(BootstrapForm):
    cpr = forms.CharField(label=_('Cpr'), required=False)
    name = forms.CharField(label=_('Navn'), required=False)


class PersonTaxYearForm(forms.ModelForm, BootstrapForm):
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
        instance = super().save(commit)
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


class PolicyTaxYearForm(forms.ModelForm, BootstrapForm):
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
