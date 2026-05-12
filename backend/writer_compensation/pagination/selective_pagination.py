from writer_compensation.pagination.base import BasePagination


class LightweightPagination(BasePagination):
    """
    For dashboards and real-time views.
    """

    page_size = 10
    max_page_size = 20
