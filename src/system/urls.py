from common import routers
from . import views

router = routers.CustomRouter()
router.register('system/countries', views.CitiesViewSet)
router.register('system/configs', views.ConfigViewSet)

urlpatterns = router.urls
