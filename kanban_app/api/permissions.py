from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    """
    Nur der Besitzer eines Objekts darf es bearbeiten.
    Lesen (GET, HEAD, OPTIONS) ist für alle Authentifizierten erlaubt.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user
