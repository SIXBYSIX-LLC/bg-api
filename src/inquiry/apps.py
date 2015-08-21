from django.apps import AppConfig


class InquiryConfig(AppConfig):
    name = 'inquiry'
    verbose_name = "Inquiry"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import tasks
