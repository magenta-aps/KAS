import json as jsonlib
import locale
import re
from html import unescape

from django.template.defaultfilters import register
from django.utils.http import urlquote
from django.utils.translation import gettext

trans_re = re.compile("_\\((.*)\\)")
format_re = re.compile("{(.*)}")

locale.setlocale(locale.LC_ALL, '')


@register.filter
def split(text, filter):
    return text.split(filter)


@register.filter
def json(data):
    return jsonlib.dumps(data)


@register.filter
def format(text, params):
    text = gettext(text)
    if params:
        if isinstance(params, str):
            params = jsonlib.loads(params)
        for key in params:
            value = params[key]
            if type(value) == tuple:
                # If a value is a tuple, it must be (message:string, params:dict,)
                value = format(value[0], value[1])
            else:
                value = format(str(value), None)
            text = text.replace("{" + key + "}", value)
    return unescape(text)


@register.filter
def analyze(data):
    print("Analysis:")
    print("---------")
    print(type(data))
    print(dir(data))
    print(data)
    print("---------")
    return ""


@register.filter
def startswith(text, prefix):
    return type(text) == str and text.startswith(prefix)


@register.filter
def after(text, prefix):
    if type(text) == str:
        try:
            return text[text.index(prefix)+len(prefix):]
        except ValueError:
            pass
    return text


@register.filter
def addstr(arg1, arg2):
    return ''.join([str(a) if a is not None else '' for a in [arg1, arg2]])


@register.filter
def back(url, backurl):
    if backurl:
        return ''.join([
            url,
            '&' if '?' in url else '?',
            'back=',
            urlquote(backurl)
        ])
    return url


@register.filter
def urlparam(url, param):
    if param:
        (key, value) = param.split("=")
        return ''.join([
            url,
            '&' if '?' in url else '?',
            key,
            '=',
            urlquote(value)
        ])
    return url


@register.filter
def get(item, attribute):
    if item is not None:
        if type(attribute) == str:
            if hasattr(item, attribute):
                return getattr(item, attribute)
            if hasattr(item, 'get'):
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
def number(item):
    locale.setlocale(locale.LC_ALL, ('da_dk', 'utf-8'))
    value = float(item.replace(',', '.')) if isinstance(item, str) else item
    return locale.format("%.2f", value, grouping=True)
