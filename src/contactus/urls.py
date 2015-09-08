from common.routers import CustomRouter
from contactus.views import ContactUsViewSet


router = CustomRouter()
router.register(r'contactus', ContactUsViewSet)

urlpatterns = router.urls
