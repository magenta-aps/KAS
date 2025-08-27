import os
import sys
from distutils.util import strtobool

from django.core.exceptions import ImproperlyConfigured

VERSION = os.environ["COMMIT_TAG"]

TESTING = bool(len(sys.argv) > 1 and sys.argv[1] == "test")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = bool(strtobool(os.environ.get("DJANGO_DEBUG", "False")))
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = "project.urls"
WSGI_APPLICATION = "project.wsgi.application"

UPLOAD_PATH = "/uploads"
MEDIA_ROOT = "/srv/media/"
MEDIA_URL = "/media/"


SELVBETJENING_REPRESENTATION_START = os.environ["SELVBETJENING_REPRESENTATION_START"]
SELVBETJENING_REPRESENTATION_STOP = os.environ["SELVBETJENING_REPRESENTATION_STOP"]
SELVBETJENING_REPRESENTATION_TOKEN_MAX_AGE = int(
    os.environ.get("SELVBETJENING_REPRESENTATION_TOKEN_MAX_AGE", 60)
)

ENVIRONMENT = os.environ["ENVIRONMENT"]
if ENVIRONMENT not in ("development", "staging", "production"):
    raise ImproperlyConfigured(
        "Environment needs to be set to either development, staging or production!"
    )

KAS_TAX_RATE = 0.153
KAS_TAX_RATE_IN_PERCENT = KAS_TAX_RATE * 100

TRANSACTION_INDIFFERENCE_LIMIT = int(
    os.environ.get("TRANSACTION_INDIFFERENCE_LIMIT") or 100
)

REPORT_EXCLUDE_ALREADY_GENERATED = False


# Feature flags and their defaults can be specified here. Once specified
# a feature flag can be overriden using the environment by specifying
# the environment variable FEATURE_FLAG_<name_of_flag_uppercased>.
FEATURE_FLAGS = {
    "enable_feature_flag_list": False,
    "test_feature_flag": False,
    "enable_dafo_override_of_address": True,
}
for x in FEATURE_FLAGS:
    env_key = "FEATURE_FLAG_" + x.upper()
    if env_key in os.environ:
        value = os.environ[env_key]
        FEATURE_FLAGS[x] = bool(strtobool(value))

LEGACY_YEARS = (2018, 2019)

