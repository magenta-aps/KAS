"""
Generated by 'django-admin startproject' using Django 2.2.18.
"""

import os
from distutils.util import strtobool

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = bool(strtobool(os.environ.get('DJANGO_DEBUG', 'False')))
ALLOWED_HOSTS = ['*']
TIME_ZONE = os.environ['DJANGO_TIMEZONE']
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'selvbetjening',
    'sullissivik.login',
]

MIDDLEWARE = [
    'django_cookies_samesite.middleware.CookiesSameSite',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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
    }
}

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
LANGUAGE_COOKIE_NAME = 'Sullissivik.Portal.Lang'
LANGUAGE_COOKIE_DOMAIN = os.environ['DJANGO_LANGUAGE_COOKIE_DOMAIN']
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]
LOCALE_MAP = {
    'da': 'da-DK',
    'kl': 'kl-GL'
}

SESSION_COOKIE_SAMESITE = 'strict'

STATIC_URL = '/static/'

UPLOAD_PATH = '/uploads'

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

LOGOUT_REDIRECT = 'selvbetjening:test'  # url reverse name to redirect to when logged out
LOGIN_DEFAULT_REDIRECT = 'selvbetjening:test'  # url reverse name to redirect to when logged in (unless another is explicitly specified in params)
LOGIN_REQUIREMENT_WHITELIST = ['/favicon.ico']

OPENID_CONNECT = {
    'enabled': False,
    'issuer': '""',  # top level url to the issuer, used for autodiscovery
    'scope': '""',  # openid is mandatory to indicated is is a openid OP, we need to use digitalimik to get the cpr/cvr number.
    'client_id': '""',  # id of the system (ouath), registered at headnet
    'client_certificate': '""',  # path to client certificate used to secure the communication between the system and OP
    'private_key': '""',  # used for signing messages passed to the OP
    'redirect_uri': '""',  # url registered at headnet to redirect the user to after a successfull login at OP
    'logout_uri': '""',  # url registered at headnet to call when logging out, removing session data there
    'front_channel_logout_uri': '""',  # url registered at headnet to call when logging out, should clear our cookies etc.
    'post_logout_redirect_uri': '""'  # url registered at headnet to redirect to when logout is complete
}

NEMID_CONNECT = {
    'enabled': False,
    'federation_service': '""',
    'cookie_name': '""',
    'cookie_path': '""',
    'cookie_domain': '""',
    'login_url': '""',
    'redirect_field': '""',
    'client_certificate': '""',
    'private_key': '""',
    'get_user_service': '""',
}
