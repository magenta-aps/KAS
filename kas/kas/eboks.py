import urllib
import urllib.parse
from dataclasses import dataclass
from time import sleep
from uuid import uuid4

import requests
from django.conf import settings
from lxml import etree
from requests.exceptions import HTTPError


class EboksDispatchGenerator(object):
    def __init__(self, content_type_id):
        self._content_type_id = str(content_type_id)

    def generate_dispatch(self, title, number, pdf_data):
        root = etree.Element("Dispatch", xmlns="urn:eboks:en:3.0.0")

        recipient = etree.Element("DispatchRecipient")
        recipient_id = etree.Element("Id")
        recipient_id.text = number
        recipient.append(recipient_id)
        r_type = etree.Element("Type")
        r_type.text = "P"
        recipient.append(r_type)
        nationality = etree.Element("Nationality")
        nationality.text = "DK"
        recipient.append(nationality)
        root.append(recipient)

        content_type = etree.Element("ContentTypeId")
        content_type.text = self._content_type_id
        root.append(content_type)

        title_element = etree.Element("Title")
        title_element.text = title
        root.append(title_element)

        content = etree.Element("Content")
        data = etree.Element("Data")
        data.text = pdf_data
        content.append(data)
        file_extension = etree.Element("FileExtension")
        file_extension.text = "pdf"
        content.append(file_extension)
        root.append(content)

        return etree.tostring(root, xml_declaration=True, encoding="UTF-8")

    @classmethod
    def from_settings(cls):
        return cls(content_type_id=settings.EBOKS["content_type_id"])


@dataclass()
class MockResponse:
    status_code: int = 200

    def __init__(self, message_id):
        self._message_id = message_id

    def json(self):
        """
        This mocks a response for a valid GL citizen.
        Please note that normally the nr field would be the CPR number of the citizen.
        """
        return {
            "message_id": self._message_id,
            "recipients": [
                {
                    "nr": "",
                    "recipient_type": "cpr",
                    "nationality": "Denmark",
                    "status": "",
                    "reject_reason": "",
                    "post_processing_status": "",
                }
            ],
        }


class EboksClient(object):
    def __init__(
        self,
        mock=False,
        client_certificate=None,
        client_private_key=None,
        verify=None,
        client_id=None,
        system_id=None,
        host=None,
        timeout=60,
    ):
        self._mock = mock
        if not self._mock:
            self._client_id = client_id
            self._system_id = str(system_id)
            self._host = host
            self.timeout = timeout
            self._session = requests.session()
            self._session.cert = (client_certificate, client_private_key)
            self._verify = verify
            self._session.verify = verify
            self._session.headers.update({"content-type": "application/xml"})
            self._url_with_prefix = urllib.parse.urljoin(
                self._host, "/int/rest/srv.svc/"
            )

    def _make_request(self, url, method="GET", params=None, data=None):
        r = self._session.request(method, url, params, data, timeout=self.timeout)
        r.raise_for_status()
        return r

    def get_client_info(self):
        url = urllib.parse.urljoin(
            self._host, "/rest/client/{client_id}/".format(client_id=self._client_id)
        )
        return self._make_request(url=url)

    def get_recipient_status(self, message_ids, retries=0, retry_wait_time=10):
        url = urllib.parse.urljoin(
            self._host, "/rest/messages/{client_id}/".format(client_id=self._client_id)
        )
        try:
            return self._make_request(url=url, params={"message_id": message_ids})
        except HTTPError:
            if retries <= 3:
                sleep(retry_wait_time)  # wait 10, 20 then 40 seconds
                return self.get_recipient_status(
                    message_ids, retries + 1, retry_wait_time * 2
                )
            else:
                raise

    def get_message_id(self):
        if self._mock:
            return uuid4().hex
        return "{sys_id}{client_id}{uuid}".format(
            sys_id=self._system_id.zfill(6), client_id=self._client_id, uuid=uuid4().hex
        )

    def send_message(self, message, message_id, retries=3, retry_wait_time=10):
        if self._mock:
            return MockResponse(message_id)
        url = urllib.parse.urljoin(
            self._url_with_prefix,
            "3/dispatchsystem/{sys_id}/dispatches/{message_id}".format(
                sys_id=self._system_id, message_id=message_id
            ),
        )
        message_ids = [message_id]
        try:
            return self._make_request(url=url, method="PUT", data=message)
        except HTTPError as e:
            if retries > 0:
                if hasattr(e, "response"):
                    if e.response.status_code == 409:
                        # message_id is already used
                        message_id = self.get_message_id()
                        message_ids.append(message_id)
                sleep(retry_wait_time)  # 10, 20 ,40 seconds
                return self.send_message(
                    message, message_id, retries - 1, retry_wait_time * 2
                )
            else:
                print(
                    f"Failed sending message (id={', '.join(message_ids)}): {message}"
                )
                raise

    @staticmethod
    def parse_exception(e):
        """
        parse Request exception and return a error dict
        :param e:
        :return: error dictionary
        """
        error = {"error": str(e)}
        try:
            status_code = e.response.status_code
            try:
                error = {"status": status_code, "message": e.response.json()}
            except ValueError:
                error = {"status": status_code, "message": e.response.text}
        except AttributeError:
            pass
        return error

    def close(self):
        if hasattr(self, "_session"):
            self._session.close()

    @classmethod
    def from_settings(cls):
        eboks_settings = dict(settings.EBOKS)
        eboks_settings.pop("content_type_id")
        eboks_settings.pop("dispatch_bulk_size")
        return cls(**eboks_settings)
