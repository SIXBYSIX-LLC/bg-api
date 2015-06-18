from common.routers import CustomRouter
from views import GroupViewSet


routers = CustomRouter()
routers.register('groups', GroupViewSet)

urlpatterns = routers.urls
