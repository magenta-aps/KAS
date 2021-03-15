from django.db.models import Count
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView
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
            by_year_data['imported_mandtal'][x['skatteaar']] =  x['count']

        for x in ImportedR75PrivatePension.objects.values("tax_year").annotate(count=Count('tax_year')):
            by_year_data['imported_r75'][x['tax_year']] =  x['count']

        for x in PersonTaxYear.objects.values("tax_year__year").annotate(count=Count('tax_year__year')):
            by_year_data['persons'][x['tax_year__year']] =  x['count']

        for x in PolicyTaxYear.objects.values(
            "person_tax_year__tax_year__year"
        ).annotate(count=Count('person_tax_year__tax_year__year')):
            by_year_data['policies'][x['person_tax_year__tax_year__year']] = x['count']

        if settings.ENVIRONMENT != "production":
            result["show_mockup"] = True

            by_year_data['mockup_mandtal'] = {}
            by_year_data['mockup_r75'] = {}

            for x in MockModels.MockKasMandtal.objects.values("skatteaar").annotate(count=Count('skatteaar')):
                by_year_data['mockup_mandtal'][x['skatteaar']] =  x['count']

            for x in MockModels.MockR75PrivatePension.objects.values("tax_year").annotate(count=Count('tax_year')):
                by_year_data['mockup_r75'][x['tax_year']] =  x['count']

        for k, v in by_year_data.items():
            result[k] = [v.get(year, 0) for year in result['years']]

        return result
