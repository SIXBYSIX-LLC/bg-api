"""
Permissions
~~~~~~~~~~~
"""
import logging

from rest_framework import permissions as rf_permissions

LOG = logging.getLogger('nbmapi.' + __name__)


class DjangoModelPermissions(rf_permissions.DjangoModelPermissions):
    """
    Adds view permission
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class IsOwnerPermissions(rf_permissions.BasePermission):
    """
    Decide permission grant according to ``ownership_fields`` attribute defined in view. If it's \
    an empty object, ``True`` will always return.

    Condition check on ``ownership_fields`` will be done in ORing fashion
    """

    def has_object_permission(self, request, view, obj):
        """
        Checks for the single object if its user is same as obj. If you want to skip the owner
        permission for LISTing the data, you can set `skip_owner_filter=True` in viewset class
        """
        if request.user.is_staff or request.user.is_superuser:
            return True

        ownership_fields = getattr(view, 'ownership_fields', None)
        skip_owner_filter = getattr(view, 'skip_owner_filter', False)

        # If it's explicitly mentioned to empty
        if ownership_fields is None or (skip_owner_filter is True and request.method == 'GET'):
            return True

        _u = request.user

        # Requesting user is accessing to himself?
        if _u.profile == obj:
            return True

        result = any(_u == getattr(obj, field) or _u.id == getattr(obj, field)
                     for field in ownership_fields)
        if result is False:
            logging.warning('Permission denied', extra={'user': _u,
                                                        'ownership_fields': ownership_fields,
                                                        'object': obj})

        return result


class CustomActionPermissions(rf_permissions.BasePermission):
    """
    Implements check for custom permission defined under model's meta option. This should be used \
    for custom view actions where special permission granted to user.

    To let this permission class work, permission's *codename* should be defined as \
    ``<action_name>``. ``action_name`` is the name of custom method defined in *viewset*.
    ``has_permission()`` will match ``<app_label>.<action_name>`` as permission name, the user has.

    **Be careful using this class as it doesn't check anything apart from custom permissions.**
    """

    def has_permission(self, request, view):
        model_cls = getattr(view, 'model', None)
        queryset = getattr(view, 'queryset', None)

        if model_cls is None and queryset is not None:
            model_cls = queryset.model

        expected_perm = "%(app_label)s.%(action_name)s" % {'app_label': model_cls.get_app_label(),
                                                           'action_name': view.action}

        return request.user.has_perm(expected_perm)
