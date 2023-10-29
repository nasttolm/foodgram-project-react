from rest_framework import permissions


class AuthorAdminOrReadOnly(permissions.BasePermission):
    """Разрешение только для автора или только на чтение."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return any([request.method in permissions.SAFE_METHODS,
                   obj.author == request.user,
                   request.user.is_staff])
