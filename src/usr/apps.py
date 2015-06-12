from django.apps import AppConfig


class UserConfig(AppConfig):
    name = 'usr'
    verbose_name = "User"

    def ready(self):
