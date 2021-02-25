import json

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.template import Engine, Context
from django.utils import translation
from django.utils.translation.trans_real import DjangoTranslation
from django.views import View
from django.views.i18n import JavaScriptCatalog


class CustomJavaScriptCatalog(JavaScriptCatalog):

    js_catalog_template = r"""
    {% autoescape off %}
    (function(globals) {
    const django = globals.django || (globals.django = {});
    django.catalog = django.catalog || {};
    {% if catalog_str %}
    django.catalog["{{ locale }}"] = {{ catalog_str }};
    {% endif %}
    }(this));
    {% endautoescape %}
    """

    def get(self, request, locale, *args, **kwargs):
        domain = kwargs.get('domain', self.domain)
        self.locale = locale
        # If packages are not provided, default to all installed packages, as
        # DjangoTranslation without localedirs harvests them all.
        packages = kwargs.get('packages', '')
        packages = packages.split('+') if packages else self.packages
        paths = self.get_paths(packages) if packages else None
        self.translation = DjangoTranslation(locale, domain=domain, localedirs=paths)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = {'locale': self.locale}
        context.update(super(CustomJavaScriptCatalog, self).get_context_data(**kwargs))
        context['catalog_str'] = \
            json.dumps(context['catalog'], sort_keys=True, indent=2) \
            if context['catalog'] else None
        context['formats_str'] = json.dumps(context['formats'], sort_keys=True, indent=2)
        return context

    def render_to_response(self, context, **response_kwargs):
        template = Engine().from_string(self.js_catalog_template)
        return HttpResponse(template.render(Context(context)), 'text/javascript; charset="utf-8"')


class SetLanguageView(View):

    def post(self, request, *args, **kwargs):
        language = request.POST.get('language', settings.LANGUAGE_CODE)
        translation.activate(language)
        # request.session[translation.LANGUAGE_SESSION_KEY] = language
        response = JsonResponse("OK", safe=False)
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            settings.LOCALE_MAP.get(language, language),
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            path=settings.LANGUAGE_COOKIE_PATH
        )
        # set_cookie() doesn't let us set the SameSite property, so we do it explicitly
        response.cookies[settings.LANGUAGE_COOKIE_NAME]['SameSite'] = 'Strict'
        return response
