from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import ProductSerializer
from .models import Product
from .permissions import IsAuthor
from apps.orders.serializers import OrderSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (IsAuthenticated,)
        elif self.request.method in ('PUT', 'PATCH', 'DESTROY'):
            self.permission_classes = (IsAuthor,)
        else:
            self.permission_classes = (AllowAny,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'order':
            return OrderSerializer
        return ProductSerializer

    @action(methods=['POST'], detail=True)
    def order(self, request, pk=None):
        product = self.get_object()
        serilizer = self.get_serializer(data=request.data, context={'request': request})
        serilizer.is_valid(raise_exception=True)
        serilizer.save(product=product)
        return Response({'message': f'Product {product.id} was ordered succesfully'})
