import os

from project.settings.base import BASE_DIR

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
