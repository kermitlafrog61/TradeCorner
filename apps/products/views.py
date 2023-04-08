from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status, generics, viewsets
from django_filters.rest_framework.backends import DjangoFilterBackend

from apps.orders.serializers import OrderSerializer
from .serializers import (ProductSerializer, CommentSerializer, ProductListSerializer,
                          CategorySerializer, RatingSerializer, LikeSerializer)
from .models import Product, Comment, Like, Category
from .permissions import IsAuthor
from .parsers import ProductParser


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    parser_classes = (ProductParser,)
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['categories']
    search_fields = ['title', 'description']
    ordering_fields = ['ratings', 'created_at', 'price']

    def get_serializer_class(self):
        serializer_classes = {
            'list': ProductListSerializer,
            'order': OrderSerializer,
            'rate': RatingSerializer,
            'comment_create': CommentSerializer,
            'like': LikeSerializer,
        }
        return serializer_classes.get(self.action, ProductSerializer)

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DESTROY']:
            return (IsAuthor(),)
        else:
            return (IsAuthenticatedOrReadOnly(),)

    @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60*60))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @method_decorator(vary_on_cookie)
    @method_decorator(cache_page(60*60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(['GET'], detail=False)
    def recommendation(self, request):
        queryset = (self.get_queryset()
                    .annotate(orders_count=Count('orders'))
                    .order_by('-orders_count', 'ratings'))[:5]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(['POST'], detail=True)
    def order(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(
            data=request.data, context={'request': request, 'product': product})
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(
            {'message': f'Product {product.title} was ordered successfully'},
            status=status.HTTP_201_CREATED)

    @action(['POST'], detail=True, url_path='comment')
    def comment_create(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(['DELETE'], detail=True, url_path='comment/(?P<comment_id>\d+)')
    def comment_delete(self, request, pk=None, comment_id=None):
        try:
            comment = Comment.objects.filter(product=pk).get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['POST'], detail=True)
    def rate(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(data=request.data, context={
            'request': request, 'product': product})
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data)

    @action(['POST'], detail=True)
    def like(self, request, pk=None) -> None:
        product = self.get_object()
        serializer = self.get_serializer(request.user, product)
        return Response(serializer.data)


class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class FavoritesList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProductSerializer

    def get_queryset(self):
        likes = (Like.objects
                 .filter(user=self.request.user)
                 .values_list('product'))
        products = Product.objects.filter(id__in=likes)
        return products
