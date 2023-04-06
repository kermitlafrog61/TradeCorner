from rest_framework import permissions, generics, mixins, viewsets

from .models import Order
from .serializers import OrderSerializer, OrderUpdateStatus
from .permissions import IsAuthorOrOwner, IsOwner


class OrderViewSet(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Order.objects.all()
    permission_classes = (IsAuthorOrOwner,)

    def get_serializer_class(self):
        if self.action == 'update':
            return OrderUpdateStatus
        return OrderSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)


class OrderOwnerList(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsOwner,)