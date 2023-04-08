from rest_framework.permissions import BasePermission


class IsAuthorOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool((
            request.user == obj.user or
            request.user == obj.product.user) and
            request.user.is_authenticated)


class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user == obj.user and
            request.user.is_authenticated)


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user == obj.product.user and
            request.user.is_authenticated)
