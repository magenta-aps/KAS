from django.conf.urls import include
from django.urls import path
from django.views.generic import RedirectView, TemplateView
from django_mitid_auth.saml.views import AccessDeniedView

from selvbetjening.views import (  # isort: skip
    CustomJavaScriptCatalog,
    ErrorView,
    PolicyDetailPriorView,
    PolicyDetailView,
    PolicyFormView,
    RepresentationStartView,
    RepresentationStopView,
    SetLanguageView,
    ViewFinalSettlementView,
)

app_name = "selvbetjening"

urlpatterns = [
    path("", RedirectView.as_view(url="/policy/edit/")),
    path("policy/<int:year>/", PolicyDetailView.as_view(), name="policy-view"),
    path(
        "policy/prior/<int:year>/",
        PolicyDetailPriorView.as_view(),
        name="policy-prior-view",
    ),
    path("policy/edit/", PolicyFormView.as_view(), name="policy-edit"),
    path(
        "policy/submitted/",
        TemplateView.as_view(template_name="submitted.html"),
        name="policy-submitted",
    ),
    path(
        "policy/no_person_data/",
        ErrorView.as_view(template_name="not_found.html"),
        name="person-not-found",
    ),
    path(
        "language/<str:locale>/",
        CustomJavaScriptCatalog.as_view(domain="django", packages=["selvbetjening"]),
        name="javascript-language-catalog",
    ),
    path("language/", SetLanguageView.as_view(), name="set-language"),
    path(
        "policy/closed/",
        TemplateView.as_view(template_name="closed.html"),
        name="closed",
    ),
    path(
        "final_settlement/<int:year>/",
        ViewFinalSettlementView.as_view(),
        name="final-settlement",
    ),
    path(
        "represent-start/",
        RepresentationStartView.as_view(),
        name="representation-start",
    ),
    path(
        "represent-stop/", RepresentationStopView.as_view(), name="representation-stop"
    ),
    path("_ht/", include("watchman.urls")),
    path(
        "error/login-timeout/",
        AccessDeniedView.as_view(template_name="error/login_timeout.html"),
        name="login-timeout",
    ),
    path(
        "error/login-repeat/",
        AccessDeniedView.as_view(template_name="error/login_repeat.html"),
        name="login-repeat",
    ),
    path(
        "error/login-nocpr/",
        AccessDeniedView.as_view(template_name="error/login_no_cpr.html"),
        name="login-no-cpr",
    ),
    path(
        "error/login_assurance/",
        AccessDeniedView.as_view(template_name="error/login_assurance.html"),
        name="login-assurance-level",
    ),
]
