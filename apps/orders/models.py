from django.db import models
from django.contrib.auth import get_user_model

from apps.products.models import Product

User = get_user_model()


class Order(models.Model):
    STATUS_CHOISES = (
        ('PENDING', 'Pending'),
        ('PROCESS', 'Processing'),
        ('SHIP', 'Shipping'),
        ('DELIVER', 'Delivered'),
        ('COMPLETE', 'Completed'),
        ('CANCEL', 'Canceled')
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=9, choices=STATUS_CHOISES, default='PENDING')
    address = models.CharField(max_length=128)
    activation_code = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self) -> str:
        return f'Заказ от {self.user} на {self.product}'
    
