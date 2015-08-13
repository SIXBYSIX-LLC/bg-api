from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.viewsets import GenericViewSet
from paymentgateway.models import Braintree


class BraintreeViewSet(GenericViewSet):
    permission_classes = (IsAuthenticated,)

    @list_route(methods=['GET'])
    def action_generate_token(self, request, *args, **kwargs):
        return Response({'client_token': Braintree().generate_client_token()})
