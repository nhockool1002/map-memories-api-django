from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Only allow access to the owner of the object
        return obj.user == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """

    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and hasattr(request.user, 'is_admin')
            and request.user.is_admin
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read access to anyone,
    but only admin users can write.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return (
            request.user 
            and request.user.is_authenticated 
            and hasattr(request.user, 'is_admin')
            and request.user.is_admin
        )


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read access to anyone,
    but write access only to authenticated users.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_authenticated


class IsOwnerOrPublicReadOnly(permissions.BasePermission):
    """
    Custom permission for memories and locations:
    - Owner can do everything
    - Others can only read if object is public
    """

    def has_object_permission(self, request, view, obj):
        # Owner can do everything
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Others can only read public objects
        if request.method in permissions.SAFE_METHODS:
            # For memories, check is_public field
            if hasattr(obj, 'is_public'):
                return obj.is_public
            # For other objects, allow read access
            return True
        
        # No write access for non-owners
        return False


class CanViewMemoryPermission(permissions.BasePermission):
    """
    Permission for viewing memories:
    - Owner can always view
    - Others can view only if memory is public
    """
    
    def has_object_permission(self, request, view, obj):
        # Owner can always view
        if obj.user == request.user:
            return True
        
        # Others can only view if public
        return obj.is_public if hasattr(obj, 'is_public') else False


class CanModifyMemoryPermission(permissions.BasePermission):
    """
    Permission for modifying memories:
    - Only owner can modify
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user