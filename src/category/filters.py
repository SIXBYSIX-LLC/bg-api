import django_filters

from .models import Category


class CategoryFilter(django_filters.FilterSet):
    parent__isnull = django_filters.BooleanFilter(name="parent__isnull")

    class Meta:
        model = Category
        fields = ['parent__isnull', 'parent']
