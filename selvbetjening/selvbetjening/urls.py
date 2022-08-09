from django.conf.urls import url, include
from django.urls import path
from django.views.generic import RedirectView, TemplateView
from selvbetjening.views import CustomJavaScriptCatalog, SetLanguageView
from selvbetjening.views import PolicyFormView, PolicyDetailView, PolicyDetailPriorView
from selvbetjening.views import ViewFinalSettlementView
from selvbetjening.views import RepresentationStartView, RepresentationStopView

app_name = "selvbetjening"

urlpatterns = [
    url(r"^$", RedirectView.as_view(url="/policy/edit/")),
    url(r"^policy/(?P<year>[0-9]{4})$", PolicyDetailView.as_view(), name="policy-view"),
    url(
        r"^policy/prior/(?P<year>[0-9]{4})/?",
        PolicyDetailPriorView.as_view(),
        name="policy-prior-view",
    ),
    url(r"^policy/edit/?", PolicyFormView.as_view(), name="policy-edit"),
    url(
        r"^policy/submitted/?",
        TemplateView.as_view(template_name="submitted.html"),
        name="policy-submitted",
    ),
    url(
        r"^policy/no_person_data/?",
        TemplateView.as_view(template_name="not_found.html"),
        name="person-not-found",
    ),
    url(
        r"^language/(?P<locale>[a-z]{2})",
        CustomJavaScriptCatalog.as_view(domain="django", packages=["selvbetjening"]),
        name="javascript-language-catalog",
    ),
    url(r"^language", SetLanguageView.as_view(), name="set-language"),
    url(
        r"^policy/closed/",
        TemplateView.as_view(template_name="closed.html"),
        name="closed",
    ),
    path(
        "final_settlement/<int:year>/",
        ViewFinalSettlementView.as_view(),
        name="final-settlement",
    ),
    path(
        "represent-start",
        RepresentationStartView.as_view(),
        name="representation-start",
    ),
    path(
        "represent-stop", RepresentationStopView.as_view(), name="representation-stop"
    ),
    path("_ht/", include("watchman.urls")),
]
