from django.apps import AppConfig


class OrderConfig(AppConfig):
    name = 'order'
    verbose_name = "Order"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import tasks
