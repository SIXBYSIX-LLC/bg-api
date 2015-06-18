from common.viewsets import ModelViewSet
from .serializers import *
from .models import Group


class GroupViewSet(ModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    paginate_by = 0
    paginate_by_param = ''
