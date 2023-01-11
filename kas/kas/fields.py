from django import forms


class PensionCompanyChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, pension_company):
        return f"{pension_company.name} ({pension_company.res})"


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%d"
        super().__init__(**kwargs)


class DisabledIntegerField(forms.IntegerField):
    def __init__(self, **kwargs):
        kwargs["disabled"] = True
        # Set to match the max/min values that ModelForm creates from BigIntegerField
        kwargs["min_value"] = -9223372036854775808
        kwargs["max_value"] = 9223372036854775807
        super().__init__(**kwargs)
