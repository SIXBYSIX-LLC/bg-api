from common import routers
from . import views

router = routers.CustomExtendedSimpleRouter()
order_router = router.register(r'orders', views.OrderViewSet)
orderline_router = router.register(r'orderlines', views.OrderLineViewSet)
orderline_router.register(r'items', views.ItemViewSet, base_name='orderline-item',
                          parents_query_lookups=['orderline'])

urlpatterns = router.urls
