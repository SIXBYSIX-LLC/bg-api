from django.apps import AppConfig


class CatalogConfig(AppConfig):
    name = 'catalog'
    verbose_name = "Catalog"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import tasks
