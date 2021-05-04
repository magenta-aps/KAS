from django import forms


class PensionCompanyChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name
