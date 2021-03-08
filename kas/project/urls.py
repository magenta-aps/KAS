from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

from kas.viewsets import router

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='kas/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login/'), name='logout'),

    path('worker/', include('worker.urls', namespace='worker')),
    path('rest/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
