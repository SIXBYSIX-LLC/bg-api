from cart.views import CartViewSet, RentalItemViewSet
from common.routers import CustomExtendedSimpleRouter

router = CustomExtendedSimpleRouter()
cart = router.register(r'carts', CartViewSet)
cart.register(r'rental_products', RentalItemViewSet, base_name='cart-rental-item',
              parents_query_lookups=['cart'])

urlpatterns = router.urls
