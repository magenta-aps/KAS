from django.forms import Form


class BootstrapForm(Form):

    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control mr-2'

    def full_clean(self):
        super(BootstrapForm, self).full_clean()
        for name, field in self.fields.items():
            if self.has_error(name) is True:
                field.widget.attrs['class'] = 'form-control is-invalid mr-2'

    def as_table(self):
        return self._html_output(
            normal_row='<tr%(html_class_attr)s><th>%(label)s</th><td>%(field)s%(help_text)s</td><td>%(errors)s</td></tr>',
            error_row='<tr><td colspan="3">%s</td></tr>',
            row_ender='</td></tr>',
            help_text_html='<br /><span class="helptext">%s</span>',
            errors_on_separate_row=False
        )
