from rest_framework.pagination import CursorPagination, PageNumberPagination

class SuperadminPagination(PageNumberPagination):
    """Default pagination for Superadmin APIs."""
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class SuperadminLogCursorPagination(CursorPagination):
    """Optimized pagination for large log data."""
    page_size = 15  # Adjust as needed
    ordering = "-timestamp"  # Ensures newest logs are shown first