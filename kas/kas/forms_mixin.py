from django.forms import Form, CheckboxInput, RadioSelect, FileInput


class BootstrapForm(Form):
    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            self.set_field_classes(name, field)

    def full_clean(self):
        result = super(BootstrapForm, self).full_clean()
        for name, field in self.fields.items():
            self.set_field_classes(name, field, True)

        return result

    def as_table(self):
        return self._html_output(
            normal_row="<tr%(html_class_attr)s><th>%(label)s</th><td>%(field)s%(help_text)s</td><td>%(errors)s</td></tr>",
            error_row='<tr><td colspan="3">%s</td></tr>',
            row_ender="</td></tr>",
            help_text_html='<small class="form-text text-muted mb-2 ml-1">%s</small>',
            errors_on_separate_row=False,
        )

    def set_field_classes(self, name, field, check_for_errors=False):
        classes = self.split_class(field.widget.attrs.get("class"))
        classes.append("mr-2")
        if isinstance(field.widget, (CheckboxInput, RadioSelect)):
            if "not-form-check-input" not in classes:
                classes.append("form-check-input")
        else:
            if not isinstance(field.widget, FileInput):
                classes.append("form-control")
        if check_for_errors:
            if self.has_error(name) is True:
                classes.append("is-invalid")
        field.widget.attrs["class"] = " ".join(set(classes))

    def split_class(self, class_string):
        return class_string.split(" ") if class_string else []
