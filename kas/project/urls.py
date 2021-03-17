from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

from kas.viewsets import router

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('accounts/login/', LoginView.as_view(template_name='kas/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='login/'), name='logout'),

    path('worker/', include('worker.urls', namespace='worker')),
    path('rest/', include(router.urls)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
