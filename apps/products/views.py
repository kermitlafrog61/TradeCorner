from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from apps.orders.serializers import OrderSerializer
from django.db.models import Q
from django.core.files.uploadedfile import SimpleUploadedFile

from .serializers import ProductSerializer
from .models import Product
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [IsAdminOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = ProductSerializer
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'order':
            return OrderSerializer
        return ProductSerializer

    def get_permissions(self):
        if self.action == 'POST':
            return [IsAuthenticated()]
        elif self.action in ['PUT', 'PATCH', 'DESTROY']:
            return [IsOwnerOrReadOnly()]
        else:
            return [AllowAny()]

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def order(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response({'message': f'Product {product.id} was ordered successfully'})

    def get_queryset(self):
        queryset = Product.objects.all()
        title = self.request.query_params.get('title')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if title:
            queryset = queryset.filter(title__icontains=title)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        return queryset
    
    @action(methods=['POST'], detail=True)
    def upload_image(self, request, pk=None):
        product = self.get_object()
        image_file = request.FILES.get('image', None)

        if image_file:
            content = image_file.read()
            image_name = image_file.name
            uploaded_file = SimpleUploadedFile(
                image_name, content, content_type='image/jpeg')
            product.image.save(image_name, uploaded_file, save=True)
            return Response({'message': f'Image {image_name} uploaded successfully'})
        else:
            return Response({'message': 'Image not provided'}, status=400)

    @action(methods=['GET'], detail=True)
    def download_image(self, request, pk=None):
        product = self.get_object()
        image_url = request.build_absolute_uri(product.image.url)
        return Response({'image_url': image_url})
