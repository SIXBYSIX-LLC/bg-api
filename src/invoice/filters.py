from rest_framework_filters import FilterSet
from rest_framework_filters import filters

from .models import Invoice


class InvoiceFilter(FilterSet):
    date_created_at__gte = filters.IsoDateTimeFilter('date_created_at', lookup_type='gte')
    date_created_at__lte = filters.IsoDateTimeFilter('date_created_at', lookup_type='lte')

    class Meta:
        model = Invoice
        fields = {
            'order': ['exact'],
        }
