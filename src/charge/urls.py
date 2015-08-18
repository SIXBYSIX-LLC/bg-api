from common.routers import CustomRouter
from charge.views import AdditionalChargeViewSet

router = CustomRouter()
router.register(r'charges/additional_charges', AdditionalChargeViewSet)

urlpatterns = router.urls
