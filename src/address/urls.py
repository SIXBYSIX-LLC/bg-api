from common import routers
from .views import AddressViewSet


router = routers.CustomRouter()
router.register(r'addresses', AddressViewSet)

urlpatterns = router.urls
