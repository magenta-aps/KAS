from django.db.models import Count
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView, DetailView, ListView, View
from django.views.generic.detail import SingleObjectMixin
from eskat.models import ImportedKasMandtal, ImportedR75PrivatePension, MockModels
from kas.forms import PersonListFilterForm
from kas.models import TaxYear, PersonTaxYear, PolicyTaxYear, TaxSlipGenerated

import os


class FrontpageView(LoginRequiredMixin, TemplateView):
    template_name = 'kas/frontpage.html'

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)

        result['years'] = [x.year for x in TaxYear.objects.order_by('year')]

        by_year_data = {
            'imported_mandtal': {},
            'imported_r75': {},
            'persons': {},
            'policies': {},
        }

        for x in ImportedKasMandtal.objects.values("skatteaar").annotate(number_per_year=Count('skatteaar')):
            by_year_data['imported_mandtal'][x['skatteaar']] = x['number_per_year']

        for x in ImportedR75PrivatePension.objects.values("tax_year").annotate(number_per_year=Count('tax_year')):
            by_year_data['imported_r75'][x['tax_year']] = x['number_per_year']

        for x in PersonTaxYear.objects.values("tax_year__year").annotate(number_per_year=Count('tax_year__year')):
            by_year_data['persons'][x['tax_year__year']] = x['number_per_year']

        for x in PolicyTaxYear.objects.values(
            "person_tax_year__tax_year__year"
        ).annotate(number_per_year=Count('person_tax_year__tax_year__year')):
            by_year_data['policies'][x['person_tax_year__tax_year__year']] = x['number_per_year']

        if settings.ENVIRONMENT != "production":
            result["show_mockup"] = True

            by_year_data['mockup_mandtal'] = {}
            by_year_data['mockup_r75'] = {}

            for x in MockModels.MockKasMandtal.objects.values("skatteaar").annotate(number_per_year=Count('skatteaar')):
                by_year_data['mockup_mandtal'][x['skatteaar']] = x['number_per_year']

            for x in MockModels.MockR75Idx4500230.objects.values("tax_year").annotate(number_per_year=Count('tax_year')):
                by_year_data['mockup_r75'][x['tax_year']] = x['number_per_year']

        for k, v in by_year_data.items():
            result[k] = [v.get(year, 0) for year in result['years']]

        return result


class PersonTaxYearListView(LoginRequiredMixin, ListView):
    template_name = 'kas/persontaxyear_list.html'
    context_object_name = 'personstaxyears'
    paginate_by = 20

    model = PersonTaxYear

    def get_queryset(self):
        qs = super().get_queryset()

        self.year = self.kwargs.get("year", None)

        if not self.year:
            raise Http404("No year specified")

        filters = {'tax_year__year': self.year}

        form = PersonListFilterForm(self.request.GET)

        if form.is_valid():
            if form.cleaned_data['cpr']:
                filters['person__cpr__contains'] = form.cleaned_data['cpr']
            if form.cleaned_data['name']:
                filters['person__name__contains'] = form.cleaned_data['name']

        self.form = form
        qs = qs.filter(**filters)

        return qs


class PersonTaxYearDetailView(LoginRequiredMixin, DetailView):
    template_name = 'kas/persontaxyear_detail.html'
    model = PersonTaxYear
    context_object_name = 'person_tax_year'

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
            obj = queryset.get(
                tax_year__year=self.year,
                person=self.person_id
            )
        except queryset.model.DoesNotExist:
            raise Http404("Persontaxyear not found")

        return obj

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)

        obj = self.get_object()

        result['joined_address'] = "\n".join([x or "" for x in (
            obj.person.address_line_1,
            obj.person.address_line_2,
            obj.person.address_line_3,
            obj.person.address_line_4,
            obj.person.address_line_5,
        )])

        return result


class PolicyTaxYearDetailView(LoginRequiredMixin, DetailView):
    template_name = 'kas/policytaxyear_detail.html'
    model = PolicyTaxYear
    context_object_name = 'policy'

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)

        policy = self.get_object()

        result['calculation'] = policy.get_calculation()

        amount_choices_by_value = {x[0]: x[1] for x in PolicyTaxYear.active_amount_options}

        result['pension_company_amount_label'] = amount_choices_by_value[PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED]
        result['estimated_amount_label'] = amount_choices_by_value[PolicyTaxYear.ACTIVE_AMOUNT_ESTIMATED]
        result['self_reported_amount_label'] = amount_choices_by_value[PolicyTaxYear.ACTIVE_AMOUNT_SELF_REPORTED]

        result['used_negativ_table'] = policy.previous_year_deduction_table_data

        return result


class PdfDownloadView(LoginRequiredMixin, SingleObjectMixin, View):
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
                persontaxyear__tax_year__year=year,
                persontaxyear__person=person_id
            )
        except queryset.model.DoesNotExist:
            raise Http404("PDF not found")

        return obj

    def get(self, *args, **kwargs):

        obj = self.get_object()
        filefield = obj.file
        file_obj = filefield.file

        response = HttpResponse(
            file_obj.read(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(obj.file.file.name)

        return response
