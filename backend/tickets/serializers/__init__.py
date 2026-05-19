from tickets.api.serializers import *

TicketSerializer = TicketDetailSerializer
TicketAttachmentSerializer = TicketFileSerializer

__all__ = [
    *[name for name in globals() if name.endswith("Serializer")],
]
