from django.http import Http404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import generics, mixins, viewsets, status

from .models import Order
from .serializers import (OrderSerializer, OrderUpdateStatus,
                          OrderCancelSerializer, OrderConfirmSerializer)
from .permissions import IsAuthorOrOwner, IsOwner, IsAuthor


class OrderViewSet(mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Order.objects.all()

    def get_permissions(self):
        if self.request.method == 'PATCH':
            self.permission_classes = (IsOwner,)
        else:
            self.permission_classes = (IsAuthorOrOwner,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return OrderUpdateStatus
        elif self.action == 'destroy':
            return OrderCancelSerializer
        return OrderSerializer

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(
            order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        self.get_serializer(order)
        return Response({'message': f'Order on {order.product.title} was canceled'})

    def get_author_orders(self, request):
        author_orders = [order for order in self.get_queryset()
                         if order.user == request.user]
        return author_orders

    @action(['GET'], detail=False)
    def active(self, request, pk=None):
        active_orders = [order for order in self.get_author_orders(request)
                         if order.status not in ('CANCEL', 'COMPLETE')]

        serializer = self.get_serializer(active_orders, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(['GET'], detail=False)
    def history(self, request, pk=None):
        active_orders = [order for order in self.get_author_orders(request)
                         if order.status in ('CANCEL', 'COMPLETE')]

        serializer = self.get_serializer(active_orders, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class OrderOwnerList(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.all()

    def list(self, request, *args, **kwargs):
        owned_orders = [order for order in self.get_queryset()
                        if order.product.user == request.user]

        serializer = self.get_serializer(owned_orders, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class OrderConfirm(generics.RetrieveAPIView):
    serializer_class = OrderConfirmSerializer

    def get(self, request, activation_code):
        order = Order.objects.get(activation_code=activation_code)
        self.get_serializer(
            order, context={'confirm_on': 'PENDING', 'activation_code': activation_code})
        return Response({'message': f'Order on {order.product.title} confirmed'})


class OrderComplete(generics.RetrieveAPIView):
    serializer_class = OrderConfirmSerializer

    def get(self, request, activation_code):
        order = Order.objects.get(activation_code=activation_code)
        self.get_serializer(
            order, context={'confirm_on': 'DELIVER', 'activation_code': activation_code})
        return Response({'message': f'Order {order.product.title} completed'})
