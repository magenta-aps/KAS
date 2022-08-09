from django.conf.urls import url
from sullissivik.login.openid.views import (
    LoginView,
    LoginCallback,
    LogoutView,
    LogoutCallback,
)

app_name = "sullissivik.login.openid"

urlpatterns = [
    # url(r'^login/$', LoginView.as_view(), name='login'),
    # url(r'^callback/$', LoginCallback.as_view(), name='login-callback'),  # RedirectUris
    # url(r'^logout-manual/$', LogoutView.as_view(), name='logout'),
    # url(r'^logout/$', LogoutCallback.as_view(), name='logout-callback'),  # FrontChannelLogoutUri
    url(r"^login/$", LoginView.as_view(), name="login"),
    url(
        r"^login/callback/$", LoginCallback.as_view(), name="login-callback"
    ),  # RedirectUris
    url(r"^logout/$", LogoutView.as_view(), name="logout"),
    url(
        r"^logout/callback/$", LogoutCallback.as_view(), name="logout-callback"
    ),  # FrontChannelLogoutUri
]
