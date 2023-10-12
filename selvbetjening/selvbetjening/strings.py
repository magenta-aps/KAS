from django.utils.translation import gettext as _
from django.utils.translation import ungettext_lazy

# Strings in django core or other modules that we use, and don't have a greenlandic translation

# From django.forms.fields
_("This field is required.")
_("Enter a whole number.")
_("No file was submitted. Check the encoding type on the form.")
_("No file was submitted.")
_("The submitted file is empty.")
ungettext_lazy(
    "Ensure this filename has at most %(max)d character (it has %(length)d).",
    "Ensure this filename has at most %(max)d characters (it has %(length)d).",
    "max",
)
_("Select a valid choice. %(value)s is not one of the available choices.")
