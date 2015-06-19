from django.apps import AppConfig


class SystemConfig(AppConfig):
    name = 'system'
    verbose_name = "System"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import tasks
