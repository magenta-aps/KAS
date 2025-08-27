import os
from distutils.util import strtobool

DAFO = {
    "mock": strtobool(os.environ.get("PITU_MOCK", "False")),
    "certificate": os.environ.get("PITU_CERTIFICATE"),
    "private_key": os.environ.get("PITU_KEY"),
    "root_ca": os.environ.get("PITU_ROOT_CA"),
    "service_header_cpr": os.environ.get("PITU_UXP_SERVICE_CPR"),
    "client_header": os.environ.get("PITU_UXP_CLIENT"),
    "url": os.environ.get("PITU_URL"),
}
