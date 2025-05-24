from orders.utils.order_utils import get_orders_by_status_older_than, save_order


class ArchiveService:
    """
    Service for archiving orders.
    """

    @staticmethod
    def archive_orders_older_than(cutoff_date):
        """
        Archive 'approved' orders older than cutoff_date.
        """
        orders = get_orders_by_status_older_than('approved', cutoff_date)
        for order in orders:
            order.status = 'archived'
            save_order(order)