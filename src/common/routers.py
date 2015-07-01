"""
Routers
=======
"""
import re

from django.core.exceptions import ImproperlyConfigured
from rest_framework import routers as rf_routers
from rest_framework_extensions import routers as rfe_routers


class CustomRouter(rf_routers.SimpleRouter):
    """
    Extends simple router with default trailing_slash to False
    """

    def __init__(self):
        super(CustomRouter, self).__init__(trailing_slash=False)

    def get_urls(self):
        """
        non standard method name ``actions_deactivate`` will appear in url as ``actions/deactivate``
        """
        urls = super(CustomRouter, self).get_urls()

        for url in urls:
            url._regex = re.sub(r'/actions?_', '/actions/', url._regex, 1)

        return urls


class CustomExtendedSimpleRouter(rfe_routers.ExtendedSimpleRouter, CustomRouter):
    def get_dynamic_routes(self, viewset):
        known_actions = self.get_known_actions()
        dynamic_routes = []
        for methodname in dir(viewset):

            attr = getattr(viewset, methodname)
            httpmethods = getattr(attr, 'bind_to_methods', None)
            if httpmethods:
                endpoint = getattr(attr, 'endpoint', methodname)
                is_for_list = not getattr(attr, 'detail', True)
                if endpoint in known_actions:
                    raise ImproperlyConfigured('Cannot use @action or @link decorator on '
                                               'method "%s" as %s is an existing route'
                                               % (methodname, endpoint))
                httpmethods = [method.lower() for method in httpmethods]
                dynamic_routes.append((httpmethods, methodname, endpoint, is_for_list))
        return dynamic_routes
