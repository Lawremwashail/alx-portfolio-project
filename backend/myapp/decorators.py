from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Permission for admin users only.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'admin':
            return True
        return False

class IsUserOrAdmin(BasePermission):
    def has_permission(self, request, view):
        # Admins have permission to access all
        if request.user.role == 'admin':
            return True
        # Users can only access their associated admin's sales
        if request.user.role == 'user' and request.user.created_by:
            return True
        return False
