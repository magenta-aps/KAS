import os

from django.utils.translation import gettext_lazy as _


TIME_ZONE = os.environ["DJANGO_TIMEZONE"]
LANGUAGE_CODE = "da-DK"
USE_I18N = True
USE_L10N = True

USE_TZ = True
LANGUAGES = [
    ("da", _("Danish")),
    ("kl", _("Greenlandic")),
]
