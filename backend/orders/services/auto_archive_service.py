from orders.utils.order_utils import get_orders_by_status_older_than
from orders.services.transition_helper import OrderTransitionHelper
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class AutoArchiveService:
    """
    Service for archiving orders older than a cutoff date.
    """

    @staticmethod
    @transaction.atomic
    def archive_orders_older_than(cutoff_date, status="approved", website=None, user=None):
        """
        Archive orders with a given status older than the cutoff date.

        Args:
            cutoff_date (datetime): Archive orders older than this.
            status (str): Order status to target. Default is 'approved'.
            website (Website, optional): Scope to a specific tenant.
            user (User, optional): User performing the archiving (for logging).
        
        Returns:
            dict: Summary of archived orders.
        """
        try:
            # Get orders by status and date
            orders = get_orders_by_status_older_than(status, cutoff_date)
            # Filter by website if provided
            if website:
                orders = orders.filter(website=website)
            count = 0

            for order in orders:
                try:
                    OrderTransitionHelper.transition_order(
                        order=order,
                        target_status="archived",
                        user=user,
                        reason=f"Auto-archived: order older than {cutoff_date.isoformat()}",
                        action="auto_archive",
                        is_automatic=True,
                        metadata={
                            "cutoff_date": cutoff_date.isoformat(),
                            "previous_status": status,
                        }
                    )
                    count += 1
                except Exception as e:
                    logger.warning(f"Failed to archive order #{order.id}: {e}")
                    continue

            logger.info(f"Archived {count} '{status}' orders older than {cutoff_date}")
            return {
                "archived_count": count,
                "status": status,
                "cutoff": cutoff_date.isoformat(),
            }

        except Exception as e:
            logger.exception("Error during auto-archiving orders.")
            raise  # Let upstream handle it