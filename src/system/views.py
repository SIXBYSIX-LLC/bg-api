from rest_framework import decorators
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from cities.models import Country, Region, City

from common import viewsets
from .models import Config
from system.serializers import ConfigSerializer


class CitiesViewSet(viewsets.GenericViewSet):
    queryset = Country.objects.all()
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        data = {country.id: country.name for country in Country.objects.all()}

        return Response(data)

    @decorators.detail_route(methods=['GET'])
    def regions(self, request, *args, **kwargs):
        c_id = kwargs.get('pk')
        data = {region.id: region.name for region in Region.objects.filter(country_id=c_id)}

        return Response(data)


    @decorators.detail_route(methods=['GET'], url_path='regions/(?P<rpk>[^/.]+)/cities')
    def cities(self, request, *args, **kwargs):
        r_id = kwargs.get('rpk')
        data = {city.id: city.name for city in City.objects.filter(region_id=r_id)}

        return Response(data)


class ConfigViewSet(viewsets.GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    queryset = Config.objects.all()
    serializer_class = ConfigSerializer

    def update(self, request, *args, **kwargs):
        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        Config.objects.get_or_create(**filter_kwargs)

        return super(ConfigViewSet, self).update(request, *args, **kwargs)
