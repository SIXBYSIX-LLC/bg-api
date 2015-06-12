from django.conf.urls import url, patterns

from common import routers
from . import views

router = routers.CustomRouter()
router.register(r'users', views.UserViewSet)

password_reset_url = patterns('usr.views', url('^users/actions/password_reset', 'password_reset'))
email_verify_url = patterns('usr.views', url('^users/actions/verify_email', 'verify_email'))

urlpatterns = router.urls + password_reset_url + email_verify_url
