from django.urls import path
from sullissivik.login.openid.views import (
    LoginView,
    LoginCallback,
    LogoutView,
    LogoutCallback,
)

app_name = "sullissivik.login.openid"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path(
        "login/callback/", LoginCallback.as_view(), name="login-callback"
    ),  # RedirectUris
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "logout/callback/", LogoutCallback.as_view(), name="logout-callback"
    ),  # FrontChannelLogoutUri
]
