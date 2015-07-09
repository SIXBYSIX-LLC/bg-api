from common import routers
from . import views

router = routers.CustomExtendedSimpleRouter()
user_router = router.register(r'orders', views.OrderViewSet)

urlpatterns = router.urls
