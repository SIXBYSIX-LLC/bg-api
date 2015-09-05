"""
=======
Filters
=======
"""

from rest_framework import filters as rf_filters
from django.db.models import Q


class OwnerFilterBackend(rf_filters.BaseFilterBackend):
    """
    Filter class that filters list view to its owner's subset.

    It reads two additional attributes in viewset class.

    :param list,tuple ownership_fields: List of str of model property that specify the ownership \
    of object
    :param bool skip_owner_filter: If True, this filter will be be switched off
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


class SearchFilter(rf_filters.SearchFilter):
    """
    Filter class to perform search.

    It reads ``search`` query parameter string and perform searches using queryset. Multiple search
    term can be separated by comma.

    :param Manager search_manager: Manager that should have ``.search(term)`` method implemented. \
    This filter calls that method and filter the queryset
    """
    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter.
        The while space or comma delimited has been removed and whole string will be returned
        """
        params = request.query_params.get(self.search_param, '')
        return params.replace(',', ' ').strip()

    def filter_queryset(self, request, queryset, view):
        search_manager = getattr(view, 'search_manager', None)
        term = self.get_search_terms(request)
        if search_manager and term:
            return queryset & search_manager.search(term)

        return super(SearchFilter, self).filter_queryset(request, queryset, view)
