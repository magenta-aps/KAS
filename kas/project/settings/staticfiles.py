import os

from project.settings.base import BASE_DIR

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

WHITENOISE_USE_FINDERS = True
