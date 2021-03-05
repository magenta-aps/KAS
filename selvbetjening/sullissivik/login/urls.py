from django.conf.urls import url, include

from sullissivik.login.views import LoginView
from sullissivik.login.views import LogoutView

app_name = 'sullissivik.login'

urlpatterns = [
    url('oid/', include('sullissivik.login.openid.urls', namespace='openid')),
    url('nemid/', include('sullissivik.login.nemid.urls', namespace='nemid')),
    url('login/?$', LoginView.as_view(), name='login'),
    url('logout/?$', LogoutView.as_view(), name='logout')
]
