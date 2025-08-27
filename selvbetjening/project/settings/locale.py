import os

import django.conf.locale
from project.settings.base import BASE_DIR

LANGUAGE_CODE = "da-DK"

USE_I18N = True
USE_L10N = False
USE_TZ = True
USE_THOUSAND_SEPARATOR = True
LANGUAGE_COOKIE_NAME = "Sullissivik.Portal.Lang"
LANGUAGE_COOKIE_DOMAIN = os.environ["DJANGO_LANGUAGE_COOKIE_DOMAIN"]
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]
LOCALE_MAP = {"da": "da-DK", "kl": "kl-GL"}
TIME_ZONE = os.environ["DJANGO_TIMEZONE"]

LANGUAGES = [
    ("da", ("Dansk")),
    ("kl", ("Kalaallisut")),
]

# Add custom languages not provided by Django
django.conf.locale.LANG_INFO["kl"] = {
    "bidi": False,
    "code": "kl",
    "name": "Greenlandic",
    "name_local": "Kalaallisut",
}
