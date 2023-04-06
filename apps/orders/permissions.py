from rest_framework.permissions import BasePermission


class IsAuthorOrOwner(BasePermission):
    def has_object_permission(self, request, view, order):
        return bool((request.user == order.user or
                     request.user == order.product.user) and
                    request.user.is_authenticated)


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, order):
        return bool(request.user == order.product.user and
                    request.user.is_authenticated)
