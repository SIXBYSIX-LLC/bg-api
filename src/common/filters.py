from rest_framework import filters as rf_filters
from django.db.models import Q


class OwnerFilterBackend(rf_filters.BaseFilterBackend):
    """
    Filters list view to its owner's subset. It reads two additional attributes in viewset class
    ``ownership_fields``. It can be switched off by specifying `ownership_fields` to False

    *ownership_fields* will specify which attribute of the model poses the ownership of object.
    """

    def filter_queryset(self, request, queryset, view):
        ownership_fields = getattr(view, 'ownership_fields', False)
        skip_owner_filter = getattr(view, 'skip_owner_filter', False)
        # Define user, as requested user is either owner or any member
        request_user = request.parent_user or request.user

        if view.action != 'list' or not ownership_fields or skip_owner_filter is True:
            return queryset

        if request.user.is_staff or request.user.is_superuser:
            return queryset

        q = Q()
        for field in ownership_fields:
            q |= Q(**{field: request_user.id})
        queryset = queryset.filter(q)

        return queryset
