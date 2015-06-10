from rest_framework import routers as rf_routers


class CustomRouter(rf_routers.SimpleRouter):
    def __init__(self):
        super(CustomRouter, self).__init__(trailing_slash=False)
