from django.apps import AppConfig


class CartConfig(AppConfig):
    name = 'cart'
    verbose_name = "Cart"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import tasks
