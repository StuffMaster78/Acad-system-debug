from rest_framework.pagination import PageNumberPagination


class BasePagination(PageNumberPagination):
    """
    Standard pagination for all financial APIs.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response( # type: ignore
            self,
            data
        ):
        return {
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "page_size": self.get_page_size(self.request),
            "results": data,
        }
