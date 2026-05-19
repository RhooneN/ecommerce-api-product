# shared/simple_permissions.py
        
  # products/permissions.py
from rest_framework.permissions import BasePermission
from rest_framework import permissions
class IsAdmin(BasePermission):
    """
    Allows access only to users with is_admin=True in JWT.
    """
    def has_permission(self, request, view):
        return bool(
            request.user 
            and getattr(request.user, "is_admin", False) is True
        )
        
class IsAuth(BasePermission):
    """
    Allows access only to authenticated users (with user_id and username).
    """
    def has_permission(self, request, view):
        return bool(
            request.user 
            and getattr(request.user, "user_id", None) 
            and getattr(request.user, "username", None)
        )


class IsAuthOrReadOnly(BasePermission):
    """Allow read access to anyone, write access to authenticated users"""
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return getattr(request.user, 'user_id', None) is not None
        
class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins to edit, but anyone to read.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only allowed to admin users
        return request.user and getattr(request.user, 'is_admin', False)
        


