from django import forms
from django.utils.translation import gettext as _
from kas.forms_mixin import BootstrapForm
from kas.models import PersonTaxYear, PolicyTaxYear, Note


class PersonListFilterForm(BootstrapForm):
    cpr = forms.CharField(label=_('Cpr'), required=False)
    name = forms.CharField(label=_('Navn'), required=False)


class PersonTaxYearForm(forms.ModelForm, BootstrapForm):

    class Meta:
        model = PersonTaxYear
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
        print("Saving")
        print(self.cleaned_data)
        if self.cleaned_data['note']:
            Note(
                person_tax_year=instance,
                author=self.user,
                content=self.cleaned_data['note']
            ).save()
        return instance


class PolicyTaxYearForm(forms.ModelForm, BootstrapForm):

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
        return instance
