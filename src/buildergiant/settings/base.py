"""
Django settings for buildergiant project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from kombu import Queue


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'o4ef3#n+b*d$_o9epi_*3)p+_-^xauezf6b*)y+36y7ijf^1h*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# --------- PASSWORD HASHER CONFIGURATION
# See: https://docs.djangoproject.com/en/1.6/topics/auth/passwords/
# Note: libffi must be installed.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
)
# --------- END PASSWORD HASHER CONFIGURATION


# --------- Application definition
DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages'
)

THIRD_PARTY_APPS = (
    'rest_framework',
    'rest_framework.authtoken',
    'miniauth',
    'cities'
)

LOCAL_APPS = (
    'common',
    'system',
    'usr',
    'address'
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'common.middleware.HeadInfoMiddleware'
)

ROOT_URLCONF = 'buildergiant.urls'

WSGI_APPLICATION = 'buildergiant.wsgi.application'

APPEND_SLASH = False
#--------- END Application definition


#--------- Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'buildergiant',
        'USER': 'abhinav',
        'PASSWORD': 'admin',
        'CONN_MAX_AGE': 1 * 60 * 60  # 1 hour
    }
}
#--------- END Database


# -------- REST framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ('common.renderer.JSONRenderer',),
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.TokenAuthentication',),
    'PAGINATE_BY': 10,  # Default to 10
    'PAGINATE_BY_PARAM': 'page_size',  # Allow client to override, using `?page_size=xxx`.
    'MAX_PAGINATE_BY': 100,  # Maximum limit allowed when using `?page_size=xxx`.
    'EXCEPTION_HANDLER': 'common.helper.custom_exception_handler',
}
# -------- End REST framework


# --------- Celery
# Configuring queue
CELERY_CREATE_MISSING_QUEUES = True
CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'
CELERY_QUEUES = (
    Queue('default', routing_key='default'),
    Queue('video', routing_key='video'),
    Queue('push_notification', routing_key='push_notification'),
    Queue('email', routing_key='email'),
)

CELERY_ACCEPT_CONTENT = ['pickle', 'json']
BROKER_URL = 'redis://localhost:6379/9'
# --------- End Celery


# --------- Email (Mandrill) specific
# See: https://djrill.readthedocs.org/en/v1.2/installation/#configuration
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
MANDRILL_API_KEY = "OVERRIDE_THIS"
# Email templates
ETPL_VERIFICATION = 'bg-email-verification'
# --------- End Email (Mandrill) specific


#--------- Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
#--------- END Internationalization


#--------- CUSTOM AUTH CONFIGURATION
#: Specify the authentication User model, we're using ``miniauth`` module which gives only
#: email and password fields. `See here <https://github.com/inabhi9/django-miniauth>`_
AUTH_USER_MODEL = 'miniauth.User'
#--------- END CUSTOM AUTH CONFIGURATION

CITIES_POSTAL_CODES = ['US']
CITIES_LOCALES = ['en']


# --------- Misc
WEB_DOMAIN = 'www.buildergiant.com'
#--------- End Misc
