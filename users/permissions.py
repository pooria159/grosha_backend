from rest_framework import permissions

class IsSellerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        return hasattr(request.user, 'seller')

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.seller == request.user.seller