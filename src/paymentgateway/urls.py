from common.routers import CustomRouter
from . import views

router = CustomRouter()
router.register(r'paymentgateway/braintree', views.BraintreeViewSet, base_name='pg-braintree')

urlpatterns = router.urls
