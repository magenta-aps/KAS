from django.db.models import Q
from django_filters import CharFilter, FilterSet, ModelChoiceFilter

from kas.forms_mixin import BootstrapForm
from kas.models import Lock, TaxYear


class PensionCompanyFilterSet(FilterSet):
    search = CharFilter(method="search_name_and_res")
    agreement = CharFilter(method="agreement_present")

    def agreement_present(self, queryset, name, value):
        if value and value == "agreement":
            return queryset.filter(Q(agreement_present=True) | ~Q(agreement=""))
        elif value and value == "no_agreement":
            return queryset.filter(agreement_present=False).filter(agreement="")

    def search_name_and_res(self, queryset, name, value):
        if value:
            return queryset.filter(Q(name__icontains=value) | Q(res__icontains=value))

    class Meta:
        fields = []


class LockFilterSet(FilterSet):
    taxyear = ModelChoiceFilter(queryset=TaxYear.objects.all(), empty_label=None)

    class Meta:
        model = Lock
        fields = [
            "taxyear",
        ]
        form = BootstrapForm
