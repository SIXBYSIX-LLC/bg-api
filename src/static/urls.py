from common.routers import CustomRouter
from . import views

router = CustomRouter()
router.register(r'staticfiles', views.StaticFileViewSet)

urlpatterns = router.urls
