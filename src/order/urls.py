from common import routers
from . import views

router = routers.CustomExtendedSimpleRouter()
router.register(r'orders', views.OrderViewSet)
router.register(r'orderlines', views.OrderLineViewSet)

urlpatterns = router.urls
