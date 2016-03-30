import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    user__ne = django_filters.MethodFilter(action='filter_user__ne')

    class Meta:
        model = Product
        fields = {
            'category': ['exact'],
            'is_active': ['exact'],
            'user': ['exact'],
            'daily_price': ['gte', 'lte'],
            'sell_price': ['gte', 'lte'],
            'location': ['exact']
        }

    def filter_user__ne(self, queryset, value):
        return queryset.exclude(user=value)
