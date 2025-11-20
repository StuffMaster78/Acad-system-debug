from notifications_system.enums import NotificationType
from notifications_system.tasks import async_send_notification
import logging

logger = logging.getLogger(__name__)

def notify_writer_order_assigned(order):
    """
    Notify the writer that an order has been assigned to them.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the writer's user object
        writer = User.objects.get(id=order.writer_id)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"You have been assigned to Order #{order.id}: {order.title}.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch the notification asynchronously
        async_send_notification(
            user_id=writer.id,
            event="order_assigned",
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
        )
        
    except User.DoesNotExist:
        logger.error(f"Writer with ID {order.writer_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to notify writer for order {order.id}: {e}", exc_info=True)
    async_send_notification(
           user_id=writer.id,
           event="order_assigned",
           payload=payload,
           channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
       )
    

def notify_admin_order_assigned(order):
    """
    Notify the admin that an order has been assigned to a writer.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get all active admins
        admins = User.objects.filter(is_staff=True, is_active=True)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"Order #{order.id} has been assigned to a writer.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch notifications to all admins asynchronously
        for admin in admins:
            async_send_notification(
                user_id=admin.id,
                event="order_assigned",
                payload=payload,
                channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
            )
            
    except Exception as e:
        logger.error(f"Failed to notify admin for order {order.id}: {e}", exc_info=True)

def notify_writer_missed_deadline(order):
    """
    Notify the writer that they have missed the deadline for an order.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the writer's user object
        writer = User.objects.get(id=order.writer_id)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"You have missed the deadline for Order #{order.id}: {order.title}.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch the notification asynchronously
        async_send_notification(
            user_id=writer.id,
            event="missed_deadline",
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
        )
        
    except User.DoesNotExist:
        logger.error(f"Writer with ID {order.writer_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to notify writer for missed deadline on order {order.id}: {e}", exc_info=True)    


def notify_admin_missed_deadline(order):
    """
    Notify the admin that a writer has missed the deadline for an order.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get all active admins
        admins = User.objects.filter(is_staff=True, is_active=True)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"Writer has missed the deadline for Order #{order.id}.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch notifications to all admins asynchronously
        for admin in admins:
            async_send_notification(
                user_id=admin.id,
                event="missed_deadline",
                payload=payload,
                channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
            )
            
    except Exception as e:
        logger.error(f"Failed to notify admin for missed deadline on order {order.id}: {e}", exc_info=True)


def notify_writer_fined(order, fine_amount):
    """
    Notify the writer that they have been fined for missing a deadline.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the writer's user object
        writer = User.objects.get(id=order.writer_id)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"You have been fined ${fine_amount} for missing the deadline on Order #{order.id}: {order.title}.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch the notification asynchronously
        async_send_notification(
            user_id=writer.id,
            event="fined",
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
        )
        
    except User.DoesNotExist:
        logger.error(f"Writer with ID {order.writer_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to notify writer for fine on order {order.id}: {e}", exc_info=True )


def notify_client_writer_declined(order):
    """
    Notify the client that the writer has declined the order.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the client's user object
        client = User.objects.get(id=order.client_id)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"The writer has declined your Order #{order.id}: {order.title}.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch the notification asynchronously
        async_send_notification(
            user_id=client.id,
            event="writer_declined",
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
        )
        
    except User.DoesNotExist:
        logger.error(f"Client with ID {order.client_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to notify client for writer decline on order {order.id}: {e}", exc_info=True )


def notify_admin_writer_declined(order):
    """
    Notify the admin that the writer has declined the order.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get all active admins
        admins = User.objects.filter(is_staff=True, is_active=True)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"The writer has declined Order #{order.id}.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch notifications to all admins asynchronously
        for admin in admins:
            async_send_notification(
                user_id=admin.id,
                event="writer_declined",
                payload=payload,
                channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
            )
            
    except Exception as e:
        logger.error(f"Failed to notify admin for writer decline on order {order.id}: {e}", exc_info=True)  


def notify_client_order_completed(order):
    """
    Notify the client that their order has been completed.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the client's user object
        client = User.objects.get(id=order.client_id)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"Your Order #{order.id}: {order.title} has been completed.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch the notification asynchronously
        async_send_notification(
            user_id=client.id,
            event="order_completed",
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
        )
        
    except User.DoesNotExist:
        logger.error(f"Client with ID {order.client_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to notify client for order completion {order.id}: {e}", exc_info=True)


def notify_admin_order_completed(order):
    """
    Notify the admin that an order has been completed.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get all active admins
        admins = User.objects.filter(is_staff=True, is_active=True)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"Order #{order.id} has been completed.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch notifications to all admins asynchronously
        for admin in admins:
            async_send_notification(
                user_id=admin.id,
                event="order_completed",
                payload=payload,
                channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
            )
            
    except Exception as e:
        logger.error(f"Failed to notify admin for order completion {order.id}: {e}", exc_info=True)


def notify_client_order_cancelled(order):
    """
    Notify the client that their order has been cancelled.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the client's user object
        client = User.objects.get(id=order.client_id)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"Your Order #{order.id}: {order.title} has been cancelled.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch the notification asynchronously
        async_send_notification(
            user_id=client.id,
            event="order_cancelled",
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
        )
        
    except User.DoesNotExist:
        logger.error(f"Client with ID {order.client_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to notify client for order cancellation {order.id}: {e}", exc_info=True)  


def notify_writer_order_cancelled(order):
    """
    Notify the writer that their order has been cancelled.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the writer's user object
        writer = User.objects.get(id=order.writer_id)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"Order #{order.id}: {order.title} has been cancelled.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch the notification asynchronously
        async_send_notification(
            user_id=writer.id,
            event="order_cancelled",
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
        )
        
    except User.DoesNotExist:
        logger.error(f"Writer with ID {order.writer_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to notify writer for order cancellation {order.id}: {e}", exc_info=True)


def notify_writer_order_on_hold(order):
    """
    Notify the writer that their order is on hold.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the writer's user object
        writer = User.objects.get(id=order.writer_id)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"Your Order #{order.id}: {order.title} is currently on hold.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch the notification asynchronously
        async_send_notification(
            user_id=writer.id,
            event="order_on_hold",
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
        )
        
    except User.DoesNotExist:
        logger.error(f"Writer with ID {order.writer_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to notify writer for order on hold {order.id}: {e}", exc_info=True )


def notify_client_order_on_hold(order):
    """
    Notify the client that their order is on hold.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the client's user object
        client = User.objects.get(id=order.client_id)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"Your Order #{order.id}: {order.title} is currently on hold. Please check with the support team for resolution.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch the notification asynchronously
        async_send_notification(
            user_id=client.id,
            event="order_on_hold",
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
        )
        
    except User.DoesNotExist:
        logger.error(f"Client with ID {order.client_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to notify client for order on hold {order.id}: {e}", exc_info=True)



def notify_client_order_archived(order):
    """
    Notify the client that their order has been archived.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the client's user object
        client = User.objects.get(id=order.client_id)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"Your Order #{order.id}: {order.title} has been archived.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch the notification asynchronously
        async_send_notification(
            user_id=client.id,
            event="order_archived",
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
        )
        
    except User.DoesNotExist:
        logger.error(f"Client with ID {order.client_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to notify client for order archived {order.id}: {e}", exc_info=True)


def notify_writer_order_archived(order):
    """
    Notify the writer that their order has been archived.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the writer's user object
        writer = User.objects.get(id=order.writer_id)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"Your Order #{order.id}: {order.title} has been archived.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch the notification asynchronously
        async_send_notification(
            user_id=writer.id,
            event="order_archived",
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
        )
        
    except User.DoesNotExist:
        logger.error(f"Writer with ID {order.writer_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to notify writer for order archived {order.id}: {e}", exc_info=True)


def notify_admin_order_archived(order):
    """
    Notify the admin that an order has been archived.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get all active admins
        admins = User.objects.filter(is_staff=True, is_active=True)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"Order #{order.id} has been archived.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch notifications to all admins asynchronously
        for admin in admins:
            async_send_notification(
                user_id=admin.id,
                event="order_archived",
                payload=payload,
                channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
            )
            
    except Exception as e:
        logger.error(f"Failed to notify admin for order archived {order.id}: {e}", exc_info=True)


def notify_writer_revision_requested(order, revision_details):
    """
    Notify the writer that a revision has been requested for their order.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the writer's user object
        writer = User.objects.get(id=order.writer_id)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"A revision has been requested for Order #{order.id}: {order.title}. Details: {revision_details}",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch the notification asynchronously
        async_send_notification(
            user_id=writer.id,
            event="revision_requested",
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
        )
        
    except User.DoesNotExist:
        logger.error(f"Writer with ID {order.writer_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to notify writer for revision request on order {order.id}: {e}", exc_info=True)



def notify_client_revision_complete(order):
    """
    Notify the client that the revision for their order has been completed.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the client's user object
        client = User.objects.get(id=order.client_id)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"The revision for your Order #{order.id}: {order.title} has been completed.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch the notification asynchronously
        async_send_notification(
            user_id=client.id,
            event="revision_complete",
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
        )
        
    except User.DoesNotExist:
        logger.error(f"Client with ID {order.client_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to notify client for revision completion {order.id}: {e}", exc_info=True)


def notify_admin_revision_requested(order, revision_details):
    """
    Notify the admin that a revision has been requested for an order.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get all active admins
        admins = User.objects.filter(is_staff=True, is_active=True)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"A revision has been requested for Order #{order.id}. Details: {revision_details}",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch notifications to all admins asynchronously
        for admin in admins:
            async_send_notification(
                user_id=admin.id,
                event="revision_requested",
                payload=payload,
                channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
            )
            
    except Exception as e:
        logger.error(f"Failed to notify admin for revision request on order {order.id}: {e}", exc_info=True)


def notify_writer_order_disputed(order):
    """
    Notify the writer that their order has been disputed.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the writer's user object
        writer = User.objects.get(id=order.writer_id)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"Your Order #{order.id}: {order.title} has been disputed.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch the notification asynchronously
        async_send_notification(
            user_id=writer.id,
            event="order_disputed",
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
        )
        
    except User.DoesNotExist:
        logger.error(f"Writer with ID {order.writer_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to notify writer for order dispute {order.id}: {e}", exc_info=True)


def notify_client_order_disputed(order):
    """
    Notify the client that their order has been disputed.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the client's user object
        client = User.objects.get(id=order.client_id)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"Your Order #{order.id}: {order.title} has been disputed.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch the notification asynchronously
        async_send_notification(
            user_id=client.id,
            event="order_disputed",
            payload=payload,
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
        )
        
    except User.DoesNotExist:
        logger.error(f"Client with ID {order.client_id} does not exist.")
    except Exception as e:
        logger.error(f"Failed to notify client for order dispute {order.id}: {e}", exc_info=True)


def notify_admin_order_disputed(order):
    """
    Notify the admin that an order has been disputed.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get all active admins
        admins = User.objects.filter(is_staff=True, is_active=True)
        
        # Prepare notification payload
        payload = {
            "order_id": order.id,
            "order_title": order.title,
            "message": f"Order #{order.id} has been disputed.",
            "order_status": order.status,
            "link": f"/orders/{order.id}/details/"
        }
        
        # Dispatch notifications to all admins asynchronously
        for admin in admins:
            async_send_notification(
                user_id=admin.id,
                event="order_disputed",
                payload=payload,
                channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET]
            )
            
    except Exception as e:
        logger.error(f"Failed to notify admin for order dispute {order.id}: {e}", exc_info=True)