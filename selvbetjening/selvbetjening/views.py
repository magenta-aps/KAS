import json

from django.conf import settings
from django.forms import formset_factory
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.template import Engine, Context
from django.urls import reverse
from django.utils import translation
from django.utils.datetime_safe import date
from django.utils.translation import gettext as _
from django.utils.translation.trans_real import DjangoTranslation
from django.views import View
from django.views.decorators.cache import cache_control
from django.views.generic import FormView, TemplateView
from django.views.i18n import JavaScriptCatalog
from selvbetjening.exceptions import PersonNotFoundException
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


class HasUserMixin(object):

    @property
    def cpr(self):
        return self.request.session['user_info']['CPR']

    @property
    def name(self):
        return self.request.session['user_info'].get('PersonName')

    def get_context_data(self, **kwargs):
        return super(HasUserMixin, self).get_context_data(**{
            'cpr': self.cpr,
            'name': self.name,
            **kwargs
        })


class PolicyFormView(HasUserMixin, FormView):
    template_name = 'form.html'
    success_url = ''
    form_class = formset_factory(PolicyForm, min_num=0, extra=1)

    def get(self, request, *args, **kwargs):
        try:
            self.load_initial()
        except PersonNotFoundException:
            return redirect(reverse('selvbetjening:person-not-found'))
        return super(PolicyFormView, self).get(request, *args, **kwargs)

    def get_form(self, form_class=None):
        formset = super(PolicyFormView, self).get_form(form_class=form_class)
        choices = [(None, _("--- angiv navn ---"))] + [(company['id'], company['name']) for company in self.request.session['pension_companies']]
        for form in formset.extra_forms:
            form.fields['pension_company_id'].widget.choices = choices
        return formset

    def get_context_data(self, **kwargs):
        context = {
            **kwargs,
            'year': date.today().year - 1,
            'data': {str(item['id']): item for item in self.request.session['policy_tax_years']},
        }
        return super(PolicyFormView, self).get_context_data(**context)

    @property
    def year(self):
        return date.today().year - 1

    def load_initial(self):
        # Load known policy_tax_year data to populate form with initial data
        # We should only do this once per get-post cycle, because it contains requests to the REST backend (and is thus "expensive")
        client = RestClient()
        person_tax_year = client.get_person_tax_year(
            self.cpr,
            self.year
        )
        if person_tax_year is not None:
            self.request.session['person_tax_year'] = person_tax_year
            policy_tax_years = client.get_policies(
                person_tax_year=person_tax_year['id']
            )
            policy_tax_years.sort(key=lambda k: str(k['pension_company']['res']))
        else:
            raise PersonNotFoundException()
        self.request.session['policy_tax_years'] = policy_tax_years
        pension_companies = client.get_pension_companies()
        self.request.session['pension_companies'] = pension_companies

    def get_initial(self):
        return self.request.session['policy_tax_years']

    def form_valid(self, form):
        client = RestClient()
        for policyform in form:
            policyform_data = policyform.get_nonfile_data()
            if len(policyform_data):
                id = policyform_data['id']
                if id is None:
                    # Creating new
                    if policyform_data['pension_company_name'] and not policyform_data['pension_company_id']:
                        pension_company = client.create_pension_company(policyform_data.pop('pension_company_name'))
                        policyform_data['pension_company'] = pension_company['id']
                    else:
                        policyform_data['pension_company'] = policyform_data['pension_company_id']
                    policyform_data['policy_number'] = policyform_data['policy_number_new']
                    person_tax_year = self.request.session.get('person_tax_year')
                    if person_tax_year is None:
                        person_tax_year = client.get_person_tax_year(self.cpr, self.year)
                        if person_tax_year is not None:
                            self.request.session['person_tax_year'] = person_tax_year
                        else:
                            return redirect(reverse('selvbetjening:person-not-found'))
                    policyform_data['person_tax_year'] = person_tax_year['id']
                    client.create_policy({
                        **policyform_data,
                        'files': policyform.get_filled_files(),
                    })
                else:
                    existing_files_data = policyform.get_existing_files()
                    client.update_policy(id, {
                        **policyform_data,
                        'files': policyform.get_filled_files(),
                        'existing_files': existing_files_data,
                    })
        # return redirect(reverse('selvbetjening:policyview', args=[date.today().year - 1]))
        return redirect(reverse('selvbetjening:policy-submitted'))


class PolicyDetailView(HasUserMixin, TemplateView):
    template_name = 'view.html'

    def get_context_data(self, **kwargs):
        client = RestClient()
        year = kwargs.get('year')
        nowyear = date.today().year - 1
        if year is None or year == '':
            year = nowyear
        else:
            year = int(year)

        policies = client.get_policies(cpr=self.cpr, year=year)
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
                    'foreign_paid_amount_actual', 'applied_deduction_from_previous_years',
                    'calculated_result'
                ]
            },
        }

        if year < nowyear:
            all_years = client.get_person_tax_years(self.cpr)
            years = [
                p['tax_year']
                for p in all_years
                if p['tax_year'] < nowyear
            ] if all_years is not None else []
            years.sort()
            context['years'] = years

        return context
