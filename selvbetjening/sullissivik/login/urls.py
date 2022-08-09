from django.conf.urls import url, include

app_name = "sullissivik.login"

urlpatterns = [
    url("oid/", include("sullissivik.login.openid.urls", namespace="openid")),
]
