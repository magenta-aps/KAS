import mimetypes
import os
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models import Count, F, Q, Min, FilteredRelation
from django.http import Http404, HttpResponse, HttpResponseRedirect, FileResponse
from django.core.exceptions import SuspiciousOperation
from django.db.models import Case, Value, When
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.views.generic import (
    TemplateView,
    ListView,
    View,
    UpdateView,
    CreateView,
    FormView,
    RedirectView,
)
from django.views.generic.detail import DetailView, SingleObjectMixin, BaseDetailView
from django.views.generic.list import MultipleObjectMixin
from django_filters.views import FilterView
from eskat.models import ImportedKasMandtal, ImportedR75PrivatePension, MockModels
from ipware import get_client_ip
from kas.filters import PensionCompanyFilterSet, LockFilterSet
from kas.forms import (
    PersonListFilterForm,
    SelfReportedAmountForm,
    EditAmountsUpdateForm,
    PensionCompanySummaryFileForm,
    CreatePolicyTaxYearForm,
    PolicyTaxYearActivationForm,
    PolicyNotesAndAttachmentForm,
    PersonNotesAndAttachmentForm,
    PaymentOverrideUpdateForm,
    PolicyListFilterForm,
    FinalStatementForm,
    PolicyTaxYearCompanyForm,
    PolicyTaxYearNumberForm,
    PensionCompanyModelForm,
    PensionCompanyMergeForm,
    NoteUpdateForm,
    UploadExistingFinalSettlementForm,
    PreviousYearNegativePayoutForm,
)
from kas.models import (
    PensionCompanySummaryFile,
    PensionCompanySummaryFileDownload,
    Note,
    TaxYear,
    PersonTaxYear,
    PolicyTaxYear,
    TaxSlipGenerated,
    PolicyDocument,
    FinalSettlement,
    PensionCompany,
    RepresentationToken,
    Person,
    Lock,
    Agterskrivelse,
    PreviousYearNegativePayout,
)
from kas.reportgeneration.kas_final_statement import TaxFinalStatementPDF
from kas.view_mixins import (
    CreateOrUpdateViewWithNotesAndDocumentsForPolicyTaxYear,
    HighestSingleObjectMixin,
    SpecialExcelMixin,
    KasMixin,
)
from openpyxl import Workbook
from prisme.models import Transaction, Prisme10QBatch
from project.view_mixins import (
    sagsbehandler_or_administrator_required,
    sagsbehandler_or_administrator_or_borgerservice_required,
    PermissionRequiredWithMessage,
    administrator_required,
)
from tenQ.dates import get_due_date
from worker.models import Job

from kas.jobs import dispatch_final_settlement, import_mandtal, merge_pension_companies


class StatisticsView(KasMixin, PermissionRequiredWithMessage, TemplateView):
    permission_required = "kas.list_persontaxyear"
    permission_denied_message = sagsbehandler_or_administrator_required
    template_name = "kas/statistics.html"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)

        result["years"] = [x.year for x in TaxYear.objects.order_by("year")]

        by_year_data = {
            "imported_mandtal": {},
            "imported_r75": {},
            "persons": {},
            "policies": {},
        }

        for x in ImportedKasMandtal.objects.values("skatteaar").annotate(
            number_per_year=Count("skatteaar")
        ):
            by_year_data["imported_mandtal"][x["skatteaar"]] = x["number_per_year"]

        for x in ImportedR75PrivatePension.objects.values("tax_year").annotate(
            number_per_year=Count("tax_year")
        ):
            by_year_data["imported_r75"][x["tax_year"]] = x["number_per_year"]

        for x in (
            PersonTaxYear.objects.values("tax_year__year")
            .order_by("tax_year__year")
            .annotate(number_per_year=Count("pk"))
        ):
            by_year_data["persons"][x["tax_year__year"]] = x["number_per_year"]

        for x in PolicyTaxYear.objects.values(
            "person_tax_year__tax_year__year"
        ).annotate(number_per_year=Count("person_tax_year__tax_year__year")):
            by_year_data["policies"][x["person_tax_year__tax_year__year"]] = x[
                "number_per_year"
            ]

        if settings.ENVIRONMENT != "production":
            result["show_mockup"] = True

            by_year_data["mockup_mandtal"] = {}
            by_year_data["mockup_r75"] = {}

            for x in MockModels.MockKasMandtal.objects.values("skatteaar").annotate(
                number_per_year=Count("skatteaar")
            ):
                by_year_data["mockup_mandtal"][x["skatteaar"]] = x["number_per_year"]

            for x in MockModels.MockR75Idx4500230.objects.values("tax_year").annotate(
                number_per_year=Count("tax_year")
            ):
                by_year_data["mockup_r75"][x["tax_year"]] = x["number_per_year"]

        for k, v in by_year_data.items():
            result[k] = [v.get(year, 0) for year in result["years"]]

        return result


class PersonTaxYearListView(
    KasMixin, SpecialExcelMixin, PermissionRequiredWithMessage, ListView
):
    permission_required = "kas.view_persontaxyear"
    template_name = "kas/persontaxyear_list.html"
    context_object_name = "personstaxyears"
    paginate_by = 20

    excel_headers = [
        "Personnummer",
        "Navn",
        "Adresse",
        "Kommune",
        "Antal policer",
        "Næste behandlingsdato",
        "Slutlignede policer",
        "Ikke-slutlignede policer",
    ]

    values = [
        "person__cpr",
        "person__name",
        "person__full_address",
        "person__municipality_name",
        "policy_count",
        "next_processing_date",
        "slutlignede",
        "ikke_slutlignede",
    ]

    model = PersonTaxYear
    form_class = PersonListFilterForm
    default_order_by = "person__cpr"

    def get_form(self):
        years = [tax_year.year for tax_year in TaxYear.objects.order_by("year")]
        current_year = timezone.now().year
        if current_year not in years:
            current_year = max([y for y in years if y < current_year])
        initial = {"year": current_year}
        kwargs = {"initial": initial}
        if self.request.GET:
            kwargs["data"] = {**initial, **self.request.GET.dict()}
        return PersonListFilterForm(**kwargs)

    def should_search(self, form):
        return form.is_valid() and form.has_changed()

    def get_queryset(self):
        self.form = self.get_form()
        order_by = self.request.GET.get("order_by", self.default_order_by)

        # Handle fields that should always have null last when sorting
        if order_by.endswith("_nulllast"):
            order_by = order_by[:-9]
            if order_by.startswith("-"):
                order_by = F(order_by[1:]).desc(nulls_last=True)
            else:
                order_by = F(order_by).asc(nulls_last=True)

        return self.filter_queryset(super().get_queryset()).order_by(
            order_by, "person__name"
        )

    def filter_queryset(self, qs):
        form = self.form
        if self.should_search(form):
            # you always need to call is_valid before using cleaned_data
            if hasattr(form, "cleaned_data"):
                qs = qs.filter(
                    tax_year__year=form.cleaned_data["year"] or form.initial["year"]
                )
                # Check whether there are any fields filled out apart from 'year'
                if form.cleaned_data["cpr"]:
                    qs = qs.filter(person__cpr__icontains=form.cleaned_data["cpr"])
                if form.cleaned_data["name"]:
                    qs = qs.filter(person__name__icontains=form.cleaned_data["name"])
                if form.cleaned_data["municipality_code"]:
                    qs = qs.filter(
                        person__municipality_code=form.cleaned_data["municipality_code"]
                    )
                if form.cleaned_data["municipality_name"]:
                    qs = qs.filter(
                        person__municipality_name__icontains=form.cleaned_data[
                            "municipality_name"
                        ]
                    )
                if form.cleaned_data["address"]:
                    qs = qs.filter(
                        person__full_address__icontains=form.cleaned_data["address"]
                    )
                if (
                    form.cleaned_data["tax_liability"] is not None
                ):  # False is a valid value
                    qs = qs.filter(fully_tax_liable=form.cleaned_data["tax_liability"])

                qs = qs.annotate(
                    slutlignede=Count(
                        expression="policytaxyear",
                        filter=Q(
                            policytaxyear__slutlignet=True, policytaxyear__active=True
                        ),
                    ),
                    ikke_slutlignede=Count(
                        expression="policytaxyear",
                        filter=Q(
                            policytaxyear__slutlignet=False, policytaxyear__active=True
                        ),
                    ),
                )
                if form.cleaned_data["finalized"]:
                    finalized = form.cleaned_data["finalized"]
                    if finalized == "har_slutlignede":
                        qs = qs.filter(slutlignede__gt=0)
                    elif finalized == "mangler_slutlignede":
                        qs = qs.filter(slutlignede=0)
                    if finalized == "har_ikkeslutlignede":
                        qs = qs.filter(ikke_slutlignede__gt=0)
                    elif finalized == "mangler_ikkeslutlignede":
                        qs = qs.filter(ikke_slutlignede=0)
            elif "year" in form.initial:
                qs = qs.filter(tax_year__year=form.initial["year"])
            qs = qs.annotate(
                policy_count=Count("policytaxyear"),
                next_processing_date=Min("policytaxyear__next_processing_date"),
            )
        else:
            # Don't find anything if form is invalid or empty
            qs = self.model.objects.none()
        return qs


class PersonTaxYearSpecialListView(PersonTaxYearListView):

    default_order_by = "person__cpr"

    excel_headers = [
        "Personnummer",
        "Navn",
        "Adresse",
        "Kommune",
        "Antal policer",
        "Næste behandlingsdato",
    ]

    values = [
        "person__cpr",
        "person__name",
        "person__full_address",
        "person__municipality_name",
        "policy_count",
        "next_processing_date",
    ]

    def should_search(self, form):
        # Allow searching with an unbound form (just the default year)
        return not form.errors


class PersonTaxYearUnfinishedListView(PersonTaxYearSpecialListView):

    template_name = "kas/persontaxyear_unfinished_list.html"
    default_order_by = "-efterbehandling_count"
    filename = "unfinished_person.xlsx"

    def filter_queryset(self, qs):
        qs = super(PersonTaxYearUnfinishedListView, self).filter_queryset(qs)
        return qs.annotate(
            efterbehandling_count=Count(
                "policytaxyear",
                filter=Q(
                    policytaxyear__efterbehandling=True, policytaxyear__active=True
                ),
            ),
        ).filter(efterbehandling_count__gt=0)


class PersonTaxYearFailSendListView(PersonTaxYearSpecialListView):

    template_name = "kas/persontaxyear_failsend_list.html"
    default_order_by = "person__name"
    filename = "failed_eboks.xls"

    def filter_queryset(self, qs):
        return (
            super(PersonTaxYearFailSendListView, self)
            .filter_queryset(qs)
            .filter(tax_slip__status="failed")
        )


class PersonTaxYearUnhandledDocumentsAndNotes(PersonTaxYearSpecialListView):
    template_name = "kas/persontaxyear_unhandled_list.html"
    filename = "unhandled_person.xls"

    def filter_queryset(self, qs):
        return (
            super(PersonTaxYearUnhandledDocumentsAndNotes, self)
            .filter_queryset(qs)
            .filter(all_documents_and_notes_handled=False)
        )


class PersonTaxYearGeneralAndForeignNotesListView(PersonTaxYearSpecialListView):
    template_name = "kas/persontaxyear_foreign.html"
    filename = "udenlandsk_pension.xls"

    def filter_queryset(self, qs):
        qs = super(PersonTaxYearGeneralAndForeignNotesListView, self).filter_queryset(
            qs
        )
        qs = qs.exclude(
            Q(foreign_pension_notes__isnull=True) | Q(foreign_pension_notes__exact=""),
            Q(general_notes__isnull=True) | Q(general_notes__exact=""),
        )
        print(qs.query)
        return qs


class PersonTaxYearEskatDiffListView(PersonTaxYearSpecialListView):
    template_name = "kas/persontaxyear_eskat_diff.html"
    filename = "eskat_diff.xls"

    def filter_queryset(self, qs):
        qs = super(PersonTaxYearEskatDiffListView, self).filter_queryset(qs)
        # find persontaxyears hvor FinalSettlement.pseudo_amount != ImportedKasBeregningerX.capital_return_tax

        qs = qs.annotate(
            pseudo_settlement=FilteredRelation(
                "finalsettlement",
                condition=Q(
                    finalsettlement__pseudo=True, finalsettlement__invalid=False
                ),
            )
        ).annotate(
            pseudo_amount=F("pseudo_settlement__pseudo_amount"),
        )

        qs = qs.annotate(
            capital_return_tax=F("importedkasberegningerx__capital_return_tax")
        )

        qs = qs.exclude(pseudo_amount=F("capital_return_tax"))

        return qs


class PersonTaxYearDetailView(KasMixin, PermissionRequiredWithMessage, DetailView):
    permission_required = "kas.view_persontaxyear"
    template_name = "kas/persontaxyear_detail.html"
    model = PersonTaxYear
    context_object_name = "person_tax_year"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        self.year = self.kwargs.get("year", None)

        if not self.year:
            raise Http404("No year specified")

        self.person_id = self.kwargs.get("person_id", None)

        if not self.person_id:
            raise Http404("No person specified")

        try:
            obj = queryset.get(tax_year__year=self.year, person=self.person_id)
        except queryset.model.DoesNotExist:
            raise Http404("Persontaxyear not found")
        self.object = obj
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context["joined_address"] = "\n".join(
            [
                x or ""
                for x in (
                    self.object.person.address_line_1,
                    self.object.person.address_line_2,
                    self.object.person.address_line_3,
                    self.object.person.address_line_4,
                    self.object.person.address_line_5,
                )
            ]
        )
        context["transactions"] = Transaction.objects.filter(
            person_tax_year=self.object
        ).order_by("-created_at")
        context["person_tax_years"] = PersonTaxYear.objects.filter(
            person=self.object.person
        )
        context["representing"] = RepresentationToken.objects.filter(
            user=self.request.user, consumed=True
        ).first()

        return context


class PersonTaxYearDocumentsAndNotesUpdateView(
    KasMixin, PermissionRequiredWithMessage, SingleObjectMixin, View
):
    permission_required = "kas.change_persontaxyear"
    permission_denied_message = sagsbehandler_or_administrator_required
    model = PersonTaxYear

    def post(self, *args, **kwargs):
        instance = self.get_object()
        instance.all_documents_and_notes_handled = True
        instance.save(update_fields=["all_documents_and_notes_handled"])
        return HttpResponseRedirect(
            reverse(
                "kas:person_in_year",
                kwargs={"year": instance.year, "person_id": instance.person.id},
            )
        )


class NoteUpdateView(KasMixin, PermissionRequiredWithMessage, UpdateView):
    permission_required = "kas.change_note"
    permission_denied_message = sagsbehandler_or_administrator_required
    form_class = NoteUpdateForm
    model = Note
    template_name = "kas/form_with_notes.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        if self.object.policy_tax_year:
            return reverse(
                "kas:policy_detail", kwargs={"pk": self.object.policy_tax_year.pk}
            )
        else:
            return reverse(
                "kas:person_in_year",
                kwargs={
                    "year": self.object.person_tax_year.year,
                    "person_id": self.object.person_tax_year.person.id,
                },
            )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(
            {
                "person_tax_year": self.object.person_tax_year,
                "policy_tax_year": self.object.policy_tax_year,
            }
        )
        return ctx


class PersonNotesAndAttachmentsView(
    KasMixin, PermissionRequiredWithMessage, UpdateView
):
    permission_required = ("kas.add_note", "kas.add_policydocument")
    permission_denied_message = sagsbehandler_or_administrator_or_borgerservice_required
    form_class = PersonNotesAndAttachmentForm
    model = PersonTaxYear
    template_name = "kas/person/add_notes_and_attachment_form.html"

    def get_form_kwargs(self):
        kwargs = super(PersonNotesAndAttachmentsView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse(
            "kas:person_in_year",
            kwargs={"year": self.object.year, "person_id": self.object.person.id},
        )

    def get_context_data(self, **kwargs):
        ctx = super(PersonNotesAndAttachmentsView, self).get_context_data(**kwargs)
        ctx.update({"person_tax_year": self.object})
        return ctx


class PersonRepresentStartView(KasMixin, PermissionRequiredWithMessage, DetailView):
    permission_denied_message = sagsbehandler_or_administrator_required
    permission_required = "kas.add_persontaxyear"
    template_name = "kas/person/represent.html"
    model = Person

    def get_context_data(self, **kwargs):
        token = RepresentationToken.objects.create(
            token=RepresentationToken.generate_token(),
            person=self.object,
            user=self.request.user,
        )
        ctx = super().get_context_data(**kwargs)
        ctx["form_action"] = settings.SELVBETJENING_REPRESENTATION_START
        ctx["form_data"] = {"token": token.token}
        return ctx


class PersonRepresentStopView(KasMixin, PermissionRequiredWithMessage, RedirectView):
    permission_denied_message = sagsbehandler_or_administrator_required
    permission_required = "kas.add_persontaxyear"

    def get_redirect_url(self):
        # There really should be only one, but don't die if there are more
        tokens = RepresentationToken.objects.filter(user=self.request.user)
        token = tokens.first()
        person = None
        if token:
            person = token.person
        tokens.delete()
        if person:
            return reverse(
                "kas:person_in_year",
                kwargs={
                    "year": TaxYear.objects.order_by("-year")
                    .values("year")
                    .first()["year"],
                    "person_id": person.id,
                },
            )
        else:
            return reverse("kas:person_search")


class PolicyTaxYearListView(KasMixin, PermissionRequiredWithMessage, ListView):
    permission_required = "kas.list_persontaxyear"
    permission_denied_message = sagsbehandler_or_administrator_required
    context_object_name = "policytaxyears"
    paginate_by = 20

    model = PolicyTaxYear
    form_class = PolicyListFilterForm

    def get_form(self):
        years = [tax_year.year for tax_year in TaxYear.objects.order_by("year")]
        current_year = timezone.now().year
        if current_year not in years:
            current_year = max([y for y in years if y < current_year])
        initial = {"year": current_year}
        kwargs = {"initial": initial}
        if self.request.GET:
            kwargs["data"] = {**initial, **self.request.GET.dict()}
        return PolicyListFilterForm(**kwargs)

    def should_search(self, form):
        return form.is_valid() and form.has_changed()

    def get_queryset(self):
        form = self.get_form()
        qs = super().get_queryset()
        # Always exclude inactive PolicyTaxYears
        qs = qs.exclude(active=False)
        if self.should_search(form):
            if hasattr(form, "cleaned_data"):
                qs = qs.filter(
                    person_tax_year__tax_year__year=form.cleaned_data["year"]
                    or form.initial["year"]
                )
                # Check whether there are any fields filled out apart from 'year'
                if form.cleaned_data["pension_company"]:
                    qs = qs.filter(
                        pension_company__name__icontains=form.cleaned_data[
                            "pension_company"
                        ]
                    )
                if form.cleaned_data["policy_number"]:
                    qs = qs.filter(
                        policy_number__icontains=form.cleaned_data["policy_number"]
                    )
                if form.cleaned_data["finalized"] is not None:
                    qs = qs.filter(slutlignet=form.cleaned_data["finalized"])
            elif "year" in form.initial:
                qs = qs.filter(person_tax_year__tax_year__year=form.initial["year"])
        else:
            # Don't find anything if form is invalid or empty
            qs = self.model.objects.none()
        self.form = form
        return qs


class PolicyTaxYearSpecialListView(PolicyTaxYearListView):

    default_order_by = "policy_number"

    def should_search(self, form):
        # Allow searching with an unbound form (just the default year)
        return not form.errors

    def get_queryset(self):

        order_by = self.request.GET.get("order_by", self.default_order_by)

        # Handle fields that should always have null last when sorting
        if order_by.endswith("_nulllast"):
            order_by = order_by[:-9]
            if order_by.startswith("-"):
                order_by = F(order_by[1:]).desc(nulls_last=True)
            else:
                order_by = F(order_by).asc(nulls_last=True)

        return self.filter_queryset(super().get_queryset()).order_by(
            order_by, "person_tax_year__person__name", "policy_number"
        )

    def filter_queryset(self, qs):
        return qs


class PolicyTaxYearTaxDifferenceListView(
    SpecialExcelMixin, PolicyTaxYearSpecialListView
):

    template_name = "kas/policytaxyear_taxdifference_list.html"
    default_order_by = "difference_nulllast"
    filename = "selvangivet_forskel_policer.xls"

    excel_headers = [
        "Person",
        "Pensionsselskab",
        "Policenummer",
        "Næste behandlingsdato",
        "Fortrykt beløb",
        "Selvangivet beløb",
        "Forskel",
    ]

    values = [
        "person_tax_year__person__name",
        "pension_company__name",
        "policy_number",
        "next_processing_date",
        "prefilled_amount",
        "self_reported_amount",
        "difference",
    ]

    def filter_queryset(self, qs):
        qs = super(PolicyTaxYearTaxDifferenceListView, self).filter_queryset(qs)

        return (
            qs.filter(
                self_reported_amount__isnull=False, prefilled_amount__isnull=False
            )
            .exclude(self_reported_amount__exact=F("prefilled_amount"))
            .annotate(difference=F("self_reported_amount") - F("prefilled_amount"))
        )


class PolicyTaxYearUnfinishedListView(SpecialExcelMixin, PolicyTaxYearSpecialListView):
    template_name = "kas/policytaxyear_unfinished_list.html"
    default_order_by = "difference_pct_nulllast"
    filename = "efterbehandling_policer.xls"

    excel_headers = [
        "Person",
        "Pensionsselskab",
        "Policenummer",
        "Næste behandlingsdato",
        "Fortrykt beløb",
        "Selvangivet beløb",
        "Forskel",
        "Forskel i procent",
    ]

    values = [
        "person_tax_year__person__name",
        "pension_company__name",
        "policy_number",
        "next_processing_date",
        "prefilled_amount",
        "self_reported_amount",
        "difference",
        "difference_pct",
    ]

    def filter_queryset(self, qs):
        qs = super(PolicyTaxYearUnfinishedListView, self).filter_queryset(qs)
        return (
            qs.filter(efterbehandling=True)
            .annotate(difference=F("self_reported_amount") - F("prefilled_amount"))
            .annotate(
                difference_pct=Case(
                    When(prefilled_amount=0, then=Value(None)),
                    default=F("difference") * 100 / F("prefilled_amount"),
                    output_field=models.IntegerField(),
                )
            )
        )


class PolicyTaxYearTabView(KasMixin, PermissionRequiredWithMessage, ListView):
    permission_required = "kas.view_policytaxyear"
    template_name = "kas/policytaxyear_tabs.html"
    model = PolicyTaxYear

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                person_tax_year__person__id=self.kwargs["person_id"],
                person_tax_year__tax_year__year=self.kwargs["year"],
            )
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        amount_choices_by_value = {
            x[0]: x[1] for x in PolicyTaxYear.active_amount_options
        }
        context["pension_company_amount_label"] = amount_choices_by_value[
            PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED
        ]
        context["self_reported_amount_label"] = amount_choices_by_value[
            PolicyTaxYear.ACTIVE_AMOUNT_SELF_REPORTED
        ]
        return context


class PolicyTaxYearDetailView(
    KasMixin, PermissionRequiredWithMessage, SingleObjectMixin, RedirectView
):
    permission_required = "kas.view_policytaxyear"
    model = PolicyTaxYear

    def get_redirect_url(self, *args, **kwargs):
        # This is so we don't need to implement the logic in several templates
        self.object = self.get_object()
        fragment = f"#policy_{self.object.pk}"
        if "tab" in self.request.GET:
            fragment += f"__{self.request.GET['tab']}"
        return (
            reverse(
                "kas:policy_tabs",
                kwargs={
                    "year": self.object.year,
                    "person_id": self.object.person_tax_year.person_id,
                },
            )
            + fragment
        )


class PolicyTaxYearCreateView(
    KasMixin,
    PermissionRequiredWithMessage,
    CreateOrUpdateViewWithNotesAndDocumentsForPolicyTaxYear,
    CreateView,
):
    permission_required = "kas.add_policytaxyear"
    permission_denied_message = sagsbehandler_or_administrator_required
    form_class = CreatePolicyTaxYearForm
    template_name = "kas/policytaxyear_create.html"

    def get_person_tax_year(self):
        self.year = self.kwargs.get("year", None)
        self.person_id = self.kwargs.get("person_id", None)
        try:
            return PersonTaxYear.objects.get(
                tax_year__year=self.year, person__id=self.person_id
            )
        except PersonTaxYear.DoesNotExist:
            raise Http404

    def get_policy_tax_year(self):
        return getattr(self, "object")

    def form_valid(self, form):
        form.instance.person_tax_year = self.get_person_tax_year()
        form.instance.active_amount = PolicyTaxYear.ACTIVE_AMOUNT_SELF_REPORTED
        if PolicyTaxYear.objects.filter(
            person_tax_year=form.instance.person_tax_year,
            policy_number=form.instance.policy_number,
            pension_company=form.instance.pension_company,
        ).exists():
            form.add_error(None, _("En police med disse oplysninger findes allerede"))
            return super().form_invalid(form)
        return super().form_valid(form)


class PolicyNotesAndAttachmentsView(
    KasMixin, PermissionRequiredWithMessage, UpdateView
):
    permission_required = ("kas.add_note", "kas.add_policydocument")
    permission_denied_message = sagsbehandler_or_administrator_or_borgerservice_required
    model = PolicyTaxYear
    form_class = PolicyNotesAndAttachmentForm
    template_name = "kas/policy/add_notes_and_attachment_form.html"

    def get_success_url(self):
        return reverse("kas:policy_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class PolicyDocumentDownloadView(KasMixin, PermissionRequiredWithMessage, View):
    permission_required = "kas.view_policydocument"

    def get(self, *args, **kwargs):
        document = get_object_or_404(PolicyDocument, pk=kwargs["pk"])
        mime_type, _ = mimetypes.guess_type(document.file.name)
        response = HttpResponse(document.file.read(), content_type=mime_type)
        response["Content-Disposition"] = "attachment; filename=%s" % document.name
        return response


class PdfDownloadView(KasMixin, PermissionRequiredWithMessage, SingleObjectMixin, View):
    permission_required = "kas.view_taxslipgenerated"
    model = TaxSlipGenerated

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        year = self.kwargs.get("year", None)

        if not year:
            raise Http404("No year specified")

        person_id = self.kwargs.get("person_id", None)

        if not person_id:
            raise Http404("No person specified")

        try:
            obj = queryset.get(
                persontaxyear__tax_year__year=year, persontaxyear__person=person_id
            )
        except queryset.model.DoesNotExist:
            raise Http404("PDF not found")

        return obj

    def get(self, *args, **kwargs):

        obj = self.get_object()
        filefield = obj.file
        file_obj = filefield.file

        response = HttpResponse(file_obj.read(), content_type="application/pdf")
        response["Content-Disposition"] = "inline; filename=" + os.path.basename(
            obj.file.file.name
        )

        return response


class SelfReportedAmountUpdateView(
    KasMixin,
    PermissionRequiredWithMessage,
    CreateOrUpdateViewWithNotesAndDocumentsForPolicyTaxYear,
    UpdateView,
):
    permission_required = "kas.change_policytaxyear"
    form_class = SelfReportedAmountForm
    template_name = "kas/form_with_notes.html"
    permission_denied_message = sagsbehandler_or_administrator_required
    allowed_year_parts = ["selvangivelse"]

    def get_queryset(self):
        return PolicyTaxYear.objects.filter(
            person_tax_year__tax_year__year_part="selvangivelse"
        )


class EditAmountsUpdateView(
    KasMixin,
    PermissionRequiredWithMessage,
    CreateOrUpdateViewWithNotesAndDocumentsForPolicyTaxYear,
    UpdateView,
):
    form_class = EditAmountsUpdateForm
    permission_required = "kas.change_policytaxyear"
    template_name = "kas/form_with_notes.html"
    permission_denied_message = sagsbehandler_or_administrator_required

    def get_queryset(self):
        return PolicyTaxYear.objects.filter(
            person_tax_year__tax_year__year_part__in=["ligning", "genoptagelsesperiode"]
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **{
                **kwargs,
                "text_after_form": _(
                    "Bemærk at Selvangivet beløb og Ansat beløb ikke bliver justeret for antal skattedage i året; det antages at beløbene allerede er justerede"
                ),
            }
        )

    def get_form_kwargs(self):
        if self.object.assessed_amount is None:
            # if the assessed amount is not set prefill it
            self.object.assessed_amount = self.object.get_assessed_amount()
        if self.object.prefilled_amount_edited is None:
            # Fill out prefilled_amount_edited since we are not allowed to change prefilled_amount.
            self.object.prefilled_amount_edited = self.object.prefilled_amount
        return super(EditAmountsUpdateView, self).get_form_kwargs()

    def form_valid(self, form):
        if self.has_changes or form.changed_data:
            # if the formsets or the form has changes we need to set efterbehandling=True
            # unless slutlignet=True
            self.object = form.save(False)
            if self.object.slutlignet:
                # always clear efterbehandling when slutlignet is set
                self.object.efterbehandling = False
            else:
                self.object.efterbehandling = True
                # super handles saving of the object
            # When selfreported amount is being used, make sure to set active_amount accordingly
            if self.object.assessed_amount is None:
                if self.object.self_reported_amount is not None:
                    self.object.active_amount = (
                        PolicyTaxYear.ACTIVE_AMOUNT_SELF_REPORTED
                    )
                elif self.object.prefilled_amount is not None:
                    self.object.active_amount = PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED
        return super(EditAmountsUpdateView, self).form_valid(form)


class PolicyPaymentOverrideView(
    KasMixin,
    PermissionRequiredWithMessage,
    CreateOrUpdateViewWithNotesAndDocumentsForPolicyTaxYear,
    UpdateView,
):
    permission_required = "kas.change_policytaxyear"
    permission_denied_message = sagsbehandler_or_administrator_required
    model = PolicyTaxYear
    form_class = PaymentOverrideUpdateForm
    template_name = "kas/form_with_notes.html"

    def form_valid(self, form):
        if self.has_changes or form.changed_data:
            self.object = form.save(False)
            self.object.efterbehandling = True
            # super handles saving of the object (form.instance == self.object)
        return super(PolicyPaymentOverrideView, self).form_valid(form)


class PolicyTaxYearCompanyUpdateView(
    KasMixin,
    PermissionRequiredWithMessage,
    CreateOrUpdateViewWithNotesAndDocumentsForPolicyTaxYear,
    UpdateView,
):
    permission_required = "kas.change_policytaxyear"
    permission_denied_message = sagsbehandler_or_administrator_required
    model = PolicyTaxYear
    form_class = PolicyTaxYearCompanyForm
    template_name = "kas/form_with_notes.html"

    def form_valid(self, form):
        if self.has_changes or form.changed_data:
            self.object = form.save(False)
        return super().form_valid(form)


class PolicyTaxYearNumberUpdateView(
    KasMixin,
    PermissionRequiredWithMessage,
    CreateOrUpdateViewWithNotesAndDocumentsForPolicyTaxYear,
    UpdateView,
):
    permission_required = "kas.change_policytaxyear"
    permission_denied_message = sagsbehandler_or_administrator_required
    model = PolicyTaxYear
    form_class = PolicyTaxYearNumberForm
    template_name = "kas/form_with_notes.html"

    def form_valid(self, form):
        if self.has_changes or form.changed_data:
            self.object = form.save(False)
            if form.cleaned_data["change_related"]:
                # Opdatér andre policer med samme nummer
                old_instance = self.model.objects.get(pk=form.instance.pk)
                siblings = old_instance.same_policy_qs.exclude(pk=form.instance.pk)
                siblings.update(policy_number=self.object.policy_number)
        return super().form_valid(form)


class PensionCompanySummaryFileView(
    KasMixin,
    PermissionRequiredWithMessage,
    HighestSingleObjectMixin,
    MultipleObjectMixin,
    FormView,
):
    permission_required = "kas.add_pensioncompanysummaryfile"
    model = TaxYear
    form_class = PensionCompanySummaryFileForm
    template_name = "kas/policycompanysummary_list.html"
    paginate_by = 20
    slug_url_kwarg = "year"
    slug_field = "year"

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        return super().get_context_data(
            **{
                "object_list": PensionCompanySummaryFile.objects.filter(
                    tax_year=self.object
                ).order_by("company", "-created"),
                "years": TaxYear.objects.values_list("year", flat=True).order_by(
                    "-year"
                ),
                **kwargs,
            }
        )

    def get_success_url(self):
        return reverse(
            "kas:policy_summary_list", kwargs={"year": self.get_object().year}
        )

    def form_valid(self, form):
        self.object = self.get_object()
        file_entry = PensionCompanySummaryFile.create(
            form.cleaned_data["pension_company"], self.object, self.request.user
        )
        # Instruct the client to download the file after refreshing the page
        return HttpResponseRedirect(
            self.get_success_url() + f"?download={file_entry.id}"
        )


class PensionCompanySummaryFileDownloadView(
    KasMixin, PermissionRequiredWithMessage, BaseDetailView
):
    permission_required = "kas.view_pensioncompanysummaryfile"
    model = PensionCompanySummaryFile

    # Register info about who is downloading, and serve the file
    def render_to_response(self, context):
        client_ip, is_routable = get_client_ip(self.request)
        PensionCompanySummaryFileDownload.objects.create(
            downloaded_by=self.request.user, downloaded_to=client_ip, file=self.object
        )
        response = HttpResponse(self.object.file, content_type="text/csv")
        response["Content-Length"] = self.object.file.size
        response[
            "Content-Disposition"
        ] = f"attachment; filename={os.path.basename(self.object.file.name)}"
        return response


class ActivatePolicyTaxYearView(KasMixin, PermissionRequiredWithMessage, UpdateView):
    permission_required = "kas.change_policytaxyear"
    permission_denied_message = sagsbehandler_or_administrator_required
    form_class = PolicyTaxYearActivationForm
    model = PolicyTaxYear

    def get_success_url(self):
        return reverse("kas:policy_detail", kwargs=self.kwargs)


class PersonTaxYearHistoryListView(KasMixin, PermissionRequiredWithMessage, DetailView):
    """
    shows all changes related to a person tax year
    """

    permission_required = "kas.view_policytaxyear"
    model = PersonTaxYear
    template_name = "kas/persontaxyear_historical_list.html"

    def get_context_data(self, **kwargs):
        ctx = super(PersonTaxYearHistoryListView, self).get_context_data(**kwargs)

        qs = (
            self.object.history.all()
            .annotate(
                klass=models.Value("PersonTaxYear", output_field=models.CharField()),
            )
            .values_list(
                "history_date",
                "history_id",
                "history_user__username",
                "history_change_reason",
                "history_type",
                "updated_by",
                "klass",
            )
        )

        person_qs = (
            self.object.person.history.all()
            .annotate(
                klass=models.Value("Person", output_field=models.CharField()),
                updated_by=models.Value(None, output_field=models.CharField()),
            )
            .values_list(
                "history_date",
                "history_id",
                "history_user__username",
                "history_change_reason",
                "history_type",
                "updated_by",
                "klass",
            )
        )

        policy_qs = (
            PolicyTaxYear.history.filter(person_tax_year=self.object)
            .annotate(
                klass=models.Value("Policy", output_field=models.CharField()),
            )
            .values_list(
                "history_date",
                "id",
                "history_user__username",
                "history_change_reason",
                "history_type",
                "updated_by",
                "klass",
            )
        )

        notes_qs = (
            Note.objects.filter(person_tax_year=self.object)
            .annotate(
                history_type=models.Value("+", output_field=models.CharField()),
                klass=models.Value("Note", output_field=models.CharField()),
                updated_by=models.Value(None, output_field=models.CharField()),
            )
            .values_list(
                "date",
                "id",
                "author__username",
                "content",
                "history_type",
                "updated_by",
                "klass",
            )
        )

        documents_qs = (
            PolicyDocument.objects.filter(person_tax_year=self.object)
            .annotate(
                history_type=models.Value("+", output_field=models.CharField()),
                klass=models.Value("PolicyDocument", output_field=models.CharField()),
            )
            .values_list(
                "uploaded_at",
                "id",
                "uploaded_by__username",
                "description",
                "history_type",
                "uploaded_by__username",
                "klass",
            )
        )

        # generated tax slips
        tax_slip_generated_qs = (
            TaxSlipGenerated.objects.filter(persontaxyear=self.object)
            .annotate(
                created_by=models.Value("", output_field=models.CharField()),
                description=models.Value("Generated", output_field=models.CharField()),
                history_type=models.Value("+", output_field=models.CharField()),
                klass=models.Value("TaxSlipGenerated", output_field=models.CharField()),
                updated_by=models.Value(None, output_field=models.CharField()),
            )
            .values_list(
                "created_at",
                "id",
                "created_by",
                "description",
                "history_type",
                "updated_by",
                "klass",
            )
        )

        # send tax slips
        tax_slip_sendt_qs = (
            TaxSlipGenerated.objects.filter(persontaxyear=self.object)
            .exclude(send_at__isnull=True)
            .annotate(
                created_by=models.Value("", output_field=models.CharField()),
                description=models.Value("Send", output_field=models.CharField()),
                history_type=models.Value("~", output_field=models.CharField()),
                klass=models.Value("TaxSlipGenerated", output_field=models.CharField()),
                updated_by=models.Value(None, output_field=models.CharField()),
            )
            .values_list(
                "send_at",
                "id",
                "created_by",
                "description",
                "history_type",
                "updated_by",
                "klass",
            )
        )

        final_settlement_generated_qs = (
            FinalSettlement.objects.filter(person_tax_year=self.object)
            .annotate(
                id=models.Value(0, output_field=models.IntegerField()),
                created_by=models.Value("", output_field=models.CharField()),
                description=models.Value("Generated", output_field=models.CharField()),
                history_type=models.Value("+", output_field=models.CharField()),
                klass=models.Value("FinalSettlement", output_field=models.CharField()),
                updated_by=models.Value("", output_field=models.CharField()),
            )
            .values_list(
                "created_at",
                "id",
                "created_by",
                "description",
                "history_type",
                "updated_by",
                "klass",
            )
        )

        final_settlement_send_qs = (
            FinalSettlement.objects.filter(person_tax_year=self.object)
            .exclude(send_at__isnull=True)
            .annotate(
                id=models.Value(1, output_field=models.IntegerField()),
                created_by=models.Value("", output_field=models.CharField()),
                description=models.Value("Send", output_field=models.CharField()),
                history_type=models.Value("~", output_field=models.CharField()),
                klass=models.Value("FinalSettlement", output_field=models.CharField()),
                updated_by=models.Value("", output_field=models.CharField()),
            )
            .values_list(
                "send_at",
                "id",
                "created_by",
                "description",
                "history_type",
                "updated_by",
                "klass",
            )
        )

        # It appears that queryset.union() doesn't give the correct output, specifically putting values under the wrong keys
        # e.g. putting the `klass` value under the `updated_by` key for items from _some_ querysets
        # So instead we extract the values from each queryset and join them together in code
        items = []
        keys = (
            "history_date",
            "history_id",
            "history_user__username",
            "history_change_reason",
            "history_type",
            "updated_by",
            "klass",
        )
        for queryset in (
            qs,
            policy_qs,
            person_qs,
            notes_qs,
            documents_qs,
            tax_slip_generated_qs,
            tax_slip_sendt_qs,
            final_settlement_generated_qs,
            final_settlement_send_qs,
        ):
            for obj in queryset:
                items.append({key: obj[index] for index, key in enumerate(keys)})
        items.sort(key=lambda item: item["history_date"], reverse=True)
        ctx["objects"] = items

        #         ctx['objects'] = qs.union(policy_qs, person_qs, notes_qs, documents_qs,
        #                                   tax_slip_generated_qs, tax_slip_sendt_qs, final_settlement_generated_qs,
        #                                   final_settlement_send_qs,
        #                                   all=True).order_by('-history_date')

        return ctx


class PersonTaxYearHistoryDetailView(
    KasMixin, PermissionRequiredWithMessage, DetailView
):
    """
    Shows a specific "version" of a person_tax_year
    """

    model = PersonTaxYear.history.model
    permission_required = "kas.view_policytaxyear"
    slug_field = "history_id"
    template_name = "kas/persontaxyear_detail.html"
    context_object_name = "person_tax_year"

    def get_context_data(self, **kwargs):
        ctx = super(PersonTaxYearHistoryDetailView, self).get_context_data(**kwargs)
        ctx["historical"] = True
        return ctx


class PolicyTaxYearHistoryListView(KasMixin, PermissionRequiredWithMessage, DetailView):
    permission_required = "kas.view_policytaxyear"
    model = PolicyTaxYear
    template_name = "kas/policytaxyear_historical_list.html"

    def get_context_data(self, **kwargs):
        ctx = super(PolicyTaxYearHistoryListView, self).get_context_data(**kwargs)

        qs = (
            self.object.history.all()
            .annotate(
                klass=models.Value("Policy", output_field=models.CharField()),
            )
            .values(
                "history_date",
                "history_user__username",
                "history_id",
                "history_change_reason",
                "history_type",
                "klass",
                "updated_by",
            )
        )
        notes_qs = (
            Note.objects.filter(policy_tax_year=self.object)
            .annotate(
                history_type=models.Value("+", output_field=models.CharField()),
                klass=models.Value("Note", output_field=models.CharField()),
            )
            .values(
                "date",
                "author__username",
                "id",
                "content",
                "history_type",
                "klass",
                "policy_tax_year__updated_by",
            )
        )
        documents_qs = (
            PolicyDocument.objects.filter(policy_tax_year=self.object)
            .annotate(
                history_type=models.Value("+", output_field=models.CharField()),
                klass=models.Value("PolicyDocument", output_field=models.CharField()),
            )
            .values(
                "uploaded_at",
                "uploaded_by__username",
                "id",
                "description",
                "history_type",
                "klass",
                "policy_tax_year__updated_by",
            )
        )
        ctx["objects"] = qs.union(notes_qs, documents_qs, all=True).order_by(
            "-history_date"
        )
        return ctx


class PolicyTaxYearHistoryDetailView(
    KasMixin, PermissionRequiredWithMessage, DetailView
):
    permission_required = "kas.view_policytaxyear"
    model = PolicyTaxYear.history.model
    slug_field = "history_id"
    template_name = "kas/policytaxyear_detail.html"
    context_object_name = "policy"

    def get_context_data(self, **kwargs):
        ctx = super(PolicyTaxYearHistoryDetailView, self).get_context_data(**kwargs)
        ctx["historical"] = True
        return ctx


class FinalSettlementDownloadView(
    KasMixin, PermissionRequiredWithMessage, SingleObjectMixin, View
):
    permission_required = "kas.view_finalsettlement"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    model = FinalSettlement

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        response = HttpResponse(self.object.pdf.read(), content_type="application/pdf")
        response[
            "Content-Disposition"
        ] = "attachment; filename={year}_{cpr}.pdf".format(
            year=self.object.person_tax_year.tax_year.year,
            cpr=self.object.person_tax_year.person.cpr,
        )
        return response


class FinalSettlementGenerateView(
    KasMixin, PermissionRequiredWithMessage, SingleObjectMixin, FormView
):
    permission_required = "kas.add_finalsettlement"
    permission_denied_message = sagsbehandler_or_administrator_required
    model = PersonTaxYear
    template_name = "kas/finalstatement_generate.html"
    form_class = FinalStatementForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(FinalSettlementGenerateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(FinalSettlementGenerateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        if not self.object.policytaxyear_set.exists():
            return HttpResponse(
                status=400,
                content=_(
                    "Der skal mindst være én police for at generere en slutopgørelse"
                ),
            )
        if self.object.tax_year.year_part != "genoptagelsesperiode":
            return HttpResponse(
                status=400,
                content=_(
                    "Der kan kun genereres nye slutopgørelser hvis året er i genoptagelsesperioden"
                ),
            )

        final_statement = TaxFinalStatementPDF.generate_pdf(
            person_tax_year=self.object, **form.cleaned_data
        )

        if final_statement.get_transaction_amount() != 0:
            collect_date = get_due_date(date.today())

            prisme10Q_batch = Prisme10QBatch.objects.create(
                created_by=self.request.user,
                tax_year=self.object.tax_year,
                collect_date=collect_date,
            )
            prisme10Q_batch.add_transaction(final_statement)

        messages.add_message(
            self.request,
            messages.INFO,
            _("Ny slutopgørelse genereret for %(person)s for %(år)s")
            % {"person": self.object.person.name, "år": str(self.object.tax_year.year)},
        )

        return HttpResponseRedirect(
            reverse(
                "kas:person_in_year",
                kwargs={"year": self.object.year, "person_id": self.object.person.id},
            )
        )


class MarkFinalSettlementAsInvalid(
    PermissionRequiredWithMessage, SingleObjectMixin, View
):
    permission_required = "kas.change_finalsettlement"
    permission_denied_message = sagsbehandler_or_administrator_required
    model = FinalSettlement

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status != "created":
            return HttpResponse(
                status=400,
                content=_(
                    "Du kan kun markere slutopgørelser der ikke er afsendt som ugyldige."
                ),
            )
        self.object.invalid = True
        self.object.save(update_fields=["invalid"])
        return HttpResponseRedirect(
            reverse(
                "kas:person_in_year",
                kwargs={
                    "year": self.object.person_tax_year.year,
                    "person_id": self.object.person_tax_year.person.id,
                },
            )
        )


class DispatchFinalSettlement(PermissionRequiredWithMessage, UpdateView):
    permission_required = "kas.change_finalsettlement"
    permission_denied_message = sagsbehandler_or_administrator_required
    """
    used to create a job that dispatches a single final settlement
    """

    fields = ("title",)

    def get_queryset(self):
        return FinalSettlement.objects.exclude(invalid=True).filter(
            status__in=["created", "failed"],
            person_tax_year__tax_year__year_part="genoptagelsesperiode",
        )

    def form_valid(self, form):
        r = super(DispatchFinalSettlement, self).form_valid(form)
        Job.schedule_job(
            dispatch_final_settlement,
            job_type="DispatchFinalSettlement",
            created_by=self.request.user,
            job_kwargs={"uuid": str(self.object.uuid)},
        )

        try:
            transaction = Transaction.objects.get(
                object_id=self.object.pk,
                source_content_type=ContentType.objects.get_for_model(
                    FinalSettlement
                ).id,
            )
            batch = transaction.prisme10Q_batch
            return HttpResponseRedirect(
                reverse("prisme:batch-send", kwargs={"pk": batch.pk})
            )
        except Transaction.DoesNotExist:
            return r

    def get_success_url(self):
        return reverse(
            "kas:person_in_year",
            kwargs={
                "year": self.object.person_tax_year.year,
                "person_id": self.object.person_tax_year.person.id,
            },
        )


class UploadExistingFinalSettlementView(
    KasMixin, PermissionRequiredWithMessage, UpdateView
):
    form_class = UploadExistingFinalSettlementForm
    permission_required = "kas.change_finalsettlement"
    permission_denied_message = sagsbehandler_or_administrator_required

    def get_queryset(self):
        return FinalSettlement.objects.filter(pseudo=True, invalid=False)

    def form_valid(self, form):
        self.object = form.save()
        transaction = self.object.get_transaction()
        if transaction is not None:
            transaction.amount = self.object.pseudo_amount
            transaction.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        person_tax_year = self.object.person_tax_year
        return (
            reverse(
                "kas:person_in_year",
                kwargs={
                    "year": person_tax_year.year,
                    "person_id": person_tax_year.person.id,
                },
            )
            + "#settlement"
        )


class UpdateSingleMandtal(PermissionRequiredWithMessage, SingleObjectMixin, View):
    permission_required = "kas.change_persontaxyear"
    permission_denied_message = sagsbehandler_or_administrator_required
    model = PersonTaxYear
    job = None

    def post(self, request, *args, **kwargs):

        obj = self.get_object()
        job = None

        try:
            job = Job.schedule_job(
                import_mandtal,
                job_type="ImportMandtalJob",
                created_by=self.request.user,
                job_kwargs={
                    "year": obj.year,
                    "cpr": obj.person.cpr,
                },
            )
        except Exception as e:
            print(e)
            raise e
            messages.add_message(
                request,
                messages.ERROR,
                _("Kunne ikke job for import af mandtal for enkelt person"),
            )
            return HttpResponseRedirect(
                reverse(
                    "kas:person_in_year",
                    kwargs={"year": obj.year, "person_id": obj.person.id},
                )
            )

        return HttpResponseRedirect(
            reverse("kas:wait_for_mandtal_update", kwargs={"pk": job.pk})
        )


class WaitForSingleMandtal(
    PermissionRequiredWithMessage, SingleObjectMixin, TemplateView
):
    permission_required = "kas.change_persontaxyear"
    permission_denied_message = sagsbehandler_or_administrator_required
    model = Job
    template_name = "kas/wait_for_single_mandtal.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.person_tax_year = PersonTaxYear.objects.filter(
            tax_year__year=self.object.arguments["year"],
            person__cpr=self.object.arguments["cpr"],
        ).first()

        if self.object.status == "finished":
            messages.add_message(request, messages.INFO, _("Mandtal opdateret"))
            return HttpResponseRedirect(
                reverse(
                    "kas:person_in_year",
                    kwargs={
                        "year": self.person_tax_year.year,
                        "person_id": self.person_tax_year.person.id,
                    },
                )
            )

        return super(WaitForSingleMandtal, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)

        result["person_tax_year"] = self.person_tax_year
        result["elapsed"] = (timezone.now() - self.object.created_at).total_seconds()
        result["timed_out"] = result["elapsed"] > 60

        return result


class PensionCompanyFormView(KasMixin, PermissionRequiredWithMessage, FormView):
    """
    Renders the pensioncompany list template and
    handles the start merge job form post.
    """

    template_name = "kas/pensioncompany_list.html"
    form_class = PensionCompanyMergeForm
    permission_required = "kas.change_pensioncompany"
    permission_denied_message = sagsbehandler_or_administrator_required

    def form_valid(self, form):
        redirect_response = super(PensionCompanyFormView, self).form_valid(form)
        target = form.cleaned_data["target"].pk
        to_be_merged = list(
            form.cleaned_data["to_be_merged"].values_list("pk", flat=True)
        )
        job = Job.schedule_job(
            merge_pension_companies,
            "MergeCompanies",
            created_by=self.request.user,
            job_kwargs={"target": target, "to_be_merged": to_be_merged},
        )
        messages.add_message(
            self.request,
            messages.INFO,
            mark_safe(
                '<a href="%s">Flette job started</a>'
                % (reverse("worker:job_detail", kwargs={"uuid": job.uuid}))
            ),
        )
        return redirect_response

    def form_invalid(self, form):
        # raise None field errors as messages
        messages.add_message(self.request, messages.ERROR, form.non_field_errors())
        return super(PensionCompanyFormView, self).form_invalid(form)

    def get_success_url(self):
        return reverse("kas:pensioncompany-listview")


class PensionCompanyHtmxView(KasMixin, PermissionRequiredWithMessage, FilterView):
    """
    returns a  list of pension selskaber.
    """

    template_name = "kas/htmx/pensioncompany_list.html"
    filterset_class = PensionCompanyFilterSet
    permission_required = "kas.view_pensioncompany"
    permission_denied_message = sagsbehandler_or_administrator_required

    def get_queryset(self):
        last_id = self.kwargs.get("last_id")
        q = PensionCompany.objects.prefetch_related("policytaxyear_set")
        if last_id:
            last_object = get_object_or_404(PensionCompany, pk=last_id)
            q = q.filter(name__gt=last_object.name)
        return q.order_by("name").annotate(policies_count=Count("policytaxyear"))

    def get_context_data(self, object_list=None, **kwargs):
        return super(PensionCompanyHtmxView, self).get_context_data(
            object_list=object_list[:20], kwargs=kwargs
        )


class PensionCompanyUpdateView(KasMixin, PermissionRequiredWithMessage, UpdateView):
    form_class = PensionCompanyModelForm
    model = PensionCompany
    permission_required = "kas.change_pensioncompany"
    permission_denied_message = sagsbehandler_or_administrator_required

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.INFO,
            _("Pensionsselskabet %(company)s blev opdateret.")
            % {"company": self.object.name},
        )
        return reverse("kas:pensioncompany-listview")


class AgreementDownloadView(KasMixin, PermissionRequiredWithMessage, View):
    permission_required = "kas.view_pensioncompany"

    def get(self, *args, **kwargs):
        company = get_object_or_404(PensionCompany, pk=kwargs["pk"])
        if company.agreement is None:
            raise Http404("No such document")
        mime_type, _ = mimetypes.guess_type(company.agreement.name)
        response = HttpResponse(company.agreement.read(), content_type=mime_type)
        response["Content-Disposition"] = (
            "attachment; filename=%s" % company.agreement.name
        )
        return response


class FeatureFlagView(KasMixin, LoginRequiredMixin, TemplateView):
    template_name = "kas/feature_flag_list.html"


class LockFilterView(KasMixin, PermissionRequiredWithMessage, FilterView):
    filterset_class = LockFilterSet
    queryset = Lock.objects.none()
    permission_required = "kas.view_lock"
    permission_denied_message = administrator_required


class LocksHtmxView(KasMixin, PermissionRequiredWithMessage, FilterView):
    """
    Returns a list of Locks, rendered as TR`s used by htmx.
    """

    filterset_class = LockFilterSet
    queryset = Lock.objects.all().annotate(settlements_count=Count("settlements"))
    permission_required = "kas.view_lock"
    permission_denied_message = administrator_required
    template_name = "kas/lock/locks_tr.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super(LocksHtmxView, self).get_context_data(
            object_list=object_list, **kwargs
        )
        ctx["object_list"] = sorted(
            ctx.get("object_list", []),
            key=lambda x: x.remaining_transaction_sum,
            reverse=True,
        )
        return ctx


class CreateLockForYearTemplateView(
    KasMixin, PermissionRequiredWithMessage, TemplateView
):
    permission_required = "kas.change_lock"
    permission_denied_message = administrator_required
    template_name = "kas/lock/allow.html"

    def get_context_data(self, **kwargs):
        """
        For get requests return the context for the modal,
        stating if it is allowed to create a new lock or not.
        """
        kwargs["object"] = get_object_or_404(
            TaxYear, pk=self.request.GET.get("taxyear")
        )
        return super(CreateLockForYearTemplateView, self).get_context_data(**kwargs)

    def post(self, request):
        tax_year = get_object_or_404(TaxYear, pk=request.POST.get("taxyear"))
        if tax_year.get_current_lock.allow_closing:
            with transaction.atomic():
                today = timezone.now().date()
                tax_year.get_current_lock.interval_to = today
                # Create new open lock
                Lock.objects.create(taxyear=tax_year, interval_from=today)
                tax_year.get_current_lock.save(update_fields=["interval_to"])
        return HttpResponseRedirect(
            reverse("kas:locks-htmxview") + f"?taxyear={tax_year.pk}"
        )


class LockDetailView(KasMixin, PermissionRequiredWithMessage, DetailView):
    """
    Shows the finalsettlements belonging to the chosen lock (PK).
    Also allows the list of finalsettlements to be downloaded as an excel file.
    """

    permission_required = "kas.view_lock"
    permission_denied_message = administrator_required
    model = Lock
    excel_headers = [
        "Personnummer",
        "Navn",
        "Samlet beregnet skat",
        "Samlede overførsler til Prisme",
        "Udestående",
    ]

    def get_context_data(self, **kwargs):
        ctx = super(LockDetailView, self).get_context_data(**kwargs)
        ctx["object_list"] = sorted(
            self.object.settlements.all(),
            key=lambda x: x.remaining_transaction_sum,
            reverse=True,
        )
        return ctx

    def render_to_response(self, context, **response_kwargs):
        if self.kwargs.get("format") == "excel":
            wb = Workbook(write_only=True)
            ws = wb.create_sheet()
            ws.append(self.excel_headers)
            for settlement in context.get("object_list"):
                ws.append(
                    [
                        settlement.person_tax_year.person.cpr,
                        settlement.person_tax_year.person.name,
                        settlement.total_tax,
                        settlement.previous_transactions_sum,
                        settlement.remaining_transaction_sum,
                    ]
                )
            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = "attachment; filename={}".format(
                "export.xlsx"
            )
            wb.save(response)
            return response
        return super(LockDetailView, self).render_to_response(
            context, **response_kwargs
        )


class AgterskrivelseView(KasMixin, PermissionRequiredWithMessage, DetailView):
    model = Agterskrivelse
    permission_required = "kas.view_agterskrivelse"
    permission_denied_message = administrator_required

    def get(self, request, *args, **kwargs):
        agterskrivelse = self.get_object()
        return FileResponse(agterskrivelse.pdf)


class BaseNegativePayoutView(BaseDetailView):
    model = PreviousYearNegativePayout

    def get_policy_tax_year(self):
        return PolicyTaxYear.objects.get(pk=self.kwargs["pk"])

    def get_back_url(self):
        """
        returns an URL which sends you back to the proper:
            - person tax year
            - policy tax year
            - negative payout tab
        """
        policy_tax_year = self.get_policy_tax_year()
        person_tax_year = policy_tax_year.person_tax_year

        return (
            reverse(
                "kas:policy_tabs",
                kwargs={
                    "year": self.request.GET.get("back") or person_tax_year.year,
                    "person_id": person_tax_year.person.id,
                },
            )
            + "#policy_%d__negativ" % policy_tax_year.pk
        )


class UpdatePreviousYearNegativePayoutView(BaseNegativePayoutView, UpdateView):
    form_class = PreviousYearNegativePayoutForm
    template_name = "kas/previousyearnegativepayoutdefined_form.html"
    model = PreviousYearNegativePayout

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        from_year = self.kwargs["from"]
        to_year = self.kwargs["to"]
        latest_policy = self.get_policy_tax_year().latest_policy

        deduction_table = latest_policy.previous_year_deduction_table_data

        deduction = deduction_table[from_year]

        kwargs.update(
            {
                "limit": deduction["used_max_by_year"][to_year],
                "initial": {
                    "transferred_negative_payout": deduction["used_by_year"][to_year],
                    "protected_against_recalculations": True,
                },
            }
        )
        return kwargs

    def get_object(self):

        if self.kwargs["to"] <= self.kwargs["from"]:
            raise SuspiciousOperation("This cell cannot be edited")

        try:
            # Find the entry which needs to be modified in the database
            policy_tax_year = self.get_policy_tax_year()
            policies = policy_tax_year.same_policy_qs

            return self.model.objects.get(
                used_from__person_tax_year__tax_year__year=self.kwargs["from"],
                used_for__person_tax_year__tax_year__year=self.kwargs["to"],
                used_from__in=policies,
                used_for__in=policies,
            )
        except self.model.DoesNotExist:
            # Return an empty object - if there is no entry in the database yet
            used_from = policy_tax_year.same_policy_qs.get(
                person_tax_year__tax_year__year=self.kwargs["from"],
            )
            used_for = policy_tax_year.same_policy_qs.get(
                person_tax_year__tax_year__year=self.kwargs["to"],
            )

            created_object = self.model.objects.create(
                used_from=used_from, used_for=used_for, transferred_negative_payout=0
            )

            created_object.history.last().delete()

            return created_object

    def get_success_url(self):
        return self.get_back_url()

    def get_context_data(self, **kwargs):
        ctx = super(UpdatePreviousYearNegativePayoutView, self).get_context_data(
            **kwargs
        )

        ctx["back_url"] = self.get_back_url()

        policy_tax_year = self.get_policy_tax_year()
        deduction_table = (
            policy_tax_year.latest_policy.previous_year_deduction_table_data
        )

        used_in_this_for_year = []
        for year_from in deduction_table.keys():
            value = deduction_table[year_from]["used_by_year"][self.kwargs["to"]]
            if value != "-":
                used_in_this_for_year.append(value)

        ctx["assessed_amount"] = deduction_table[self.kwargs["to"]]["used_max"]
        ctx["used_this_for_year"] = sum(used_in_this_for_year)

        ctx["year_to"] = self.kwargs["to"]
        ctx["year_from"] = self.kwargs["from"]

        ctx["negative_payout"] = deduction_table[self.kwargs["from"]]["available"]
        ctx["remaining_negative_payout"] = deduction_table[self.kwargs["from"]][
            "remaining"
        ]

        ctx["current_amount"] = deduction_table[self.kwargs["from"]]["used_by_year"][
            self.kwargs["to"]
        ]

        ctx["limit"] = self.get_form_kwargs()["limit"]

        return ctx


class PreviousYearNegativePayoutHistoryListView(
    BaseNegativePayoutView, PermissionRequiredWithMessage, DetailView
):
    permission_required = "kas.view_policytaxyear"
    model = PreviousYearNegativePayout
    template_name = "kas/previousyearnegativepayoutdefined_history.html"

    def get_object(self):
        policy_tax_year = self.get_policy_tax_year()
        policies = policy_tax_year.same_policy_qs

        try:
            return self.model.objects.get(
                used_from__person_tax_year__tax_year__year=self.kwargs["from"],
                used_for__person_tax_year__tax_year__year=self.kwargs["to"],
                used_from__in=policies,
                used_for__in=policies,
            )
        except self.model.DoesNotExist:
            raise Http404("There is no history for this cell")

    def get_context_data(self, **kwargs):
        ctx = super(PreviousYearNegativePayoutHistoryListView, self).get_context_data(
            **kwargs
        )
        ctx["objects"] = self.object.history.order_by("-history_date")
        ctx["back_url"] = self.get_back_url()

        return ctx


class KasLoginView(KasMixin, LoginView):
    template_name = "kas/login.html"
