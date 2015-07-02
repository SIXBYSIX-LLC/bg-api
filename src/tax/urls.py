from common.routers import CustomRouter
from tax.views import SalesTaxViewSet

router = CustomRouter()
router.register(r'taxes/sales_tax', SalesTaxViewSet)

urlpatterns = router.urls
