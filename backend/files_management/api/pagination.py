from rest_framework.pagination import PageNumberPagination


class FilePageNumberPagination(PageNumberPagination):
    """
    Default pagination for file management endpoints.
    """

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100