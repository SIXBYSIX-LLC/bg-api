from common import routers
from . import views

router = routers.CustomExtendedSimpleRouter()
(router
 .register(r'products', views.ProductViewSet)
 .register(r'inventories', views.InventoryViewSet, base_name='product-inventory',
           parents_query_lookups=['product'])
)

urlpatterns = router.urls
