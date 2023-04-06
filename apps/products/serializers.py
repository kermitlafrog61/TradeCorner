from rest_framework import serializers

from .models import Product
from apps.users.serializers import UserSerializer


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = serializers.ImageField(max_length=None, use_url=True)
    
    class Meta:
        model = Product
        fields = (
            'id', 'category', 'user', 'title', 'slug',
            'image', 'price', 'description', 'is_sold'
        )
        read_only_fields = (
            'id', 'user'
        )