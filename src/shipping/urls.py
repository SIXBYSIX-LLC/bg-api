from common.routers import CustomRouter
from shipping.views import StandardShippingViewSet

router = CustomRouter()
router.register(r'settings/shipping/standard', StandardShippingViewSet)

urlpatterns = router.urls
