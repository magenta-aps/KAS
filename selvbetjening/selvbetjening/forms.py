import re

from django.forms import forms, fields, widgets


class PolicyForm(forms.Form):

    id = fields.IntegerField(
        widget=widgets.HiddenInput(),
        disabled=True
    )
    policy_number = fields.CharField(
        widget=widgets.HiddenInput(),
        disabled=True
    )

    prefilled_amount = fields.IntegerField(
        min_value=0,
        required=False,
        disabled=True
    )

    self_reported_amount = fields.IntegerField(
        min_value=0,
        required=False
    )

    preliminary_paid_amount = fields.IntegerField(
        min_value=0,
        required=False
    )

    from_pension = fields.BooleanField(
        widget=widgets.RadioSelect(choices=[(False, 'Nej'), (True, 'Ja')]),
        required=False
    )

    foreign_paid_amount_self_reported = fields.IntegerField(
        min_value=0,
        required=False
    )

    deduction_from_previous_years = fields.IntegerField(
        min_value=0,
        required=False
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
