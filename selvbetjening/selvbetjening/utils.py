from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django_mitid_auth.middleware import LoginManager


def session_timed_out(request):
    # What to do when session has timed out
    # See https://github.com/Lapeth/django-session-timeout
    whitelist = LoginManager.get_whitelisted_urls()
    if request.path in whitelist:
        return None
    redirect_url = getattr(settings, "SESSION_TIMEOUT_REDIRECT", None)
    if redirect_url:
        return redirect(redirect_url)
    else:
        return redirect_to_login(next=request.path)
