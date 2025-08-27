import os
from distutils.util import strtobool

EBOKS_MOCK = bool(strtobool(os.environ.get("EBOKS_MOCK", "False")))
EBOKS = {}
if EBOKS_MOCK:
    # If mock is set ignore the rest of the settings.
    EBOKS["mock"] = EBOKS_MOCK
    EBOKS["content_type_id"] = ""
else:
    # Otherwise failfast if a single setting is missing.
    EBOKS.update(
        {
            "client_certificate": os.environ["EBOKS_CLIENT_CERTIFICATES"],
            "client_private_key": os.environ["EBOKS_CLIENT_PRIVATE_KEY"],
            "verify": os.environ["EBOKS_VERIFY"],
            "client_id": os.environ["EBOKS_CLIENT_ID"],
            "system_id": os.environ["EBOKS_SYSTEM_ID"],
            "content_type_id": os.environ["EBOKS_CONTENT_TYPE_ID"],
            "host": os.environ["EBOKS_HOST"],
        }
    )
