from django.db.models import Q
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from apps.orders.serializers import OrderSerializer
from .serializers import ProductSerializer, CommentSerializer, RatingSerializer, LikeSerializer
from .models import Product, Comment, Like
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    pagination_class = CustomPagination
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        image_file = request.FILES.get('image')
        if image_file:
            serializer.instance.image = image_file
            serializer.instance.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)   

    def get_serializer_class(self):
        if self.action == 'order':
            return OrderSerializer
        elif self.action == 'rate':
            return RatingSerializer
        elif self.action == 'comment_create':
            return CommentSerializer
        elif self.action == 'like':
            return None
        return ProductSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return (IsAuthenticated(),)
        elif self.request.method in ['PUT', 'PATCH', 'DESTROY']:
            return [IsOwnerOrReadOnly()]
        else:
            return [AllowAny()]

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated]) # GET FROM ISLAM
    def order(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response({'message': f'Product {product.id} was ordered successfully'})

    def get_queryset(self):  # TODO FILTERING
        queryset = Product.objects.all()
        title = self.request.query_params.get('title')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        return queryset

    def create(self, request, *args, **kwargs):
        product = super().create(request, *args, **kwargs)
        image_file = request.FILES.get('image', None)

        if image_file:
            content = image_file.read()
            image_name = image_file.title
            uploaded_file = SimpleUploadedFile(
                image_name, content, content_type='image/jpeg')
            product.image.save(image_name, uploaded_file, save=True)

        return Response({'message': f'Product created'}, status=status.HTTP_201_CREATED)

    @action(methods=['GET'], detail=True)
    def download_image(self, request, pk=None):
        product = self.get_object()
        image_url = request.build_absolute_uri(product.image.url)
        return Response({'image_url': image_url})

    @action(methods=['POST'], detail=True, url_path='comment')
    def comment_create(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['DELETE'], detail=True, url_path='comment/(?P<comment_id>\d+)')
    def comment_delete(self, request, pk=None, comment_id=None):
        try:
            comment = Comment.objects.filter(product=pk).get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST'], detail=True)
    def rate(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(data=request.data, context={
                                      'request': request, 'product': product})
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def like(self, request, pk=None) -> None:
        product = self.get_object()
        like = Like.objects.filter(user=request.user, product=product)
        if like.exists():
            like.delete()
            return Response({'liked': False})
        else:
            Like.objects.create(user=request.user, product=product).save()
            return Response({'liked': True})
