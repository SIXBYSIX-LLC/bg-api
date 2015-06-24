from django.conf.urls import url, patterns

from common import routers
from . import views

router = routers.CustomExtendedSimpleRouter()
user_router = router.register(r'users', views.UserViewSet, base_name='user')

user_router.register(r'addresses', views.AddressViewSet, base_name='user-address',
                     parents_query_lookups=['user'])

user_router.register(r'favorite_products', views.FavoriteProductViewSet,
                     base_name='user-favorite-products', parents_query_lookups=['user'])

password_reset_url = patterns('usr.views', url('^users/actions/password_reset', 'password_reset'))
email_verify_url = patterns('usr.views', url('^users/actions/verify_email', 'verify_email'))

urlpatterns = router.urls + password_reset_url + email_verify_url
