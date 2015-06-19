from common import routers
from . import views

router = routers.CustomExtendedSimpleRouter()
router.register(r'products', views.ProductViewSet)

urlpatterns = router.urls
