import os
from distutils.util import strtobool

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = bool(strtobool(os.environ.get('DJANGO_DEBUG', 'False')))
ALLOWED_HOSTS = ['*']
TIME_ZONE = os.environ['DJANGO_TIMEZONE']
LOGIN_REDIRECT_URL = '/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django_rq",
    'kas',
    'eskat',
    'worker',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'simple_history',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ['POSTGRES_HOST'],
    },
    'eskat': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': (
            '('
            'DESCRIPTION=(ADDRESS='
            '(PROTOCOL=TCP)'
            '(HOST=' + os.environ['ESKAT_HOST'] + ')'
            '(PORT=' + os.environ['ESKAT_PORT'] + '))'
            '(CONNECT_DATA=(SERVICE_NAME=' + os.environ['ESKAT_DB'] + '))'
            ')'
        ),
        'USER': os.environ['ESKAT_USER'],
        'PASSWORD': os.environ['ESKAT_PASSWORD'],
        'HOST': '',
        'PORT': '',
    },
}

# Make a copy of the default database handle that can be used for
# avoiding transaction issues during imports
DATABASES['second_default'] = DATABASES['default'].copy()

DATABASE_ROUTERS = ['eskat.database_routers.ESkatRouter']

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'da-DK'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

UPLOAD_PATH = '/uploads'
MEDIA_ROOT = "/srv/media/"
MEDIA_URL = "/media/"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'gunicorn': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['gunicorn'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['gunicorn'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
REDIS = {
    'HOST': 'redis',
    'PORT': 6379,
    'DB': 1,
    'DEFAULT_TIMEOUT': 360,
}
RQ_QUEUES = {
    'default': REDIS,
    'high': REDIS,
    'low': REDIS
}
RQ_EXCEPTION_HANDLERS = ['worker.exception_handler.write_exception_to_db']

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}

ENVIRONMENT = os.environ['ENVIRONMENT']

KAS_TAX_RATE = 0.153
KAS_TAX_RATE_IN_PERCENT = KAS_TAX_RATE * 100

EBOKS = {
    'client_certificate': os.environ['EBOKS_CLIENT_CERTIFICATES'],
    'client_private_key': os.environ['EBOKS_CLIENT_PRIVATE_KEY'],
    'verify': os.environ['EBOKS_VERIFY'],
    'client_id': os.environ['EBOKS_CLIENT_ID'],
    'system_id': os.environ['EBOKS_SYSTEM_ID'],
    'content_type_id': os.environ['EBOKS_CONTENT_TYPE_ID'],
    'host': os.environ['EBOKS_HOST'],
    'dispatch_bulk_size': int(os.environ['EBOKS_DISPATCH_BULK_SIZE'])
}
