from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from jwkest.jwk import rsa_load
from oic.oic import Client, rndstr
from oic.oic.message import RegistrationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.utils.keyio import KeyBundle


class OpenId:

    open_id_settings = {}
    kc_rsa = None
    client_cert = None
    if getattr(settings, 'OPENID_CONNECT', None) and settings.OPENID_CONNECT.get('enabled', True):
        # if openID is enabled setup the key bundle and client_cert
        open_id_settings = settings.OPENID_CONNECT
        key = rsa_load(open_id_settings['private_key'])
        kc_rsa = KeyBundle([{'key': key, 'kty': 'RSA', 'use': 'ver'},
                            {'key': key, 'kty': 'RSA', 'use': 'sig'}])

        client_cert = (open_id_settings['client_certificate'], open_id_settings['private_key'])

    @staticmethod
    def enabled():
        return settings.OPENID_CONNECT.get('enabled', True)

    @staticmethod
    def authenticate(request):
        return None  # If the user has nothing in the session, we just don't log him in - there's no SSO cookie that we may want to check

    whitelist = [reverse_lazy('openid:login'), reverse_lazy('openid:callback'), reverse_lazy('openid:logout-callback')]

    @staticmethod
    def clear_session(session):
        for key in ['oid_state', 'oid_nonce', 'user_info', 'login_method', 'has_checked_cvr']:
            if key in session:
                del session[key]
        session.save()

    @classmethod
    def logout(cls, session):
        # See also doc here: https://github.com/IdentityServer/IdentityServer4/blob/master/docs/endpoints/endsession.rst
        client = Client(
            client_authn_method=CLIENT_AUTHN_METHOD,
            client_cert=OpenId.client_cert
        )
        client.store_registration_info(
            RegistrationResponse(**{
                'client_id': cls.open_id_settings['client_id'],
                'redirect_uris': [cls.open_id_settings['front_channel_logout_uri']],
                'post_logout_redirect_uris': [cls.open_id_settings['post_logout_redirect_uri']]
            })
        )
        request_args = {
            'scope': cls.open_id_settings['scope'],
            'client_id': cls.open_id_settings['client_id'],
            'redirect_uri': cls.open_id_settings['front_channel_logout_uri'],
            'id_token_hint': session.get('raw_id_token'),
            'post_logout_redirect_uri': cls.open_id_settings['post_logout_redirect_uri'],
            'state': rndstr(32),
        }
        auth_req = client.construct_EndSessionRequest(
            request_args=request_args,
            id_token=session['access_token_data']['id_token']
        )
        logout_url = auth_req.request(cls.open_id_settings['logout_uri'])
        OpenId.clear_session(session)
        return HttpResponseRedirect(logout_url)
