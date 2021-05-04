from django.forms import ModelChoiceField


class PensionCompanyChoiceField(ModelChoiceField):
    def label_from_instance(self, pension_company):
        return f"{pension_company.name} ({pension_company.res})"
