import re

from rest_framework import routers as rf_routers
from rest_framework_extensions import routers as rfe_routers


class CustomRouter(rf_routers.SimpleRouter):
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
    pass
