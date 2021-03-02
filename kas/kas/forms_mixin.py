from django.forms import ModelForm


class BootstrapModelForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(BootstrapModelForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control mr-2'

    def full_clean(self):
        super(BootstrapModelForm, self).full_clean()
        for name, field in self.fields.items():
            if self.has_error(name) is True:
                field.widget.attrs['class'] = 'form-control is-invalid mr-2'
