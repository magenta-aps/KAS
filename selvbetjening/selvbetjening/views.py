import json

from django.conf import settings
from django.forms import formset_factory
from django.http import FileResponse
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.template import Engine, Context
from django.urls import reverse
from django.utils import translation, timezone
from django.utils.datetime_safe import date
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.utils.translation.trans_real import DjangoTranslation
from django.views import View
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView, RedirectView
from django.views.i18n import JavaScriptCatalog

from selvbetjening.exceptions import PersonNotFoundException
from selvbetjening.forms import PolicyForm, PersonTaxYearForm, RepresentationTokenForm
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
        domain = kwargs.get("domain", self.domain)
        self.locale = locale
        # If packages are not provided, default to all installed packages, as
        # DjangoTranslation without localedirs harvests them all.
        packages = kwargs.get("packages", "")
        packages = packages.split("+") if packages else self.packages
        paths = self.get_paths(packages) if packages else None
        self.translation = DjangoTranslation(locale, domain=domain, localedirs=paths)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = {"locale": self.locale}
        context.update(super(CustomJavaScriptCatalog, self).get_context_data(**kwargs))
        context["catalog_str"] = (
            json.dumps(context["catalog"], sort_keys=True, indent=2)
            if context["catalog"]
            else None
        )
        context["formats_str"] = json.dumps(
            context["formats"], sort_keys=True, indent=2
        )
        return context

    def render_to_response(self, context, **response_kwargs):
        template = Engine().from_string(self.js_catalog_template)
        return HttpResponse(
            template.render(Context(context)), 'text/javascript; charset="utf-8"'
        )


class SetLanguageView(View):
    def post(self, request, *args, **kwargs):
        language = request.POST.get("language", settings.LANGUAGE_CODE)
        translation.activate(language)
        # request.session[translation.LANGUAGE_SESSION_KEY] = language
        response = JsonResponse("OK", safe=False)
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            settings.LOCALE_MAP.get(language, language),
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            path=settings.LANGUAGE_COOKIE_PATH,
        )
        # set_cookie() doesn't let us set the SameSite property, so we do it explicitly
        response.cookies[settings.LANGUAGE_COOKIE_NAME]["SameSite"] = "Strict"
        return response


class HasUserMixin(object):
    @property
    def cpr(self):
        return self.request.session["user_info"]["CPR"]

    @property
    def name(self):
        return self.request.session["user_info"].get("PersonName")

    @property
    def admin_name(self):
        return self.request.session["user_info"].get("AdminUsername")

    def get_context_data(self, **kwargs):
        return super(HasUserMixin, self).get_context_data(
            **{
                "cpr": self.cpr,
                "cpr_x": (self.cpr[0:6] + "xxxx") if self.cpr else None,
                "name": self.name,
                "admin_name": self.admin_name,
                **kwargs,
            }
        )


class CloseMixin(object):
    def redirect_if_close_time(self):
        if (
            settings.CLOSE_AT["month"] > 0 and settings.CLOSE_AT["date"] > 0
        ):  # Test server should be able to deactivate closing
            today = timezone.now().date()
            close_date = date(
                today.year, settings.CLOSE_AT["month"], settings.CLOSE_AT["date"]
            )
            if today >= close_date:
                return redirect(
                    reverse("selvbetjening:policy-view", kwargs={"year": today.year})
                )

    def dispatch(self, request, *args, **kwargs):
        redir = self.redirect_if_close_time()
        if redir:
            return redir
        return super().dispatch(request, *args, **kwargs)


class YearTabMixin(object):
    cutoff_years = 3

    def get_context_data(self, **kwargs):
        client = RestClient()
        all_years = client.get_person_tax_years(self.cpr)
        all_years.sort(key=lambda pty: pty["tax_year"]["year"], reverse=True)
        return super().get_context_data(
            **{
                **kwargs,
                "person_tax_years": {
                    "all": all_years,
                    "latest": all_years[0 : self.cutoff_years],
                    "prior": all_years[self.cutoff_years :],
                },
                "latest_year": date.today().year - 1,
                "latest_tax_year": all_years[0]["tax_year"],
            }
        )


class PolicyFormView(HasUserMixin, CloseMixin, YearTabMixin, FormView):
    template_name = "form.html"
    success_url = ""
    form_class = formset_factory(PolicyForm, min_num=0, extra=1)

    def get(self, request, *args, **kwargs):
        try:
            self.load_initial()
        except PersonNotFoundException:
            return redirect(reverse("selvbetjening:person-not-found"))
        return super(PolicyFormView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        extra_form = self.get_extra_form()
        if form.is_valid() and extra_form.is_valid():
            return self.form_valid(form, extra_form)
        else:
            return self.form_invalid(form)

    def get_form(self, form_class=None):
        formset = super(PolicyFormView, self).get_form(form_class=form_class)
        choices = [(None, _("--- angiv navn ---"))] + [
            (company["id"], company["name"])
            for company in self.request.session["pension_companies"]
        ]
        for form in formset.extra_forms:
            form.fields["pension_company_id"].widget.choices = choices
        return formset

    def get_extra_form(self):
        kwargs = {"initial": self.request.session["person_tax_year"]}
        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        return PersonTaxYearForm(**kwargs)

    def get_context_data(self, **kwargs):
        context = {
            **kwargs,
            "year": date.today().year - 1,
            "person_tax_year": self.request.session["person_tax_year"],
            "data": {
                str(item["id"]): item
                for item in self.request.session["policy_tax_years"]
            },
            "extra_form": self.get_extra_form(),
        }
        return super(PolicyFormView, self).get_context_data(**context)

    @property
    def year(self):
        return date.today().year - 1

    def load_initial(self):
        # Load known policy_tax_year data to populate form with initial data
        # We should only do this once per get-post cycle, because it contains requests to the REST backend (and is thus "expensive")
        client = RestClient()
        person_tax_year = client.get_person_tax_year(self.cpr, self.year)
        if person_tax_year is not None:
            self.request.session["person_tax_year"] = person_tax_year
            policy_tax_years = client.get_policies(
                person_tax_year=person_tax_year["id"],
                active=True,
            )
            policy_tax_years.sort(key=lambda k: str(k["pension_company"]["name"]))
        else:
            raise PersonNotFoundException()
        self.request.session["policy_tax_years"] = policy_tax_years
        pension_companies = client.get_pension_companies()
        self.request.session["pension_companies"] = pension_companies

    def get_initial(self):
        return self.request.session["policy_tax_years"]

    def form_valid(self, form, extra_form):
        client = RestClient(self.request.session["user_info"])
        for policyform in form:
            policyform_data = policyform.get_nonfile_data()
            if len(policyform_data):
                id = policyform_data["id"]
                if id is None:
                    # Creating new
                    if (
                        policyform_data["pension_company_name"]
                        and not policyform_data["pension_company_id"]
                    ):
                        pension_company = client.create_pension_company(
                            policyform_data.pop("pension_company_name")
                        )
                        policyform_data["pension_company"] = pension_company["id"]
                    else:
                        policyform_data["pension_company"] = policyform_data[
                            "pension_company_id"
                        ]

                    policyform_data["policy_number"] = policyform_data[
                        "policy_number_new"
                    ]
                    person_tax_year = self.request.session.get("person_tax_year")
                    if person_tax_year is None:
                        person_tax_year = client.get_person_tax_year(
                            self.cpr, self.year
                        )
                        if person_tax_year is not None:
                            self.request.session["person_tax_year"] = person_tax_year
                        else:
                            return redirect(reverse("selvbetjening:person-not-found"))
                    policyform_data["person_tax_year"] = person_tax_year["id"]
                    client.create_policy(
                        {
                            **policyform_data,
                            "files": policyform.get_filled_files(),
                        }
                    )
                else:
                    existing_files_data = policyform.get_existing_files()
                    client.update_policy(
                        id,
                        {
                            **policyform_data,
                            "files": policyform.get_filled_files(),
                            "existing_files": existing_files_data,
                        },
                    )
        client.update_person_tax_year(
            self.request.session["person_tax_year"]["id"], extra_form.cleaned_data
        )
        return redirect(reverse("selvbetjening:policy-submitted"))


class PolicyDetailView(HasUserMixin, YearTabMixin, TemplateView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        client = RestClient()
        year = kwargs.get("year")
        nowyear = date.today().year - 1
        if year is None or year == "":
            year = nowyear
        else:
            year = int(year)

        policies = client.get_policies(cpr=self.cpr, year=year)
        person_tax_year = client.get_person_tax_year(cpr=self.cpr, year=year)
        final_settlement_exists = client.get_final_settlement_existence(
            cpr=self.cpr, year=year
        )
        return super().get_context_data(
            **{
                **kwargs,
                "items": policies,
                "person_tax_year": person_tax_year,
                "year": year,
                "summary": {
                    key: sum([int(policy.get(key) or 0) for policy in policies])
                    for key in [
                        "prefilled_adjusted_amount",
                        "self_reported_amount",
                        "calculated_result",
                    ]
                },
                "final_settlement_exists": final_settlement_exists,
            }
        )


class PolicyDetailPriorView(PolicyDetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**{**kwargs, "prior": True})
        return context


class ViewFinalSettlementView(HasUserMixin, View):
    def get(self, *args, year, **kwargs):
        try:
            year = int(year)
        except ValueError:
            return HttpResponse(status=400)
        r = RestClient().get_final_settlement(year, self.cpr)
        if r.status_code == 200:
            return FileResponse(r.iter_content(), content_type="application/pdf")
        return HttpResponse(
            content=_("Ingen slutopgørelse for givet år"),
            status=404,
            content_type="text/html; charset=utf-8",
        )


@method_decorator(csrf_exempt, name="dispatch")
class RepresentationStartView(FormView):
    form_class = RepresentationTokenForm

    def form_valid(self, form):
        token = form.cleaned_data["token"]
        client = RestClient()
        response = client.exchange_token(token)
        if not response.ok:
            return HttpResponse(status=response.status_code, content=response.content)
        data = response.json()
        pruned_data = {}
        # Keys CPR and PersonName match what we get from login service
        for key in ("CPR", "PersonName", "AdminUsername", "AdminUserID"):
            if key not in data:
                return HttpResponse(
                    status=500, content=f"Missing {key} in token service response"
                )
            pruned_data[key] = data[key]
        self.request.session["user_info"] = pruned_data
        return redirect(reverse("selvbetjening:policy-edit"))


class RepresentationStopView(RedirectView):
    def get_redirect_url(self):
        if "user_info" in self.request.session:
            del self.request.session["user_info"]
        return settings.KAS_REPRESENTATION_STOP
