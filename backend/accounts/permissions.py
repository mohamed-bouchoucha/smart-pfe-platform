from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Allow access only to users with admin role."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsSupervisor(BasePermission):
    """Allow access only to users with supervisor role."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'supervisor'


class IsStudent(BasePermission):
    """Allow access only to users with student role."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'


class IsAdminOrSupervisor(BasePermission):
    """Allow access to admins and supervisors."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('admin', 'supervisor')


class IsAdminOrReadOnly(BasePermission):
    """Allow read access to all authenticated users, write access to admins only."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAdminOrSupervisorOrReadOnly(BasePermission):
    """Read access to all, write access to admins and supervisors."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role in ('admin', 'supervisor')


class IsOwnerOrAdmin(BasePermission):
    """Object-level: allow owner or admin."""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return getattr(obj, 'user', None) == request.user or getattr(obj, 'created_by', None) == request.user
