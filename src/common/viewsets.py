"""
ViewSet
~~~~~~~
"""
from rest_framework import generics as rf_generics, viewsets as rf_viewsets


class GenericAPIView(rf_generics.GenericAPIView):
    def perform_authentication(self, request):
        """
        Add parent_user object request if current user belongs to User group
        """
        request.user
        request.parent_user = request.user.profile.parent


class GenericViewSet(GenericAPIView, rf_viewsets.GenericViewSet):
    """
    Extends standard viewset features
    """

    def get_serializer_class(self):
        """
        Return the class to use for the serializer based who requesting and what is being
        requested.

        if `admin` or `staff` is requesting, the `admin_serializer_class` will be used if
        declared in viewset.

        if the object `owner` is requesting, the `owner_[ACTION]_serializer_class` will be used
        if declared in viewset

        Other than these the action based serializer class will be returned.

        For eg: if you want different serializer for create action you can define serializer as
        ``create_serializer_class`` attribute name.
        Default to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.
        """

        # Admin serializer
        admin_serializer = self._get_admin_serializer()
        if admin_serializer:
            return admin_serializer

        # Owner classes
        owner_serializer_class = self._get_owner_serializer()
        if owner_serializer_class:
            return owner_serializer_class

        # Action serializer
        serializer_class = getattr(self, '%s_serializer_class' % self.action, None)
        if serializer_class:
            return serializer_class

        return self.serializer_class


    def _get_admin_serializer(self):
        if self.request.user.is_superuser:
            return getattr(self, 'admin_serializer_class', None)

    def _get_owner_serializer(self):
        owner_serializer_class = getattr(self, 'owner_%s_serializer_class' % self.action, None)
        if owner_serializer_class:
            _u = self.request.user
            result = any(_u == getattr(self.object, field) or _u.id == getattr(self.object, field)
                         for field in self.ownership_fields)
            if result is True:
                return owner_serializer_class


class ModelViewSet(rf_viewsets.ModelViewSet, GenericViewSet):
    """
    Base class for model view set
    """

