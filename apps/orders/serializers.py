from rest_framework import serializers

from apps.products.serializers import ProductSerializer
from apps.users.serializers import UserSerializer
from .models import Order
from .units import STATUS_CHOISES


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = (
            'id', 'user', 'product', 'created_at',
            'updated_at', 'status', 'address'
        )
        read_only_fields = (
            'id', 'user', 'product',
            'created_at', 'updated_at'
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['product'] = ProductSerializer(instance.product).data
        return rep


class OrderUpdateStatus(serializers.Serializer):
    new_status = serializers.ChoiceField(choices=STATUS_CHOISES)

    def validate(self, attrs):
        attrs['new_status']


class OrderOwnerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'id', 'user', 'product', 'created_at',
            'updated_at', 'status', 'address'
        )
