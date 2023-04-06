from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, OrderConfirm, OrderComplete

router = DefaultRouter()
router.register('orders', OrderViewSet, 'orders')

urlpatterns = [
    path('orders/<int:pk>/confirm/', OrderConfirm.as_view(), name='confirm'),
    path('orders/<int:pk>/complete/', OrderComplete.as_view(), name='complete'),
]

urlpatterns += router.urls
