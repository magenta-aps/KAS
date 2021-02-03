from django import forms
from worker.models import job_types
action_choices = ('create', )


class JobControlForm(forms.Form):
    action = forms.ChoiceField(choices=((v, v) for v in action_choices), widget=forms.HiddenInput)
    job_type = forms.ChoiceField(choices=job_types, widget=forms.HiddenInput)
    redirect_url = forms.CharField(widget=forms.HiddenInput)
