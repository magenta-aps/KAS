from django.conf import settings
from django.conf.urls import include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

urlpatterns = [
    path("", include("selvbetjening.urls", namespace="selvbetjening")),
    path("", include("django_mitid_auth.urls", namespace="login")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("metrics/", include("metrics.urls")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

if settings.MITID_TEST_ENABLED:
    urlpatterns.append(
        path("mitid_test/", include("mitid_test.urls", namespace="mitid_test"))
    )
