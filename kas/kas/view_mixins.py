from datetime import date

from django.conf import settings
from django.forms import formset_factory
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import formats
from django.utils.formats import date_format
from django.utils.http import urlencode
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.utils.translation import to_locale
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin
from openpyxl import Workbook

from kas.forms import NoteForm, PolicyDocumentForm
from kas.models import PersonTaxYear, PolicyTaxYear


class BootstrapTableMixin:
    def get_context_data(self, **kwargs):
        ctx = super(BootstrapTableMixin, self).get_context_data(**kwargs)
        lang = get_language()
        ctx["table_locale"] = to_locale(lang).replace("_", "-")  # da-DK
        ctx["lang_locale"] = ctx["table_locale"].split("-")[0]  # da, de etc
        ctx["date_format"] = formats.get_format("SHORT_DATE_FORMAT", lang=lang)
        return ctx


class CreateOrUpdateViewWithNotesAndDocuments:
    """
    Should work in combination with a Create or Update View.
    Expects the pk of a PersonTaxYear located in the url.
    can be used with 'includes/notes_and_documents_form.html'
    """

    def __init__(self, **kwargs):
        super(CreateOrUpdateViewWithNotesAndDocuments, self).__init__(**kwargs)
        self.NoteFormSet = formset_factory(NoteForm)
        self.UploadFormSet = formset_factory(PolicyDocumentForm)
        self.has_changes = False  # tracks if either formsets have changed

    def get_person_tax_year(self):
        """
        Should always return a PersonTaxYear.
        By default we look for the url param pk.
        Could be used to lookup related instances if the PK passed in related to another model.
        Override as needed.
        """
        if not hasattr(self, "person_tax_year"):
            self.person_tax_year = get_object_or_404(
                PersonTaxYear, id=self.kwargs["pk"]
            )
        return self.person_tax_year

    def get_policy_tax_year(self):
        return None

    def get_context_data(self, **kwargs):
        context = super(CreateOrUpdateViewWithNotesAndDocuments, self).get_context_data(
            **kwargs
        )
        context.update(
            {
                "notes_formset": self.NoteFormSet(prefix="notes"),
                "upload_formset": self.UploadFormSet(prefix="uploads"),
                "person_tax_year": self.get_person_tax_year(),
            }
        )
        return context

    def form_valid(self, form):
        note_form_set = self.NoteFormSet(self.request.POST, prefix="notes")
        for note_form in note_form_set:
            if note_form.has_changed():
                note = note_form.save(commit=False)
                note.person_tax_year = self.get_person_tax_year()
                note.author = self.request.user
                note.policy_tax_year = self.get_policy_tax_year()
                note.save()
                self.has_changes = True

        upload_form_set = self.UploadFormSet(
            self.request.POST, self.request.FILES, prefix="uploads"
        )
        for upload_form in upload_form_set:
            if upload_form.has_changed():  # no file no upload
                document = upload_form.save(commit=False)
                document.person_tax_year = self.get_person_tax_year()
                document.uploaded_by = self.request.user
                document.name = document.file.name
                document.policy_tax_year = self.get_policy_tax_year()
                document.save()
                self.has_changes = True

        return super(CreateOrUpdateViewWithNotesAndDocuments, self).form_valid(form)

    def get_success_url(self):
        """
        return to the person detail page.
        """
        return reverse(
            "kas:person_in_year",
            kwargs={
                "year": self.get_person_tax_year().year,
                "person_id": self.get_person_tax_year().person_id,
            },
        )


class CreateOrUpdateViewWithNotesAndDocumentsForPolicyTaxYear(
    CreateOrUpdateViewWithNotesAndDocuments
):
    def get_policy_tax_year(self):
        """
        Should always return a PolicyTaxYear.
        By default we look for the url param pk.
        Could be used to lookup related instances if the PK passed in related to another model.
        Override as needed.
        """
        if not hasattr(self, "policy_tax_year"):
            self.policy_tax_year = get_object_or_404(
                PolicyTaxYear, id=self.kwargs["pk"]
            )
        return self.policy_tax_year

    def get_person_tax_year(self):
        """
        Should not be overriden.
        Handles setting the persontaxyear "automatically". based on policytaxyear.
        """
        return self.get_policy_tax_year().person_tax_year

    def get_context_data(self, **kwargs):
        context = {"policy_tax_year": self.get_policy_tax_year()}
        context.update(
            super(
                CreateOrUpdateViewWithNotesAndDocumentsForPolicyTaxYear, self
            ).get_context_data(**kwargs)
        )
        return context

    def get_success_url(self):
        """
        By default return to the policy-detail page
        """
        return reverse("kas:policy_detail", args=[self.get_policy_tax_year().pk])


class HighestSingleObjectMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        try:
            return super(HighestSingleObjectMixin, self).get_object(queryset)
        except AttributeError:
            if queryset is None:
                queryset = self.get_queryset()
            item = queryset.order_by(f"-{self.slug_field}").first()
            if item is None:
                raise Http404(
                    _("No %(verbose_name)s found matching the query")
                    % {"verbose_name": queryset.model._meta.verbose_name}
                )
            return item


class SpecialExcelMixin(object):
    excel_headers = []
    values = []
    filename = "spreadsheet.xlsx"

    def get_context_data(self, *args, **kwargs):
        ctx = super(SpecialExcelMixin, self).get_context_data(*args, **kwargs)
        params = self.request.GET.copy()
        params["format"] = "excel"
        ctx.update({"excel_link": "?{}".format(params.urlencode())})
        return ctx

    def render_excel_file(self, queryset):
        wb = Workbook(write_only=True)
        ws = wb.create_sheet()
        ws.append(self.excel_headers)
        for row in queryset.values_list(*self.values):
            row = list(row)
            for i, value in enumerate(row):
                if isinstance(value, date):
                    row[i] = date_format(
                        value, format="SHORT_DATE_FORMAT", use_l10n=True
                    )
            ws.append(row)

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename={}".format(
            self.filename
        )
        wb.save(response)
        return response

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get("format") == "excel":
            return self.render_excel_file(self.get_queryset())
        return super(SpecialExcelMixin, self).render_to_response(
            context, **response_kwargs
        )


class KasMixin(object):
    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        if settings.ENVIRONMENT != "production":
            ctx["test_environment"] = True
        ctx["version"] = settings.VERSION
        if isinstance(self, ListView):
            # Convenience url for pagers; append the page parameter to this to get a full url with all search parameters
            params = self.request.GET.dict()
            if "page" in params:
                del params["page"]
            ctx["urlparams"] = "?" + urlencode(params) if len(params) else ""
        return ctx
