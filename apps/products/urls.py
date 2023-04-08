from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryList

router = DefaultRouter()
router.register('products', ProductViewSet, basename='products')

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', CategoryList.as_view()),
]
