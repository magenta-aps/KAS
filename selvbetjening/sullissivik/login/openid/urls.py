from django.conf.urls import url
from sullissivik.login.openid.views import Login, LoginCallback, LogoutCallback

app_name = 'sullissivik.login.openid'

urlpatterns = [
    url(r'^callback/$', LoginCallback.as_view(), name='callback'),
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^logout/$', LogoutCallback.as_view(), name='logout-callback'),
]
