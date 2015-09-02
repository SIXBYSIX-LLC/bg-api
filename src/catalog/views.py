from django.db.models import Count, Case, When, Value
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from cities.models import Country

from common import viewsets
from . import serializers, models
from usr.models import Address
from shipping.serializers import StandardShippingSerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProductSerializer
    list_serializer_class = retrieve_serializer_class = serializers.ProductListSerializer
    queryset = models.Product.objects.all()
    filter_fields = {'category': ['exact'], 'is_active': ['exact'], 'user': ['exact'],
                     'daily_price': ['gte', 'lte'], 'sell_price': ['gte', 'lte'],
                     'location': ['exact']}
    search_manager = models.Product.objects
    facets_fields = ('location',)

    ordering_fields = ('name', 'daily_price', 'sell_price')
    ordering = ('-id',)

    ownership_fields = ('user',)
    skip_owner_filter = True

    def get_queryset(self):
        qs = super(ProductViewSet, self).get_queryset()
        qs = qs.annotate(qty=Count(Case(When(inventory__is_active=True, then=Value(1)))))
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Location facets
        location_facets_qs = queryset.order_by().values('location').annotate(count=Count('*'))
        location_facets = serializers.FacetSerializer.LocationSerializer(location_facets_qs,
                                                                         many=True).data

        response = super(ProductViewSet, self).list(request, *args, **kwargs)
        response.data.update({'facets': location_facets})
        return response

    @detail_route(methods=['GET'])
    def available_shippings(self, request, *args, **kwargs):
        product = self.get_object()
        country_id = request.GET.get('country')
        zip_code = request.GET.get('zip_code')
        data = {'standard_shipping': None}

        # Building Address object to query standard shipping method
        try:
            location = Address(country=Country.objects.get(id=country_id), zip_code=zip_code)
            standard_ship = product.get_standard_shipping_method(location)
            if standard_ship:
                standard_ship = StandardShippingSerializer(standard_ship)
                data['standard_shipping'] = standard_ship.data
        except Address.DoesNotExist:
            pass

        return Response(data)


class InventoryViewSet(viewsets.NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = serializers.InventorySerializer
    list_serializer_class = retrieve_serializer_class = serializers.InventoryListSerializer
    queryset = models.Inventory.objects.all()

    ownership_fields = ('user',)
