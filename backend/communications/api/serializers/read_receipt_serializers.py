from __future__ import annotations

from rest_framework import serializers

from communications.models.receipt import CommunicationReadReceipt


class CommunicationReadReceiptSerializer(serializers.ModelSerializer):
    """
    Read serializer for communication read receipts.
    """

    user_display = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationReadReceipt
        fields = [
            "id",
            "website",
            "thread",
            "message",
            "user",
            "user_display",
            "read_at",
        ]
        read_only_fields = fields

    def get_user_display(self, obj: CommunicationReadReceipt) -> str:
        """
        Return user display label.
        """
        if hasattr(obj.user, "get_full_name"):
            full_name = obj.user.get_full_name()
            if full_name:
                return full_name

        return getattr(obj.user, "email", str(obj.user))


class CommunicationUnreadCountSerializer(serializers.Serializer):
    """
    Serializer for unread count response.
    """

    unread_count = serializers.IntegerField()