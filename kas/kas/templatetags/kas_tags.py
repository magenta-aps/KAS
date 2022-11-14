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


@register.filter
def make_tuple(value1, value2):
    return (value1, value2)


@register.filter
def get(item, attribute):
    if item is not None:
        if type(attribute) == str:
            if hasattr(item, attribute):
                return getattr(item, attribute)
            if hasattr(item, "get"):
                return item.get(attribute)
        if isinstance(item, (tuple, list)):
            return item[int(attribute)]
        if isinstance(item, dict):
            if str(attribute) in item:
                return item[str(attribute)]
        try:
            return item[attribute]
        except (KeyError, TypeError):
            pass


@register.filter
def urlparam_join(value, extra):
    if "?" in value:
        if value == "?":
            glue = ""
        else:
            glue = "&"
    else:
        glue = "?"
    return f"{value}{glue}{extra}"
