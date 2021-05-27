from django import forms


class PensionCompanyChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, pension_company):
        return f"{pension_company.name} ({pension_company.res})"


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%d"
        super().__init__(**kwargs)
