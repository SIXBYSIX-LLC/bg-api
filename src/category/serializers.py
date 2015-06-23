from common import serializers
from .models import Category
from static.serializers import FileRefSerializer


class CategorySerializer(serializers.ModelSerializer):
    image = FileRefSerializer(read_only=True)

    class Meta:
        model = Category
        read_only_fields = ('hierarchy', 'image')
