import json
import os
import sys
from distutils.util import strtobool
from os.path import dirname

VERSION = os.environ["COMMIT_TAG"]
BASE_DIR = dirname(dirname(dirname((os.path.abspath(__file__)))))

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = bool(strtobool(os.environ.get("DJANGO_DEBUG", "False")))

HOST_DOMAIN = os.environ.get("HOST_DOMAIN", "https://kas.aka.nanoq.gl")
ALLOWED_HOSTS = json.loads(os.environ.get("ALLOWED_HOSTS", "[]"))
CSRF_TRUSTED_ORIGINS = json.loads(os.environ.get("CSRF_TRUSTED_ORIGINS", "[]"))

ROOT_URLCONF = "project.urls"
WSGI_APPLICATION = "project.wsgi.application"

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 900

UPLOAD_PATH = "/uploads"

REST_HOST = os.environ["REST_HOST"]
REST_TOKEN = os.environ["REST_TOKEN"]
REST_REQUEST_TIMEOUT = int(os.environ.get("REST_REQUEST_TIMEOUT", "5"))
# REST_CA_CERT = os.environ['REST_CA_CERT']
KAS_REPRESENTATION_STOP = os.environ["KAS_REPRESENTATION_STOP"]

DEFAULT_CPR = os.environ.get("DEFAULT_CPR", None)

# Month and day where the interface should be closed
CLOSE_AT = {
    "month": int(os.environ["CLOSE_AT_MONTH"]),
    "date": int(os.environ["CLOSE_AT_DATE"]),
}
# Skip health_check for cache layer and storage since we are not using it
WATCHMAN_CHECKS = ("watchman.checks.databases",)

# Feature flags and their defaults can be specified here. Once specified
# a feature flag can be overriden using the environment by specifying
# the environment variable FEATURE_FLAG_<name_of_flag_uppercased>.
FEATURE_FLAGS = {
    "test_feature_flag": False,
}
for x in FEATURE_FLAGS:
    env_key = "FEATURE_FLAG_" + x.upper()
    if env_key in os.environ:
        value = os.environ[env_key]
        FEATURE_FLAGS[x] = bool(strtobool(value))


TESTING = bool(len(sys.argv) > 1 and sys.argv[1] == "test")
