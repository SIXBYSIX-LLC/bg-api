"""
=======
ViewSet
=======
"""
from django.contrib.auth.models import AnonymousUser
from rest_framework import generics as rf_generics, viewsets as rf_viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin as _NestedViewSetMixin


class GenericAPIView(rf_generics.GenericAPIView):
    """
    Extends feature to add parent_user object to request object
    """
    def perform_authentication(self, request):
        """
        Add parent_user object request if current user belongs to User group
        """
        request.user
        if isinstance(request.user, AnonymousUser) is False:
            parent = request.parent_user = request.user.profile.parent
            # Assign parent user only if they belongs to user group
            if parent and (parent.is_superuser is True or parent.is_staff is True):
                request.parent_user = None


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


class NestedViewSetMixin(_NestedViewSetMixin):
    """
    Extends feature to

    * Method to get parent object
    * Add parent query dict to ``request.data``
    """
    def create(self, request, *args, **kwargs):
        self.get_parent_object()
        request.data.update(**self.get_parents_query_dict())

        return super(NestedViewSetMixin, self).create(request, *args, **kwargs)

    def get_parent_object(self):
        """
        Checks the object's parent object permission and returns it
        """
        # Getting related field name
        parent_object_name = self.get_parents_query_dict().keys()[:1][0]
        # Getting parent model
        parent_model = self.get_queryset().model._meta.get_field(parent_object_name).rel.to
        # Getting parent object
        parent_object = parent_model.objects.get(
            id=self.get_parents_query_dict().get(parent_object_name)
        )

        self.check_object_permissions(self.request, parent_object)

        return parent_object
