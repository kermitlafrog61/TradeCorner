
from django.db import models
from django.contrib.auth import get_user_model

from apps.products.models import Product
from .units import STATUS_CHOISES

User = get_user_model()


class Order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=9, choices=STATUS_CHOISES, default='PENDING')
    address = models.CharField(max_length=128)