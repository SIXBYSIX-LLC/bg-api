from common.routers import CustomExtendedSimpleRouter
from inquiry.views import ThreadViewSet, MessageViewSet

router = CustomExtendedSimpleRouter()
(
    router
    .register(r'inquiries', ThreadViewSet)
    .register(r'messages', MessageViewSet, base_name='inquiry-message',
              parents_query_lookups=['thread'])
)

urlpatterns = router.urls
