from django.forms import CheckboxInput, FileInput, Form, RadioSelect


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
