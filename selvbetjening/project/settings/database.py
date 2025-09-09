import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ["SELVBETJENING_DB"],
        "USER": os.environ["SELVBETJENING_DB_USER"],
        "PASSWORD": os.environ["SELVBETJENING_DB_PASSWORD"],
        "HOST": os.environ["SELVBETJENING_DB_HOST"],
    }
}
