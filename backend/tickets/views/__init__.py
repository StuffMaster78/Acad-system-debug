from tickets.api.views import (
    TicketFileViewSet,
    TicketLogViewSet,
    TicketMessageViewSet,
    TicketPagination,
    TicketSLAViewSet,
    TicketStatisticsViewSet,
    TicketViewSet,
)

TicketAttachmentViewSet = TicketFileViewSet


def notify_user(*args, **kwargs):
    """
    Backwards-compatible test hook for older imports.
    """
    return True


__all__ = [
    "TicketAttachmentViewSet",
    "TicketFileViewSet",
    "TicketLogViewSet",
    "TicketMessageViewSet",
    "TicketPagination",
    "TicketSLAViewSet",
    "TicketStatisticsViewSet",
    "TicketViewSet",
    "notify_user",
]
