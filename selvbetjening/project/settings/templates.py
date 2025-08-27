TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "project.context_processors.feature_flag_processor",
            ],
            "libraries": {
                "csp": "csp.templatetags.csp",
            },
        },
    },
]
