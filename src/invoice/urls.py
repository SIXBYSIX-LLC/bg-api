from common.routers import CustomExtendedSimpleRouter
from . import views


router = CustomExtendedSimpleRouter()
router.register(r'invoices', views.InvoiceViewSet)
invoiceline = router.register(r'invoicelines', views.InvoiceLineViewSet)
invoiceline.register(r'items', views.ItemViewSet, parents_query_lookups=['invoiceline'],
                     base_name="invoiceline-item")

urlpatterns = router.urls
