from common import routers
from .views import CategoryViewSet


router = routers.CustomRouter()
router.register(r'categories', CategoryViewSet)

urlpatterns = router.urls
