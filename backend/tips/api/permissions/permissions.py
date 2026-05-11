from rest_framework.permissions import BasePermission


class IsTipParticipant(BasePermission):
    """
    Allows access only to sender or receiver of a tip.
    """

    def has_object_permission(self, request, view, obj):
        return obj.sender_id == request.user.id or obj.receiver_id == request.user.id