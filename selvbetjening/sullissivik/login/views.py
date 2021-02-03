from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlquote
from django.views import View
from django.views.generic import TemplateView
from sullissivik.login.nemid.nemid import NemId
from sullissivik.login.openid.openid import OpenId


class LoginView(TemplateView):
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        if settings.OPENID_CONNECT['enabled']:
            url = reverse('sullissivik:openid:login')
            if 'back' in self.request.GET:
                url += "?back=" + urlquote(self.request.GET['back'])
            return redirect(url)
        return redirect(reverse(settings.LOGIN_DEFAULT_REDIRECT))


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        method = request.session.get('login_method')
        if method == 'openid':
            return OpenId.logout(self.request.session)
        else:
            return NemId.logout(self.request.session)
