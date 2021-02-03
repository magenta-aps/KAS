from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('worker/', include('worker.urls', namespace='worker'))
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
