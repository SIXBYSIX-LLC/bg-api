from django.apps import AppConfig


class ContactusConfig(AppConfig):
    name = 'contactus'
    verbose_name = "Contact Us"

    def ready(self):
        # noinspection PyUnresolvedReferences
        import tasks
