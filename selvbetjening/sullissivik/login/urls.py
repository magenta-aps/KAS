from django.conf.urls import include
from django.urls import path

app_name = "sullissivik.login"

urlpatterns = [
    path("oid/", include("sullissivik.login.openid.urls", namespace="openid")),
]
