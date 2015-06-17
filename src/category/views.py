from common.viewsets import ModelViewSet
from . import serializers
from . import models


class CategoryViewSet(ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    # Turn off pagination
    paginate_by = 0
    paginate_by_param = ''
