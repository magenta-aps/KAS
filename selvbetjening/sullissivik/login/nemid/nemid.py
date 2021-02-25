import sys
import traceback

import requests
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy
from requests import Session
from sullissivik.login.nemid.models import SessionOnlyUser
from zeep import Client
from zeep import Transport
from zeep.helpers import serialize_object


class NemId:

    @staticmethod
    def enabled():
        return settings.NEMID_CONNECT.get("enabled")

    @staticmethod
    def authenticate(request):
        user = SessionOnlyUser.get_user(request.session)
        if not user.is_authenticated:
            try:
                config = settings.NEMID_CONNECT
                token = request.COOKIES.get(config.get('cookie_name'))
                if token:
                    response = requests.post(
                        config['get_user_service'],
                        data={'token': token},
                        cert=(
                            config['client_certificate'],
                            config['private_key'],
                        )
                    )
                    if response.status_code == 200:
                        response_object = response.json()
                        user = request.user = SessionOnlyUser.get_user(
                            request.session,
                            response_object['CPR'],
                            response_object['Name']
                        )
                        if user.is_authenticated:
                            request.session['user_info'] = user.dict()
            except Exception:
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
        return user

    @staticmethod
    def authenticate_soap(request):
        user = SessionOnlyUser.get_user(request.session)
        if not user.is_authenticated:
            try:
                config = settings.NEMID_CONNECT
                cookie = request.COOKIES.get(config.get('cookie_name'))
                if cookie is not None:

                    session = Session()
                    session.cert = (
                        config['client_certificate'],
                        config['private_key']
                    )

                    client = Client(
                        config.get('federation_service'),
                        transport=Transport(
                            session=session
                        ),
                        # plugins=[HistoryPlugin()],
                        # wsse=Signature(
                        #     config['private_key'],
                        #     config['client_certificate']
                        # ),
                    )
                    # Convert zeep object to OrderedDict
                    user_data = serialize_object(client.service.GetUser(cookie))
                    # federationPid = user_data.get('FederationPid')
                    cpr = user_data.get('CPR')
                    name = user_data.get('Name')
                    is_authenticated = user_data.get('IsAuthenticated')
                    if is_authenticated is not True:
                        return None
                    if cpr is None:
                        return None
                    user = request.user = SessionOnlyUser.get_user(request.session, cpr, name)
                    if request.user.is_authenticated:
                        request.session['user_info'] = user.dict()
            except Exception as e:
                print(e)
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                raise e
        return user

    whitelist = [reverse_lazy('nemid:login')]

    @staticmethod
    def clear_session(session):
        for key in ['user_info', 'login_method', 'user', 'has_checked_cvr']:
            if key in session:
                del session[key]
        session.save()

    @staticmethod
    def logout(session):
        NemId.clear_session(session)
        response = redirect(settings.LOGOUT_REDIRECT)
        if settings.NEMID_CONNECT['enabled']:
            response.delete_cookie(
                settings.NEMID_CONNECT['cookie_name'],
                path=settings.NEMID_CONNECT['cookie_path'],
                domain=settings.NEMID_CONNECT['cookie_domain']
            )
        return response
