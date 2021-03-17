from django.db.models import Count
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import TemplateView, DetailView, ListView
from eskat.models import ImportedKasMandtal, ImportedR75PrivatePension, MockModels
from kas.models import TaxYear, PersonTaxYear, PolicyTaxYear


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

        for x in ImportedKasMandtal.objects.values("skatteaar").annotate(count=Count('skatteaar')):
            by_year_data['imported_mandtal'][x['skatteaar']] = x['count']

        for x in ImportedR75PrivatePension.objects.values("tax_year").annotate(count=Count('tax_year')):
            by_year_data['imported_r75'][x['tax_year']] = x['count']

        for x in PersonTaxYear.objects.values("tax_year__year").annotate(count=Count('tax_year__year')):
            by_year_data['persons'][x['tax_year__year']] = x['count']

        for x in PolicyTaxYear.objects.values(
            "person_tax_year__tax_year__year"
        ).annotate(count=Count('person_tax_year__tax_year__year')):
            by_year_data['policies'][x['person_tax_year__tax_year__year']] = x['count']

        if settings.ENVIRONMENT != "production":
            result["show_mockup"] = True

            by_year_data['mockup_mandtal'] = {}
            by_year_data['mockup_r75'] = {}

            for x in MockModels.MockKasMandtal.objects.values("skatteaar").annotate(count=Count('skatteaar')):
                by_year_data['mockup_mandtal'][x['skatteaar']] = x['count']

            for x in MockModels.MockR75PrivatePension.objects.values("tax_year").annotate(count=Count('tax_year')):
                by_year_data['mockup_r75'][x['tax_year']] = x['count']

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

        qs = qs.filter(tax_year__year=self.year)

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


class PolicyTaxYearDetailView(LoginRequiredMixin, DetailView):
    template_name = 'kas/policytaxyear_detail.html'
    model = PolicyTaxYear
    context_object_name = 'policy'

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)

        policy = self.get_object()

        result['calculation'] = policy.get_calculation()

        amount_choices_by_value = {x[0]: x[1] for x in PolicyTaxYear.active_amount_options}
        print(amount_choices_by_value)

        result['pension_company_amount_label'] = amount_choices_by_value[PolicyTaxYear.ACTIVE_AMOUNT_PREFILLED]
        result['estimated_amount_label'] = amount_choices_by_value[PolicyTaxYear.ACTIVE_AMOUNT_ESTIMATED]
        result['self_reported_amount_label'] = amount_choices_by_value[PolicyTaxYear.ACTIVE_AMOUNT_SELF_REPORTED]

        result['used_negativ_table'] = policy.previous_year_deduction_table_data

        return result
