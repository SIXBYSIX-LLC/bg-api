from rest_framework.mixins import CreateModelMixin, DestroyModelMixin

from common.viewsets import GenericViewSet
from models import File
from serializers import FileSerializer


class StaticFileViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

