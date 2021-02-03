from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = [

]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
