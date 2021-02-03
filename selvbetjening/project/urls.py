from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('selvbetjening.urls', namespace='selvbetjening')),
    url(r'^user/', include('sullissivik.login.urls', namespace='sullissivik')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
