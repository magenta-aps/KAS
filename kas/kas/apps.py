from django.apps import AppConfig


class KasConfig(AppConfig):
    name = "kas"

    def ready(self):
        from project import checks  # noqa
