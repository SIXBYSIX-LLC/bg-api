from django.apps import AppConfig


class InvoiceConfig(AppConfig):
    name = 'invoice'
    verbose_name = "Invoice"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import tasks
