from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = [
    url(r'', include('selvbetjening.urls', namespace='selvbetjening')),
    url(r'^user/', include('sullissivik.login.urls', namespace='sullissivik')),
    url('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
