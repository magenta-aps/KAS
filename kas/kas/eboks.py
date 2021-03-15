import requests
import urllib
import urllib.parse
from uuid import uuid4
from lxml import etree
from django.conf import settings


class EboksDispatchGenerator(object):

    def __init__(self, content_type_id, title):
        self._content_type_id = str(content_type_id)
        self._title = title

    def generate_dispatch(self, number, pdf_data):
        root = etree.Element("Dispatch", xmlns='urn:eboks:en:3.0.0')

        recipient = etree.Element('DispatchRecipient')
        recipient_id = etree.Element('Id')
        recipient_id.text = number
        recipient.append(recipient_id)
        r_type = etree.Element('Type')
        r_type.text = 'P'
        recipient.append(r_type)
        nationality = etree.Element('Nationality')
        nationality.text = 'DK'
        recipient.append(nationality)
        root.append(recipient)

        content_type = etree.Element('ContentTypeId')
        content_type.text = self._content_type_id
        root.append(content_type)

        title = etree.Element('Title')
        title.text = self._title
        root.append(title)

        content = etree.Element('Content')
        data = etree.Element('Data')
        data.text = pdf_data
        content.append(data)
        file_extension = etree.Element('FileExtension')
        file_extension.text = 'pdf'
        content.append(file_extension)
        root.append(content)

        return etree.tostring(root, xml_declaration=True, encoding='UTF-8')

    @classmethod
    def from_settings(cls, title):
        return cls(content_type_id=settings.EBOKS['content_type_id'], title=title)


class EboksClient(object):
    def __init__(self, client_certificate, client_private_key, verify, client_id, system_id, host, timeout=60):
        self._client_id = client_id
        self._system_id = str(system_id)
        self._host = host
        self.timeout = timeout
        self._session = requests.session()
        self._session.cert = (client_certificate, client_private_key)
        self._verify = verify
        self._session.verify = verify
        self._session.headers.update({'content-type': 'application/xml'})
        self._url_with_prefix = urllib.parse.urljoin(self._host, '/int/rest/srv.svc/')

    def _make_request(self, url, method='GET', params=None, data=None):
        r = self._session.request(method, url, params, data, timeout=self.timeout)
        r.raise_for_status()
        return r

    def get_client_info(self):
        url = urllib.parse.urljoin(self._host, '/rest/client/{client_id}/'.format(client_id=self._client_id))
        return self._make_request(url=url)

    def get_recipient_status(self, message_ids):
        url = urllib.parse.urljoin(self._host, '/rest/messages/{client_id}/'.format(client_id=self._client_id))
        return self._make_request(url=url, params={'message_id': message_ids})

    def get_message_id(self):
        return '{sys_id}{client_id}{uuid}'.format(sys_id=self._system_id.zfill(6), client_id=self._client_id, uuid=uuid4().hex)

    def send_message(self, message, message_id):
        url = urllib.parse.urljoin(self._url_with_prefix, '3/dispatchsystem/{sys_id}/dispatches/{message_id}'.format(sys_id=self._system_id, message_id=message_id))
        return self._make_request(url=url, method='PUT', data=message)

    def close(self):
        self._session.close()

    @classmethod
    def from_settings(cls):
        eboks_settings = dict(settings.EBOKS)
        eboks_settings.pop('content_type_id')
        eboks_settings.pop('dispatch_bulk_size')
        return cls(**eboks_settings)
