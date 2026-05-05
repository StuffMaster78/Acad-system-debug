from __future__ import annotations

from rest_framework.pagination import CursorPagination
from rest_framework.pagination import PageNumberPagination


class CommunicationMessageCursorPagination(CursorPagination):
    """
    Cursor pagination for thread messages.
    """

    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 100
    ordering = "created_at"


class CommunicationDefaultPagePagination(PageNumberPagination):
    """
    Default pagination for admin lists.
    """

    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200