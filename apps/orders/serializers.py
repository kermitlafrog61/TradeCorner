from rest_framework import serializers

from apps.products.serializers import ProductSerializer
from .models import Order
from .tasks import send_order_created, send_updated_status, send_cancel_status
from .utils import create_activation_code


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = (
            'id', 'user', 'product', 'created_at',
            'updated_at', 'status', 'address')
        read_only_fields = (
            'id', 'user', 'product', 'created_at',
            'updated_at', 'status')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['product'] = ProductSerializer(instance.product).data
        rep['user'] = instance.user.username
        return rep

    def validate(self, attrs):
        user = attrs['user']
        product = self.context['product']
        if user == product.user:
            raise serializers.ValidationError("You can't order from yourserlf")
        elif Order.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("You can't order twice")

        attrs['product'] = product
        return attrs

    def create(self, validated_data):
        order = super().create(validated_data)
        create_activation_code(order)
        send_order_created.delay(order.id)
        return order


class OrderUpdateStatus(serializers.ModelSerializer):
    UPDATE_STATUS_CHOISES = (
        ('SHIP', 'Shipping'),
        ('DELIVER', 'Delivered'),
    )

    status = serializers.ChoiceField(choices=UPDATE_STATUS_CHOISES)

    class Meta:
        model = Order
        fields = ('status',)

    def validate(self, attrs):
        order_status = self.instance.status
        if self.instance.status in ('CANCEL', 'COMPLETE'):
            raise serializers.ValidationError(
                'You cannot update finished order')

        elif order_status == attrs['status']:
            raise serializers.ValidationError(
                f'Order in already {order_status}')
        return attrs

    def save(self, **kwargs):
        order = super().save(**kwargs)
        send_updated_status.delay(order.id)
        order.save()
        return order


class OrderCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',)

    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)
        order = self.instance
        if order.status in ('CANCEL', 'COMPLETE'):
            raise serializers.ValidationError(
                {'detail': 'You cannot cancel finished order'})

        send_cancel_status.delay(order.id, self.context['request'].user.id)
        order.status = 'CANCEL'
        order.save()


class OrderConfirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',)

    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)
        order = self.instance
        confirm_on = self.context['confirm_on']

        if order.activation_code != self.context['activation_code']:
            raise serializers.ValidationError(
                {'detail': 'Activation code is not correct'})

        order.activation_code = ''

        if confirm_on == 'PENDING':
            order.status = 'PROCESS'
        else:
            order.status = 'COMPLETE'
        order.save()
