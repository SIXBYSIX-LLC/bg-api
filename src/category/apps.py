from django.apps import AppConfig


class CategoryConfig(AppConfig):
    name = 'category'
    verbose_name = "category"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import tasks
