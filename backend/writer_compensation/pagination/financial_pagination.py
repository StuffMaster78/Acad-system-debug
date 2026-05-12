from writer_compensation.pagination.base import BasePagination


class FinancialPagination(BasePagination):
    """
    Pagination tuned for financial data.

    Slightly more conservative defaults because:
    - settlement queries can be heavy
    - ledger + event logs grow fast
    """

    page_size = 25
    max_page_size = 50