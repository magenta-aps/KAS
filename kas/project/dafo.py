from requests import Session
from django.conf import settings


class DatafordelerClient(object):
    combined_service_page_size = 400

    def __init__(self, mock=None, client_header=None,
                 service_header_cpr=None, uxp_service_owned_by=None,
                 certificate=None, private_key=None, url=None, root_ca=True, timeout=60, mock_data=None):

        self.mock_data = mock_data
        self.mock = mock
        self.client_header = client_header
        self.service_header_cpr = service_header_cpr
        self.uxp_service_owned_by = uxp_service_owned_by
        self.cert = (certificate, private_key)
        self.root_ca = root_ca
        self.url = url
        self.timeout = timeout
        self.session = Session()
        self.session.cert = self.cert
        self.session.verify = self.root_ca
        self.session.headers.update({'Uxp-Client': client_header})

    def __del__(self):
        if hasattr(self, '_session'):
            self.session.close()

    @classmethod
    def from_settings(cls):
        return cls(**settings.DAFO)

    def set_mock_data(self, mock_data):
        self.mock_data = mock_data

    def get_person_information(self, cpr):
        """
        Lookup address information for cpr
        """
        if self.mock:
            return self.mock_data
        else:
            return self._get(cpr, self.service_header_cpr)

    def _get(self, params, service_header):
        r = self.session.get(self.url, params=params, timeout=self.timeout,
                             headers={'Uxp-Service': service_header})
        r.raise_for_status()
        return r.json()

    def close(self):
        self.session.close()
