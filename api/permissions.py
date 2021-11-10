from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owners of an object to:
    view, edit, update or delete
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # view, edit, update or delete permissions only allowed to owner
        return obj.owner == request.user


class IsUserOwner(permissions.BasePermission):
    """
    Permission to only allow user to edit own information:
    view, edit, update or delete
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.id == request.user.id


class IsCreatedBy(permissions.BasePermission):
    """
    Permission to only allow creator of an object to:
    view
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # view, edit, update or delete permissions only allowed to owner
        return obj.created_by == request.user
