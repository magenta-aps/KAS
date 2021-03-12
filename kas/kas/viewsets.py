from django_filters import rest_framework as filters
from kas.models import PensionCompany, Person, PersonTaxYear, PolicyDocument, PolicyTaxYear, TaxYear
from kas.serializers import PensionCompanySerializer, PersonSerializer, PersonTaxYearSerializer, PolicyDocumentSerializer, PolicyTaxYearSerializer, TaxYearSerializer
from rest_framework import routers, viewsets
from rest_framework.parsers import MultiPartParser, FormParser


class TaxYearFilter(filters.FilterSet):
    year = filters.NumberFilter(field_name="year")
    year_lt = filters.NumberFilter(field_name="year", lookup_expr='lt')


class TaxYearViewSet(viewsets.ModelViewSet):
    queryset = TaxYear.objects.all()
    serializer_class = TaxYearSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TaxYearFilter


class PersonFilter(filters.FilterSet):
    cpr = filters.NumberFilter(field_name="cpr")


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PersonFilter


class PersonTaxYearFilter(filters.FilterSet):
    year = filters.NumberFilter(field_name="tax_year__year")
    year_lt = filters.NumberFilter(field_name="tax_year__year", lookup_expr='lt')
    cpr = filters.CharFilter(field_name="person__cpr")


class PersonTaxYearViewSet(viewsets.ModelViewSet):
    queryset = PersonTaxYear.objects.all()
    serializer_class = PersonTaxYearSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PersonTaxYearFilter


class PolicyTaxYearFilter(filters.FilterSet):
    year = filters.NumberFilter(field_name="person_tax_year__tax_year__year")
    year_lt = filters.NumberFilter(field_name="person_tax_year__tax_year__year", lookup_expr='lt')
    cpr = filters.CharFilter(field_name="person_tax_year__person__cpr")
    person_tax_year = filters.ModelChoiceFilter(queryset=PersonTaxYear.objects.all())
    pension_company = filters.ModelChoiceFilter(queryset=PensionCompany.objects.all())


class PolicyTaxYearViewSet(viewsets.ModelViewSet):
    queryset = PolicyTaxYear.objects.all()
    serializer_class = PolicyTaxYearSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PolicyTaxYearFilter


class PensionCompanyFilter(filters.FilterSet):
    res = filters.CharFilter(field_name="res")


class PensionCompanyViewSet(viewsets.ModelViewSet):
    queryset = PensionCompany.objects.all()
    serializer_class = PensionCompanySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PensionCompanyFilter


class PolicyDocumentFilter(filters.FilterSet):
    policy_tax_year = filters.ModelChoiceFilter(queryset=PolicyTaxYear.objects.all())


class PolicyDocumentViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser]
    queryset = PolicyDocument.objects.all()
    serializer_class = PolicyDocumentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PolicyDocumentFilter


router = routers.DefaultRouter()
router.register(r'pension_company', PensionCompanyViewSet)
router.register(r'tax_year', TaxYearViewSet)
router.register(r'person', PersonViewSet)
router.register(r'person_tax_year', PersonTaxYearViewSet)
router.register(r'policy_tax_year', PolicyTaxYearViewSet)
router.register(r'policy_document', PolicyDocumentViewSet)
