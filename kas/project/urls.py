from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include, reverse_lazy
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from project.admin import kasadmin
from kas.viewsets import router

urlpatterns = [
    path('admin/', kasadmin.urls),
    path('django-admin/', admin.site.urls),
    path('accounts/login/', LoginView.as_view(template_name='kas/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),

    path('worker/', include('worker.urls', namespace='worker')),
    path('rest/', include(router.urls)),
    path('', include('kas.urls', namespace='kas')),
    path('prisme/', include('prisme.urls', namespace='prisme')),

    path('_ht/', include('watchman.urls')),
]


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
