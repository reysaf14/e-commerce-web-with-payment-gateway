"""Custom permission classes."""
from rest_framework.permissions import BasePermission


class IsMerchant(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == "merchant"


class IsStoreOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return hasattr(request.user, "store_settings") and obj.store == request.user.store_settings
