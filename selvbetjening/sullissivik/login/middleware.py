from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.http import urlencode, urlquote

from sullissivik.login.openid.openid import OpenId


class LoginManager:

    @property
    def enabled(self):
        return OpenId.enabled()

    white_listed_urls = []

    def __init__(self, get_response):
        self.get_response = get_response

    @property
    def white_listed_urls(self):
        return OpenId.whitelist + settings.LOGIN_REQUIREMENT_WHITELIST + [reverse('sullissivik:openid:login'),
                                                                          reverse('selvbetjening:status')]

    def __call__(self, request):
        if self.enabled:
            white_listed_urls = self.white_listed_urls
            # When any non-whitelisted page is loaded, check if we are authenticated
            if request.path not in white_listed_urls and request.path.rstrip('/') not in white_listed_urls:
                if 'user_info' not in request.session or not request.session['user_info']:
                    if not self.authenticate(request):  # The user might not have anything in his session, but he may have a cookie that can log him in anyway
                        backpage = urlquote(request.path)
                        if request.GET:
                            backpage += "?" + urlencode(request.GET, True)
                        return redirect(reverse_lazy(settings.LOGIN_UNAUTH_REDIRECT) + "?back=" + backpage)
                if 'CPR' not in request.session['user_info']:
                    # User info exists, but does not contain a CPR number (e.g. company login)
                    return redirect(reverse_lazy('sullissivik:openid:logout'))
        elif settings.DEFAULT_CPR is not None:
            # For dev environment, use dummy CPR
            if 'user_info' not in request.session:
                request.session['user_info'] = {}
            request.session['user_info']['CPR'] = settings.DEFAULT_CPR
        return self.get_response(request)

    @staticmethod
    def authenticate(request):
        user = OpenId.authenticate(request)
        return user is not None and user.is_authenticated

    @staticmethod
    def get_backpage(request):
        backpage = request.GET.get('back', request.session.get('backpage', reverse(settings.LOGIN_DEFAULT_REDIRECT)))
        return backpage
