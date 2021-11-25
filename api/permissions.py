from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owners of an object to:
    view, edit, update or delete
    """

    # for view permission
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    # for object level permission
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsUserOwner(permissions.BasePermission):
    """
    Permission to only allow user to edit own information:
    view, edit, update or delete
    """

    # for view permission
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    # for object level permission
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user


class IsCreatedBy(permissions.BasePermission):
    """
    Permission to only allow creator of an object to:
    view
    """

    # for view permission
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    # for object level permission
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user
