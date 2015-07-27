from common.routers import CustomRouter
from charge.views import SalesTaxViewSet, AdditionalChargeViewSet

router = CustomRouter()
router.register(r'charges/sales_taxes', SalesTaxViewSet)
router.register(r'charges/additional_charges', AdditionalChargeViewSet)

urlpatterns = router.urls
