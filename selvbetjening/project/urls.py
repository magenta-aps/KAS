from django.conf import settings
from django.conf.urls import include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

urlpatterns = [
    path("", include("selvbetjening.urls", namespace="selvbetjening")),
    path("user/", include("sullissivik.login.urls", namespace="sullissivik")),
    path("i18n/", include("django.conf.urls.i18n")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
