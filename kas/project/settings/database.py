import os

# DEFAULT_AUTO_FIELD er sat, da vi benytter 3. parts biblioteker der ikke har
# fuldt implementeret app_config.
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "TIME_ZONE": os.environ.get("DJANGO_TIMEZONE", "America/Nuuk"),
    },
    "eskat": {
        "ENGINE": "django.db.backends.oracle",
        "NAME": (
                "("
                "DESCRIPTION=(ADDRESS="
                "(PROTOCOL=TCP)"
                "(HOST=" + os.environ["ESKAT_HOST"] + ")"
                "(PORT=" + os.environ["ESKAT_PORT"] + ")"
                ")"
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
