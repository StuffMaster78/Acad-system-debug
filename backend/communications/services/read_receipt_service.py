from communications.models import MessageReadReceipt
from django.utils import timezone

class ReadReceiptService:
    @staticmethod
    def mark_as_read(message, user):
        if message.recipient != user:
            return

        MessageReadReceipt.objects.get_or_create(
            message=message,
            user=user,
            defaults={"read_at": timezone.now()}
        )