from django.template.defaultfilters import register
from django.utils import formats


@register.filter
def negative(item):
    if type(item) in (int, float):
        return -item
    return item


@register.filter
def percent(value, digits=2):
    return formats.localize(round(100.0 * float(value), digits), use_l10n=True) + "%"


@register.filter
def append(value, extra):
    return f"{value}{extra}"
