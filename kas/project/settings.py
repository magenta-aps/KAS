import os
from distutils.util import strtobool
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

VERSION = os.environ["VERSION"]

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = bool(strtobool(os.environ.get("DJANGO_DEBUG", "False")))
ALLOWED_HOSTS = ["*"]
TIME_ZONE = os.environ["DJANGO_TIMEZONE"]
LOGIN_REDIRECT_URL = "/"
SESSION_COOKIE_NAME = "admin-sessionid"
WHITENOISE_USE_FINDERS = True
# DEFAULT_AUTO_FIELD  er sat da vi benytter 3 parts biblioteker der ikke har fuldt implementeret app_config
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

STATIC_ROOT = os.path.join(BASE_DIR, "kas", "static")
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_rq",
    "prisme",
    "kas",
    "eskat",
    "worker",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "simple_history",
    "watchman",
    "django_extensions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["project/templates/"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "project.context_processors.feature_flag_processor",
                "kas.context_processors.representation_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
    },
    "eskat": {
        "ENGINE": "django.db.backends.oracle",
        "NAME": (
            "("
            "DESCRIPTION=(ADDRESS="
            "(PROTOCOL=TCP)"
            "(HOST=" + os.environ["ESKAT_HOST"] + ")"
            "(PORT=" + os.environ["ESKAT_PORT"] + "))"
            "(CONNECT_DATA=(SERVICE_NAME=" + os.environ["ESKAT_DB"] + "))"
            ")"
        ),
        "USER": os.environ["ESKAT_USER"],
        "PASSWORD": os.environ["ESKAT_PASSWORD"],
        "HOST": "",
        "PORT": "",
    },
}

DATABASE_ROUTERS = ["eskat.database_routers.ESkatRouter"]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "da-DK"

USE_I18N = True

USE_L10N = True

USE_TZ = True
LANGUAGES = [
    ("da", _("Danish")),
    ("kl", _("Greenlandic")),
]


STATIC_URL = "/static/"

UPLOAD_PATH = "/uploads"
MEDIA_ROOT = "/srv/media/"
MEDIA_URL = "/media/"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "gunicorn": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["gunicorn"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["gunicorn"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
REDIS = {
    "HOST": os.environ.get("REDIS_HOST", "redis"),
    "PORT": 6379,
    "DB": 1,
    "DEFAULT_TIMEOUT": 360,
}
RQ_QUEUES = {"default": REDIS, "high": REDIS, "low": REDIS}
RQ_EXCEPTION_HANDLERS = ["worker.exception_handler.write_exception_to_db"]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

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

EBOKS_MOCK = bool(strtobool(os.environ.get("EBOKS_MOCK", "False")))
EBOKS = {"dispatch_bulk_size": int(os.environ["EBOKS_DISPATCH_BULK_SIZE"])}
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

TENQ = {
    "host": os.environ["TENQ_HOST"],
    "port": int(os.environ.get("TENQ_PORT") or 22),
    "username": os.environ["TENQ_USER"],
    "password": os.environ["TENQ_PASSWORD"],
    "known_hosts": os.environ.get("TENQ_KNOWN_HOSTS") or None,
    "dirs": {
        "10q_production": "/nanoq/prod/q",
        "10q_development": "/nanoq/uddannelse/KAS",
    },
    "destinations": {
        "production": [
            "10q_production",
            "10q_development",
        ],  # Our prod server can use both prod and dev on the 10q server
        "development": [
            "10q_development",
            "10q_mocking",
        ],  # Our dev server can only use dev on the 10q server
        "staging": ["10q_development"],
    },
    "project_id": os.environ["TENQ_PROJECT_ID"],
}

DAFO = {
    "mock": strtobool(os.environ.get("PITU_MOCK", "False")),
    "certificate": os.environ.get("PITU_CERTIFICATE"),
    "private_key": os.environ.get("PITU_KEY"),
    "root_ca": os.environ.get("PITU_ROOT_CA"),
    "service_header_cpr": os.environ.get("PITU_UXP_SERVICE_CPR"),
    "client_header": os.environ.get("PITU_UXP_CLIENT"),
    "url": os.environ.get("PITU_URL"),
}

# Skip health_check for cache layer since we are not using it
WATCHMAN_CHECKS = ("watchman.checks.databases", "watchman.checks.storage")
# skip checking of oracle database
WATCHMAN_DATABASES = ["default"]

METRICS = {
    # used to disable metrics in the pipeline
    "disable": bool(strtobool(os.environ.get("DISABLE_METRICS", "False"))),
}

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
