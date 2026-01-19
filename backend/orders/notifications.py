import logging
from django.contrib.auth import get_user_model
from notifications_system.services.core import NotificationService
from orders.notification_emitters import emit_event
from orders.notification_context import build_order_context

logger = logging.getLogger(__name__)

def _notify_admins(event_key, order, *, extra=None):
    User = get_user_model()
    admins = User.objects.filter(is_staff=True, is_active=True)
    for admin in admins:
        try:
            NotificationService.send_notification(
                user=admin,
                event=event_key,
                payload=build_order_context(
                    event=event_key,
                    order=order,
                    actor=None,
                    viewer_role=getattr(admin, "role", None) or "admin",
                    meta=extra or {},
                ),
                website=order.website
            )
        except Exception as e:
            logger.error(f"Failed to notify admin for order {order.id}: {e}", exc_info=True)

def notify_writer_order_assigned(order):
    """
    Notify the writer that an order has been assigned to them.
    """
    try:
        emit_event("order.assigned", order=order, actor=None)
    except Exception as e:
        logger.error(f"Failed to notify writer for order {order.id}: {e}", exc_info=True)
    

def notify_admin_order_assigned(order):
    """
    Notify the admin that an order has been assigned to a writer.
    """
    try:
        _notify_admins("order.assigned", order)
    except Exception as e:
        logger.error(f"Failed to notify admin for order {order.id}: {e}", exc_info=True)

def notify_writer_missed_deadline(order):
    """
    Notify the writer that they have missed the deadline for an order.
    """
    try:
        emit_event("order.expired", order=order, actor=None, extra={"reason": "deadline_missed"})
    except Exception as e:
        logger.error(f"Failed to notify writer for missed deadline on order {order.id}: {e}", exc_info=True)


def notify_admin_missed_deadline(order):
    """
    Notify the admin that a writer has missed the deadline for an order.
    """
    try:
        _notify_admins("order.expired", order, extra={"reason": "deadline_missed"})
    except Exception as e:
        logger.error(f"Failed to notify admin for missed deadline on order {order.id}: {e}", exc_info=True)


def notify_writer_fined(order, fine_amount):
    """
    Notify the writer that they have been fined for missing a deadline.
    """
    try:
        emit_event("order.fined", order=order, actor=None, extra={"fine_amount": fine_amount})
    except Exception as e:
        logger.error(f"Failed to notify writer for fine on order {order.id}: {e}", exc_info=True)


def notify_client_writer_declined(order):
    """
    Notify the client that the writer has declined the order.
    """
    try:
        emit_event("order.preferred_writer_rejected", order=order, actor=None)
    except Exception as e:
        logger.error(f"Failed to notify client for writer decline on order {order.id}: {e}", exc_info=True)


def notify_admin_writer_declined(order):
    """
    Notify the admin that the writer has declined the order.
    """
    try:
        _notify_admins("order.preferred_writer_rejected", order, extra={"reason": "writer_declined"})
    except Exception as e:
        logger.error(f"Failed to notify admin for writer decline on order {order.id}: {e}", exc_info=True)  


def notify_client_order_completed(order):
    """
    Notify the client that their order has been completed.
    """
    try:
        emit_event("order.completed", order=order, actor=None)
    except Exception as e:
        logger.error(f"Failed to notify client for order completion {order.id}: {e}", exc_info=True)


def notify_admin_order_completed(order):
    """
    Notify the admin that an order has been completed.
    """
    try:
        _notify_admins("order.completed", order)
    except Exception as e:
        logger.error(f"Failed to notify admin for order completion {order.id}: {e}", exc_info=True)


def notify_client_order_cancelled(order):
    """
    Notify the client that their order has been cancelled.
    """
    try:
        emit_event("order.cancelled", order=order, actor=None)
    except Exception as e:
        logger.error(f"Failed to notify client for order cancellation {order.id}: {e}", exc_info=True)  


def notify_writer_order_cancelled(order):
    """
    Notify the writer that their order has been cancelled.
    """
    try:
        emit_event("order.cancelled", order=order, actor=None)
    except Exception as e:
        logger.error(f"Failed to notify writer for order cancellation {order.id}: {e}", exc_info=True)


def notify_writer_order_on_hold(order):
    """
    Notify the writer that their order is on hold.
    """
    try:
        emit_event("order.on_hold", order=order, actor=None)
    except Exception as e:
        logger.error(f"Failed to notify writer for order on hold {order.id}: {e}", exc_info=True )


def notify_client_order_on_hold(order):
    """
    Notify the client that their order is on hold.
    """
    try:
        emit_event("order.on_hold", order=order, actor=None)
    except Exception as e:
        logger.error(f"Failed to notify client for order on hold {order.id}: {e}", exc_info=True)



def notify_client_order_archived(order):
    """
    Notify the client that their order has been archived.
    """
    try:
        emit_event("order.archived", order=order, actor=None)
    except Exception as e:
        logger.error(f"Failed to notify client for order archived {order.id}: {e}", exc_info=True)


def notify_writer_order_archived(order):
    """
    Notify the writer that their order has been archived.
    """
    try:
        emit_event("order.archived", order=order, actor=None)
    except Exception as e:
        logger.error(f"Failed to notify writer for order archived {order.id}: {e}", exc_info=True)


def notify_admin_order_archived(order):
    """
    Notify the admin that an order has been archived.
    """
    try:
        _notify_admins("order.archived", order)
    except Exception as e:
        logger.error(f"Failed to notify admin for order archived {order.id}: {e}", exc_info=True)


def notify_writer_revision_requested(order, revision_details):
    """
    Notify the writer that a revision has been requested for their order.
    """
    try:
        emit_event("order.revision_requested", order=order, actor=None, extra={"revision_details": revision_details})
    except Exception as e:
        logger.error(f"Failed to notify writer for revision request on order {order.id}: {e}", exc_info=True)



def notify_client_revision_complete(order):
    """
    Notify the client that the revision for their order has been completed.
    """
    try:
        emit_event("order.revised", order=order, actor=None)
    except Exception as e:
        logger.error(f"Failed to notify client for revision completion {order.id}: {e}", exc_info=True)


def notify_admin_revision_requested(order, revision_details):
    """
    Notify the admin that a revision has been requested for an order.
    """
    try:
        _notify_admins("order.revision_requested", order, extra={"revision_details": revision_details})
    except Exception as e:
        logger.error(f"Failed to notify admin for revision request on order {order.id}: {e}", exc_info=True)


def notify_writer_order_disputed(order):
    """
    Notify the writer that their order has been disputed.
    """
    try:
        emit_event("order.disputed", order=order, actor=None)
    except Exception as e:
        logger.error(f"Failed to notify writer for order dispute {order.id}: {e}", exc_info=True)


def notify_client_order_disputed(order):
    """
    Notify the client that their order has been disputed.
    """
    try:
        emit_event("order.disputed", order=order, actor=None)
    except Exception as e:
        logger.error(f"Failed to notify client for order dispute {order.id}: {e}", exc_info=True)


def notify_admin_order_disputed(order):
    """
    Notify the admin that an order has been disputed.
    """
    try:
        _notify_admins("order.disputed", order)
    except Exception as e:
        logger.error(f"Failed to notify admin for order dispute {order.id}: {e}", exc_info=True)