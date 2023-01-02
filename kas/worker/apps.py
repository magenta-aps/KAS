from django.apps import AppConfig


class WorkerConfig(AppConfig):
    name = "worker"

    def ready(self):
        from project import checks  # noqa
