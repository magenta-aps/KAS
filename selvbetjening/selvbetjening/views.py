import json

from django.conf import settings
from django.forms import formset_factory
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.template import Engine, Context
from django.urls import reverse
from django.utils import translation
from django.utils.datetime_safe import date
from django.utils.translation.trans_real import DjangoTranslation
from django.views import View
from django.views.decorators.cache import cache_control
from django.views.generic import FormView, TemplateView
from django.views.i18n import JavaScriptCatalog

from selvbetjening.forms import PolicyForm
from selvbetjening.restclient import RestClient


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

    @cache_control(max_age=3600, public=True)
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


class PolicyFormView(FormView):
    template_name = 'form.html'
    success_url = ''
    form_class = formset_factory(PolicyForm, min_num=1, extra=0)

    def get(self, request, *args, **kwargs):
        self.load_initial()
        return super(PolicyFormView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            **kwargs,
            'year': date.today().year - 1,
            'data': {str(item['id']): item for item in self.request.session['policy_tax_years']}
        }
        return super(PolicyFormView, self).get_context_data(**context)

    def load_initial(self):
        # Load known policy_tax_year data to populate form with initial data
        # We should only do this once per get-post cycle, because it contains requests to the REST backend (and is thus "expensive")
        year = date.today().year - 1
        client = RestClient()
        person_tax_years = client.get(
            'person_tax_year',
            cpr=self.request.session['user_info']['CPR'],
            year=str(year)
        )
        if len(person_tax_years) == 1:
            policy_tax_years = client.get(
                'policy_tax_year',
                person_tax_year=person_tax_years[0]['id']
            )
            policy_tax_years.sort(key=lambda k: k['pension_company']['cvr'])
        else:
            policy_tax_years = []
        self.request.session['policy_tax_years'] = policy_tax_years

    def get_initial(self):
        return self.request.session['policy_tax_years']

    def form_valid(self, form):
        client = RestClient()
        for policyform in form:
            policyform_data = policyform.get_nonfile_data()
            if len(policyform_data):
                existing_files_data = policyform.get_existing_files()
                client.post_policy(policyform_data['id'], {
                    **policyform_data,
                    'files': policyform.get_filled_files(),
                    'existing_files': existing_files_data,
                })
        return redirect(reverse('selvbetjening:policyview', args=[date.today().year - 1]))


class PolicyDetailView(TemplateView):
    template_name = 'view.html'

    def get_context_data(self, **kwargs):
        cpr = self.request.session['user_info']['CPR']
        client = RestClient()
        year = kwargs.get('year')
        nowyear = date.today().year - 1
        if year is None or year == '':
            year = nowyear
        else:
            year = int(year)

        policies = client.get_policies(cpr, year)
        context = {
            **kwargs,
            'items': policies,
            'year': year,
            'showing_current_year': year == nowyear,
            'newest_prior_year': nowyear - 1,
            'current_nav': 'view-current' if nowyear == year else 'view-prior',
            'summary': {
                key: sum([int(policy.get(key) or 0) for policy in policies])
                for key in [
                    'prefilled_amount', 'estimated_amount', 'self_reported_amount',
                    'preliminary_paid_amount', 'foreign_paid_amount_self_reported',
                    'foreign_paid_amount_actual', 'deduction_from_previous_years',
                    'applied_deduction_from_previous_years', 'calculated_result'
                ]
            }
        }

        if year < nowyear:
            years = [
                p['tax_year']
                for p in client.get_person_tax_years(cpr)
                if p['tax_year'] < nowyear
            ]
            years.sort()
            context['years'] = years

        return context
