from common import routers
from . import views

router = routers.CustomRouter()
router.register(r'users', views.UserViewSet)
urlpatterns = router.urls
