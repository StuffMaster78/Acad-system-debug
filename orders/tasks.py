from celery import shared_task
from core.utils.notifications import send_notification
from django.utils.timezone import now
from orders.models import Order
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
import logging
from django.utils import timezone
from orders.models import Order
from datetime import timedelta
from django.db.models import Avg, Count

from orders.services.archive_order_service import ArchiveOrderService
from orders.services.status_transition_service import StatusTransitionService

from orders.models import OrderRequest
from orders.order_enums import OrderRequestStatus
from orders.models import Order
from orders.order_enums import OrderStatus
from orders.workflow.state_machine import GenericStateMachineService
# from orders.models import OrderReview
from orders.services.order_request_service import OrderRequestService
from users.models import User
from websites.models import Website
from audit_logging.services import AuditLogEntry
from orders.models import WriterRequest
from audit_logging.services.audit_log_service import AuditLogService
from notifications_system.tasks import async_send_notification
from notifications_system.enums import NotificationType

logger = logging.getLogger(__name__)

@shared_task
def notify_writer(order_id):
    """
    Task to notify the assigned writer about an order.
    Sends an in-app notification and an email.
    """
    try:
        order = get_object_or_404(Order.objects.select_related('writer', 'client'), id=order_id)

        if not order.writer:
            logger.warning(f"No writer assigned for Order #{order.id}")
            return f"No writer assigned for Order #{order.id}"

        # In-app notification
        send_notification(
            user=order.writer,
            title="New Order Assigned",
            message=f"You have been assigned to Order #{order.id}: {order.topic}. Please check your dashboard."
        )

        # Email notification
        if order.writer.email:
            send_mail(
                subject="New Order Assignment",
                message=f"Dear {order.writer.username},\n\n"
                        f"You have been assigned a new order.\n\n"
                        f"Order ID: {order.id}\n"
                        f"Topic: {order.topic}\n\n"
                        f"Please log in to your dashboard to view the details.",
                from_email="no-reply@example.com",
                recipient_list=[order.writer.email],
                fail_silently=True
            )

        logger.info(f"Notification sent to writer {order.writer.email} for Order #{order.id}")
        return f"Notification sent to writer {order.writer.email} for Order #{order.id}"

    except Order.DoesNotExist:
        logger.error(f"Order with ID {order_id} does not exist.")
        return f"Order with ID {order_id} does not exist."

    except Exception as e:
        logger.error(f"Error in notify_writer task: {e}", exc_info=True)
        return f"Error in notify_writer task: {e}"
    


# Email notification to the client
@shared_task
def send_order_completion_email(client_email, client_username, order_id):
    """
    Sends an email to the client when their order is marked as completed.
    """
    try:
        subject = "Your Order is Completed!"
        message = f"Dear {client_username},\n\nYour order #{order_id} has been marked as completed."
        send_mail(
            subject, message, "no-reply@yourdomain.com", [client_email], fail_silently=True
        )
        logger.info(f"Order completion email sent to {client_email} for Order #{order_id}")
        return f"Order completion email sent to {client_email} for Order #{order_id}"

    except Exception as e:
        logger.error(f"Error sending order completion email: {e}", exc_info=True)
        return f"Error sending order completion email: {e}"
    

@shared_task
def release_stale_preferred_orders():
    """
    This task checks for orders that have been in the 'pending_preferred' status 
    for too long and moves them back to the public pool (status = 'available').

    This ensures that orders with no response from the preferred writer are 
    re-opened to the pool after a specified time.
    """
    stale_time = timedelta(hours=24)  # Orders older than 24 hours will be released

    # Find orders that are still in 'pending_preferred' and are stale
    stale_orders = Order.objects.filter(
        status='pending_preferred',
        created_at__lte=timezone.now() - stale_time
    )

    for order in stale_orders:
        order.status = 'available'  # Move to public pool
        order.preferred_writer = None  # Remove the preferred writer
        order.save()

        # Notify the client that their preferred writer did not respond
        if order.client.email:
            send_mail(
                subject="Preferred Writer Did Not Respond",
                message=f"Dear {order.client.username},\n\n"
                        f"Your preferred writer did not respond to the order request for Order #{order.id}."
                        f"The order is now available for other writers to take.\n\n"
                        f"Best regards,\nYour Team",
                from_email="no-reply@example.com",
                recipient_list=[order.client.email],
                fail_silently=True
            )

        logger.info(f"Released Order #{order.id} back to the public pool after {stale_time} hours.")
        
    print(f"Released {stale_orders.count()} stale preferred orders.")



@shared_task
def archive_approved_orders_task():
    """
    Archive orders that are in 'approved' state older than 2 weeks.
    """
    cutoff_date = now() - timedelta(weeks=2)
    ArchiveOrderService.archive_approved_orders_older_than(cutoff_date)


@shared_task
def move_complete_to_approved_task():
    """
    Move orders from 'complete' to 'approved' if they are older than 3 weeks.
    """
    cutoff_date = now() - timedelta(weeks=3)
    StatusTransitionService.move_complete_orders_to_approved_older_than(cutoff_date)



@shared_task
def expire_stale_requests():
    now = timezone.now()
    stale_requests = OrderRequest.objects.filter(
        status=OrderRequestStatus.PENDING,
        expires_at__lt=now
    )

    for request in stale_requests:
        request.status = OrderRequestStatus.EXPIRED
        request.rejection_feedback = "Request expired due to no response."
        request.save(update_fields=["status", "rejection_feedback"])


@shared_task
def archive_expired_orders():
    timeout_days = 3  # or from settings
    threshold = timezone.now() - timedelta(days=timeout_days)

    orders_to_archive = Order.objects.filter(
        status=OrderStatus.APPROVED,
        deadline__lt=threshold
    )

    for order in orders_to_archive:
        try:
            GenericStateMachineService.transition(
                order, target="archived",
                triggered_by="system"
            )
        except Exception as e:
            # log and skip
            print(f"Failed to archive order {order.id}: {e}")



# Monthly Writer Reviews
# @shared_task
# def generate_monthly_review_summary():
#     now = timezone.now()
#     month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#     month_end = (month_start + timezone.timedelta(days=32)).replace(day=1)

#     websites = Website.objects.all()

#     for site in websites:
#         reviews = OrderReview.objects.filter(
#             website=site,
#             created_at__gte=month_start,
#             created_at__lt=month_end,
#             status="approved"
#         )

#         summary = (
#             reviews
#             .values('writer_id')
#             .annotate(
#                 avg_rating=Avg('rating'),
#                 total_reviews=Count('id')
#             )
#         )

#         for item in summary:
#             writer_id = item['writer_id']
#             avg_rating = item['avg_rating']
#             total_reviews = item['total_reviews']

#             writer = User.objects.filter(id=writer_id).first()
#             if writer:
#                 AuditLogEntry.log(
#                     actor=None,
#                     target=writer,
#                     action="monthly_review_summary",
#                     website=site,
#                     metadata={
#                         "month": month_start.strftime("%B %Y"),
#                         "avg_rating": avg_rating,
#                         "total_reviews": total_reviews
#                     }
#                 )

#     return f"Monthly review summary generated for {now.strftime('%B %Y')}"



@shared_task
def send_order_completion_email(email, username, order_id):
    subject = f"Order #{order_id} Completed"
    message = f"Hi {username}, your order #{order_id} has been successfully completed!"
    send_mail(subject, message, 'noreply@penman.com', [email])

@shared_task
def expire_stale_writer_requests():
    expiry_time = timezone.now() - timedelta(hours=48)
    stale_requests = WriterRequest.objects.filter(
        status=WriterRequest.RequestStatus.PENDING,
        created_at__lt=expiry_time
    )

    for req in stale_requests:
        req.status = WriterRequest.RequestStatus.DECLINED
        req.save()

        AuditLogService.log_auto(
            actor=None,
            action="AUTO_EXPIRE_WRITER_REQUEST",
            target="orders.WriterRequest",
            target_id=req.id,
            metadata={"reason": "Auto-declined after 48 hours"}
        )




def notify_writer_order_assigned(order):
    writer = order.writer
    if not writer:
        return

    async_send_notification.delay(
        user_id=writer.id,
        event="order_assigned",
        context={
            "order_id": order.id,
            "title": "New Order Assigned",
            "message": f"You have been assigned Order #{order.id} - {order.topic}.",
            "link": f"/orders/{order.id}/"
        },
        website_id=order.website_id,
        channels=[NotificationType.EMAIL, NotificationType.IN_APP]
    )


def notify_writer_missed_deadline(order):
    writer = order.writer
    if not writer:
        return

    async_send_notification.delay(
        user_id=writer.id,
        event="deadline_missed",
        context={
            "order_id": order.id,
            "title": "Deadline Missed",
            "message": f"You’ve missed the deadline for Order #{order.id}. Please contact support.",
            "link": f"/orders/{order.id}/"
        },
        website_id=order.website_id,
        channels=[NotificationType.EMAIL, NotificationType.IN_APP],
        category="warning",
        is_critical=True
    )


def notify_writer_fined(order, fine_amount):
    writer = order.writer
    if not writer:
        return

    async_send_notification.delay(
        user_id=writer.id,
        event="fine_applied",
        context={
            "order_id": order.id,
            "fine_amount": f"{fine_amount:.2f}",
            "title": "Fine Applied",
            "message": f"A fine of ${fine_amount:.2f} has been applied to your Order #{order.id}.",
            "link": f"/orders/{order.id}/"
        },
        website_id=order.website_id,
        channels=[NotificationType.EMAIL, NotificationType.IN_APP],
        category="error"
    )


def notify_client_writer_declined(order):
    client = order.client
    if not client:
        return

    async_send_notification.delay(
        user_id=client.id,
        event="writer_declined",
        context={
            "order_id": order.id,
            "title": "Writer Declined",
            "message": f"Your preferred writer declined Order #{order.id}. The order is now public.",
            "link": f"/orders/{order.id}/"
        },
        website_id=order.website_id,
        channels=[NotificationType.EMAIL, NotificationType.IN_APP],
        category="info"
    )


def notify_client_order_completed(order):
    client = order.client
    if not client:
        return

    async_send_notification.delay(
        user_id=client.id,
        event="order_completed",
        context={
            "order_id": order.id,
            "title": "Order Completed",
            "message": f"Order #{order.id} has been completed. Please log in to review it.",
            "link": f"/orders/{order.id}/"
        },
        website_id=order.website_id,
        channels=[NotificationType.EMAIL, NotificationType.IN_APP],
        category="success"
    )