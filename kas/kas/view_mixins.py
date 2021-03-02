from django.utils import formats
from django.utils.translation import to_locale, get_language


class BootstrapTableMixin:

    def get_context_data(self, **kwargs):
        ctx = super(BootstrapTableMixin, self).get_context_data(**kwargs)
        lang = get_language()
        ctx['table_locale'] = to_locale(lang).replace('_', '-')  # da-DK
        ctx['lang_locale'] = ctx['table_locale'].split('-')[0]  # da, de etc
        ctx['date_format'] = formats.get_format('SHORT_DATE_FORMAT', lang=lang)
        return ctx
