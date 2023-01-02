from django.apps import AppConfig


class EskatConfig(AppConfig):
    name = "eskat"

    def ready(self):
        from project import checks  # noqa
