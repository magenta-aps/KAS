import re

from django.core.exceptions import ValidationError
from django.forms import forms, fields, widgets, Field


class PolicyForm(forms.Form):

    id = fields.IntegerField(
        widget=widgets.HiddenInput(),
        disabled=True,
        required=False,
    )
    policy_number = fields.CharField(
        widget=widgets.HiddenInput(),
        disabled=True,
        required=False,
    )

    pension_company_id = fields.IntegerField(
        widget=widgets.Select(
            choices=[(None, "--- angiv navn ---"), (1, "Selskab 1"), (2, "Selskab 2")],
            attrs={'class': 'company_select form-control', 'autocomplete': 'off'}
        ),
        required=False,
    )
    pension_company_name = fields.CharField(
        widget=widgets.TextInput(
            attrs={'class': 'company_explicit form-control', 'autocomplete': 'off'}
        ),
        required=False,
    )
    policy_number_new = fields.CharField(
        widget=widgets.TextInput(
            attrs={'autocomplete': 'off', 'class': 'form-control'}
        ),
        required=False,
    )

    prefilled_amount = fields.IntegerField(
        required=False,
        disabled=True,
        widget=widgets.NumberInput(
            attrs={'autocomplete': 'off', 'class': 'form-control'}
        ),
    )

    self_reported_amount = fields.IntegerField(
        required=False,
        widget=widgets.NumberInput(
            attrs={'autocomplete': 'off', 'class': 'form-control'}
        ),
    )

    self_reported_used_deduction = fields.IntegerField(
        min_value=0,
        required=False,
        widget=widgets.NumberInput(
            attrs={'autocomplete': 'off', 'class': 'form-control'}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for i in range(0, 10):
            self.fields[f"file_file_{i}"] = forms.FileField(
                allow_empty_file=True,
                required=False
            )
            self.fields[f"file_description_{i}"] = fields.CharField(
                max_length=255,
                widget=widgets.TextInput(
                    attrs={'placeholder': 'Beskrivelse'}
                ),
                required=False
            )

        if 'initial' in kwargs and 'policy_documents' in kwargs['initial']:
            self.existing_files = []
            for i, policy_document in enumerate(kwargs['initial']['policy_documents']):

                id_key = key = f"file_existing_id_{i}"
                self.fields[key] = fields.IntegerField(
                    widget=widgets.HiddenInput(),
                    disabled=True
                )
                self.existing_files.append(self[key])
                kwargs['initial'][key] = policy_document['id']

                key = f"file_existing_delete_{i}"
                self.fields[key] = fields.BooleanField(
                    widget=widgets.CheckboxInput(
                        attrs={'title': 'Behold'}
                    ),
                    label=policy_document['name'],
                    required=False
                )
                kwargs['initial'][key] = True
                self[id_key].keep_field = self[key]

                key = f"file_existing_description_{i}"
                self.fields[key] = fields.CharField(
                    max_length=255,
                    widget=widgets.TextInput(
                        attrs={'placeholder': 'Beskrivelse'}
                    ),
                    required=False
                )
                kwargs['initial'][key] = policy_document['description']
                self[id_key].description_field = self[key]

    def get_filled_files(self):
        # Returns a list of tuples (file, description)
        if self.is_bound:
            r = re.compile(self.prefix+r"-file_file_(\d+)")
            files = []
            for name, file in self.files.items():
                m = r.match(name)
                if m:
                    description = self.cleaned_data.get(f"file_description_{m.group(1)}", '')
                    files.append((file, description,))
            return files
        return None

    def get_existing_files(self):
        if self.is_bound:
            data = {}
            for id_field in self.existing_files:
                data[id_field.value()] = {
                    'keep': id_field.keep_field.value(),
                    'description': id_field.description_field.value()
                }
            return data

    def get_nonfile_data(self):
        if self.is_bound:
            return {k: v for k, v in self.cleaned_data.items() if not k.startswith('file_')}

    def clean(self):
        cleaned_data = self.cleaned_data
        # For the extra form (the one that creates a new policy_tax_year), if any field is set, the policy_number_new field is required
        extra_form_has_data = False
        if cleaned_data['id'] is None:
            for value in cleaned_data.values():
                if value not in ('', None):
                    extra_form_has_data = True
                    break

        if extra_form_has_data:
            errors = {}

            for fieldnames in [['policy_number_new'], ['self_reported_amount'], ['pension_company_id', 'pension_company_name']]:
                if len([True for x in fieldnames if cleaned_data[x] in ('', None)]) == len(fieldnames):
                    for value in cleaned_data.values():
                        if value not in ('', None):
                            errors[fieldnames[0]] = [ValidationError(Field.default_error_messages['required'])]

            if len(errors):
                raise ValidationError(errors)
        return cleaned_data


class PersonTaxYearForm(forms.Form):

    foreign_pension_notes = fields.CharField(
        widget=widgets.Textarea(
            attrs={'autocomplete': 'off', 'class': 'form-control'}
        ),
        required=False,
    )
    general_notes = fields.CharField(
        widget=widgets.Textarea(
            attrs={'autocomplete': 'off', 'class': 'form-control'}
        ),
        required=False,
    )
