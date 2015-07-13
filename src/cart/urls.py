from cart.views import CartViewSet, RentalItemViewSet
from common.routers import CustomExtendedSimpleRouter

router = CustomExtendedSimpleRouter()
cart = router.register(r'carts', CartViewSet)
cart.register(r'rentals', RentalItemViewSet, base_name='cart-rental-item',
              parents_query_lookups=['cart'])
cart.register(r'purchases', RentalItemViewSet, base_name='cart-purchase-item',
              parents_query_lookups=['cart'])
urlpatterns = router.urls
