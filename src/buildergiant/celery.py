from __future__ import absolute_import

import os

from celery import Celery


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buildergiant.settings')

from django.conf import settings

celeryapp = Celery('buildergiant')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
celeryapp.config_from_object('django.conf:settings')
celeryapp.autodiscover_tasks(lambda: settings.INSTALLED_APPS)