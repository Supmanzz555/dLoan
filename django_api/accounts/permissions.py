from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == "admin" or request.user.is_super_admin
        )


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_super_admin


class IsReviewer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ("reviewer", "admin") or request.user.is_super_admin
        )
