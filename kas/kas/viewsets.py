from datetime import timedelta

import requests
from django.conf import settings
from django.db.models import Prefetch
from django.http import FileResponse, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import Http404, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters import rest_framework as filters
from project.renders import PdfProxyRender
from rest_framework import routers, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView

from kas.models import (  # isort: skip
    FinalSettlement,
    PensionCompany,
    Person,
    PersonTaxYear,
    PolicyDocument,
    PolicyTaxYear,
    RepresentationToken,
    TaxYear,
)
from kas.serializers import (  # isort: skip
    PensionCompanySerializer,
    PersonSerializer,
    PersonTaxYearSerializer,
    PolicyDocumentSerializer,
    PolicyTaxYearSerializer,
    TaxYearSerializer,
)


class TaxYearFilter(filters.FilterSet):
    year = filters.NumberFilter(field_name="year")
    year_lt = filters.NumberFilter(field_name="year", lookup_expr="lt")


class TaxYearViewSet(viewsets.ModelViewSet):
    queryset = TaxYear.objects.all()
    serializer_class = TaxYearSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TaxYearFilter


class PersonFilter(filters.FilterSet):
    cpr = filters.CharFilter(field_name="cpr")


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PersonFilter


class PersonTaxYearFilter(filters.FilterSet):
    year = filters.NumberFilter(field_name="tax_year__year")
    year_lt = filters.NumberFilter(field_name="tax_year__year", lookup_expr="lt")
    cpr = filters.CharFilter(field_name="person__cpr")


class PersonTaxYearViewSet(viewsets.ModelViewSet):
    queryset = PersonTaxYear.objects.all()
    serializer_class = PersonTaxYearSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PersonTaxYearFilter


class PolicyTaxYearFilter(filters.FilterSet):
    year = filters.NumberFilter(field_name="person_tax_year__tax_year__year")
    year_lt = filters.NumberFilter(
        field_name="person_tax_year__tax_year__year", lookup_expr="lt"
    )
    cpr = filters.CharFilter(field_name="person_tax_year__person__cpr")
    active = filters.BooleanFilter(field_name="active")
    person_tax_year = filters.ModelChoiceFilter(queryset=PersonTaxYear.objects.all())
    pension_company = filters.ModelChoiceFilter(queryset=PensionCompany.objects.all())


class PolicyTaxYearViewSet(viewsets.ModelViewSet):
    queryset = PolicyTaxYear.objects.all().prefetch_related(
        Prefetch(
            lookup="policy_documents",
            to_attr="documents",
            queryset=PolicyDocument.objects.filter(uploaded_by__isnull=True),
        )
    )
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
router.register(r"pension_company", PensionCompanyViewSet)
router.register(r"tax_year", TaxYearViewSet)
router.register(r"person", PersonViewSet)
router.register(r"person_tax_year", PersonTaxYearViewSet)
router.register(r"policy_tax_year", PolicyTaxYearViewSet)
router.register(r"policy_document", PolicyDocumentViewSet)


class CurrentFinalSettlementExistsView(APIView):
    def get_object(self):
        try:
            return FinalSettlement.objects.filter(
                person_tax_year__person__cpr=self.kwargs["cpr"],
                person_tax_year__tax_year__year=self.kwargs["year"],
                status="send",
            ).order_by("-send_at")[0]
        except IndexError:
            return None

    def get_remote_href(self):
        # Når vi får info om urls for slutopgørelser fra Skattestyrelsen skal
        # denne genbesøges
        # TODO: use correct url
        return None

    def get_remote_exist(self):
        url = self.get_remote_href()
        if url:
            response = requests.head(self.get_remote_href(), allow_redirects=True)
            return response.status_code == 200
        else:
            return False

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            # try to see if it exists remotely
            if self.get_remote_exist():
                return HttpResponse("remote")
        else:
            try:
                if instance.pdf.size > 0:
                    return HttpResponse("local")
            except FileNotFoundError:
                pass
        raise Http404()


class CurrentFinalSettlementDownloadView(CurrentFinalSettlementExistsView):
    renderer_classes = [
        PdfProxyRender,
    ]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            if self.get_remote_exist():
                return redirect(self.get_remote_href())
            else:
                raise Http404()
        return FileResponse(
            instance.pdf,
            as_attachment=False,
            content_type="application/pdf",
            filename="{year}_{cpr}.pdf".format(
                year=instance.person_tax_year.tax_year.year,
                cpr=instance.person_tax_year.person.cpr,
            ),
        )


@method_decorator(csrf_exempt, name="dispatch")
class TokenValidationView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            tokenstring = request.POST["token"]
            token = RepresentationToken.objects.get(token=tokenstring)
        except KeyError:
            return HttpResponseBadRequest("Token not set")
        except RepresentationToken.DoesNotExist:
            return HttpResponseBadRequest("Invalid token")
        if token.created < timezone.now() - timedelta(
            seconds=settings.SELVBETJENING_REPRESENTATION_TOKEN_MAX_AGE
        ):
            return HttpResponseBadRequest("Token expired")
        if token.consumed:
            return HttpResponseBadRequest("Token already used")
        if RepresentationToken.objects.filter(user=token.user, consumed=True).exists():
            return HttpResponseBadRequest("User already is using another token")

        token.consumed = True
        token.save()
        return JsonResponse(
            {
                "CPR": token.person.cpr,
                "PersonName": token.person.name,
                "AdminUsername": token.user.username,
                "AdminUserID": token.user.id,
            }
        )
