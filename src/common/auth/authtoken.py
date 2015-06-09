from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from common.renderer import JSONRenderer
from usr.serializers import LoginSerializer


class CustomObtainAuthToken(ObtainAuthToken):
    """
    To obtain authentication token for users using their ``username`` and ``password``
    Required fields: ``username``, ``password``
    """

    #: Overriding the rest_framework's ObtainAuthToken for generating JSON response
    #: as per BuilderGiant's specification.
    # It has to be done separately as it's not part of this system. Hence can't use the default
    # render class parameter set in configuration
    renderer_classes = (JSONRenderer,)

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        serializer.is_valid(True)
        user = serializer.validated_data['user']
        user_data = {}
        profile = getattr(user, 'profile', None)
        if profile:
            profile = LoginSerializer(profile)
            user_data = profile.data

        # get or create access token
        token, created = Token.objects.get_or_create(user=user)
        # merging token and user information
        data = dict({'token': token.key}.items() + user_data.items())

        return Response(data)

#: To bind CustomObtainAuthToken to system's URL
obtain_auth_token = CustomObtainAuthToken.as_view()
