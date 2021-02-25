from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

from kas.viewsets import router
from kas.views import PolicyDocumentUpload

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('worker/', include('worker.urls', namespace='worker')),
    path("rest/policy_document/", PolicyDocumentUpload.as_view(), name="rest_document_upload"),
    path('rest/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
