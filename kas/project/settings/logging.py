from project.settings.base import TESTING

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

if TESTING:
    import logging

    logging.disable(logging.CRITICAL)
