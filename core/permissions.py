from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """Allow owners to edit, everyone else read-only."""

    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj == request.user or getattr(obj, 'user', None) == request.user


class IsNotGuest(BasePermission):
    """Block guest users from certain actions."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and not getattr(request.user, 'is_guest', False)
