from rest_framework.permissions import BasePermission


class IsTaskOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        profile = getattr(request.user, "profile", None)
        return obj.user == request.user.profile
