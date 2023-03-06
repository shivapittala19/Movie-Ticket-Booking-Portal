from rest_framework.permissions import BasePermission

class ISTheaterOwner(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return bool(request.user and request.user.is_theater_owner or request.user.is_staff)
