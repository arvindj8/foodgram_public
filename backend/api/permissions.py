from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Доступ юзерам с правами админа. Неавторизованным только чтение"""
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_superuser)


class IsAuthor(permissions.BasePermission):
    """Доступ для автора или чтение."""
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)


class IsAdmin(permissions.BasePermission):
    """Доступ только для админа"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
