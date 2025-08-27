CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "default_cache",
    },
    "saml": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "saml_cache",
        "TIMEOUT": 7200,
    },
}
