import cloudinary
from django.conf import settings
from django.apps import AppConfig


class CommonConfig(AppConfig):
    name = 'common'
    verbose_name = "Common"

    def ready(self):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )
