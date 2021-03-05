from django.conf.urls import url

from sullissivik.login.nemid import views

app_name = 'sullissivik.login.nemid'

urlpatterns = [
    url(r'^test', views.TestView.as_view(), name='test'),
    url(r'^login', views.Login.as_view(), name='login'),
]
