from django.apps import AppConfig


class PrismeConfig(AppConfig):
    name = "prisme"

    def ready(self):
        from project import checks  # noqa
