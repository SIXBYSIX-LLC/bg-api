import django_filters

from common import helper
from .models import Category


class CategoryFilter(django_filters.FilterSet):
    parent__isnull = django_filters.MethodFilter(action='filter_parent_isnull')

    class Meta:
        model = Category
        fields = ['parent__isnull', 'parent']

    def filter_parent_isnull(self, queryset, value):
        return queryset.filter(parent__isnull=helper.str2bool(value))
