from common.routers import CustomRouter
from . import views


router = CustomRouter()
router.register(r'reviews', views.OrderItemViewSet)

urlpatterns = router.urls
