"""Shared permissions and pagination used across all view modules."""
from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination


class IsSuperUser(permissions.BasePermission):
    """Grants access only to superuser accounts."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
