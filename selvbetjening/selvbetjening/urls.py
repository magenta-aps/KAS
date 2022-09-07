from django.conf.urls import include
from django.urls import path
from django.views.generic import RedirectView, TemplateView
from selvbetjening.views import CustomJavaScriptCatalog, SetLanguageView
from selvbetjening.views import PolicyFormView, PolicyDetailView, PolicyDetailPriorView
from selvbetjening.views import RepresentationStartView, RepresentationStopView
from selvbetjening.views import ViewFinalSettlementView

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
        TemplateView.as_view(template_name="not_found.html"),
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
]
