from django_filters import rest_framework as filters
from kas.models import TaxYear, Person, PersonTaxYear, PolicyTaxYear, PensionCompany
from kas.serializers import TaxYearSerializer, PersonSerializer, PolicyTaxYearSerializer, PersonTaxYearSerializer, PensionCompanySerializer
from rest_framework import routers, viewsets
from rest_framework.authentication import TokenAuthentication


class TaxYearFilter(filters.FilterSet):
    year = filters.NumberFilter(field_name="year")
    year_lt = filters.NumberFilter(field_name="year", lookup_expr='lt')


class TaxYearViewSet(viewsets.ModelViewSet):
    permission_classes = TokenAuthentication
    queryset = TaxYear.objects.all()
    serializer_class = TaxYearSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TaxYearFilter


class PersonFilter(filters.FilterSet):
    cpr = filters.NumberFilter(field_name="cpr")


class PersonViewSet(viewsets.ModelViewSet):
    permission_classes = TokenAuthentication
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PersonFilter


class PersonTaxYearFilter(filters.FilterSet):
    year = filters.NumberFilter(field_name="tax_year__year")
    year_lt = filters.NumberFilter(field_name="tax_year__year", lookup_expr='lt')
    cpr = filters.CharFilter(field_name="person__cpr")


class PersonTaxYearViewSet(viewsets.ModelViewSet):
    permission_classes = TokenAuthentication
    queryset = PersonTaxYear.objects.all()
    serializer_class = PersonTaxYearSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PersonTaxYearFilter


class PolicyTaxYearFilter(filters.FilterSet):
    year = filters.NumberFilter(field_name="person_tax_year__tax_year__year")
    year_lt = filters.NumberFilter(field_name="person_tax_year__tax_year__year", lookup_expr='lt')
    cpr = filters.CharFilter(field_name="person_tax_year__person__cpr")


class PolicyTaxYearViewSet(viewsets.ModelViewSet):
    permission_classes = TokenAuthentication
    queryset = PolicyTaxYear.objects.all()
    serializer_class = PolicyTaxYearSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PolicyTaxYearFilter


class PensionCompanyFilter(filters.FilterSet):
    cvr = filters.CharFilter(field_name="cvr")


class PensionCompanyViewSet(viewsets.ModelViewSet):
    permission_classes = TokenAuthentication
    queryset = PensionCompany.objects.all()
    serializer_class = PensionCompanySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PensionCompanyFilter


router = routers.DefaultRouter()
router.register(r'pension_company', PensionCompanyViewSet)
router.register(r'tax_year', TaxYearViewSet)
router.register(r'person', PersonViewSet)
router.register(r'person_tax_year', PersonTaxYearViewSet)
router.register(r'policy_tax_year', PolicyTaxYearViewSet)
