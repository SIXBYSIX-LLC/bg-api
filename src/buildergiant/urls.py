"""buildergiant URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from common.auth.authtoken import obtain_auth_token



# Automatically collects local apps urls, so we don't need to edit urlpatterns each time we add
# new app
localapp_urlpatterns = []
for app in settings.LOCAL_APPS:
    try:
        localapp_urlpatterns.append(url(r'^', include('%s.urls' % app)))
    except ImportError:
        pass

urlpatterns = [
                  url(r'^admin', include(admin.site.urls)),
                  url(r'^login$', obtain_auth_token),
              ] + localapp_urlpatterns
