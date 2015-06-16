from common import routers
from . import views

router = routers.CustomRouter()
router.register('system/countries', views.CitiesViewSet)

urlpatterns = router.urls
