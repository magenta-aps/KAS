from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, reverse_lazy
from project.admin import kasadmin

from kas.viewsets import router

urlpatterns = [
    path("admin/", kasadmin.urls),
    path("django-admin/", admin.site.urls),
    path(
        "accounts/logout/",
        LogoutView.as_view(next_page=reverse_lazy("kas:login")),
        name="logout",
    ),
    path("worker/", include("worker.urls", namespace="worker")),
    path("rest/", include(router.urls)),
    path("", include("kas.urls", namespace="kas")),
    path("prisme/", include("prisme.urls", namespace="prisme")),
    path("_ht/", include("watchman.urls")),
    path("metrics/", include("metrics.urls")),
]


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
