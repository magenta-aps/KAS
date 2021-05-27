from django.forms import Form, CheckboxInput, RadioSelect


class BootstrapForm(Form):

    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            self.set_field_classes(name, field)

    def full_clean(self):
        super(BootstrapForm, self).full_clean()
        for name, field in self.fields.items():
            self.set_field_classes(name, field)

    def as_table(self):
        return self._html_output(
            normal_row='<tr%(html_class_attr)s><th>%(label)s</th><td>%(field)s%(help_text)s</td><td>%(errors)s</td></tr>',
            error_row='<tr><td colspan="3">%s</td></tr>',
            row_ender='</td></tr>',
            help_text_html='<br /><span class="helptext">%s</span>',
            errors_on_separate_row=False
        )

    def set_field_classes(self, name, field):
        classes = self.split_class(field.widget.attrs.get('class'))
        classes.append('mr-2')
        if isinstance(field.widget, (CheckboxInput, RadioSelect)):
            classes.append('form-check-input')
        else:
            classes.append('form-control')
        if self.has_error(name) is True:
            classes.append('is-invalid')
        field.widget.attrs['class'] = ' '.join(set(classes))

    def split_class(self, class_string):
        return class_string.split(' ') if class_string else []
