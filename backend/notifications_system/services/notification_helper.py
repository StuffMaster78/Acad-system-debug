"""
Helper service for easy notification integration across the system.
Provides convenience methods for common notification scenarios.
"""
from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from websites.models import Website
from websites.utils import get_current_website
from notifications_system.services.core import NotificationService

User = get_user_model()


class NotificationHelper:
    """
    Helper class to simplify notification sending across the system.
    """
    
    @staticmethod
    def send_notification(
        user,
        event: str,
        payload: Dict[str, Any],
        website: Optional[Website] = None,
        actor=None,
        **kwargs
    ):
        """
        Send a notification to a user.
        
        Args:
            user: User instance or user ID
            event: Event key (e.g., "order.paid", "payment.completed")
            payload: Event payload data
            website: Website instance (optional, will try to get from context)
            actor: User who triggered the event (optional)
            **kwargs: Additional arguments passed to NotificationService
        
        Returns:
            Notification instance or None
        """
        # Convert user ID to user instance if needed
        if isinstance(user, int):
            try:
                user = User.objects.get(id=user)
            except User.DoesNotExist:
                return None
        
        # Get website if not provided
        if website is None:
            # Try to get from payload
            website_id = payload.get("website_id")
            if website_id:
                try:
                    website = Website.objects.get(id=website_id)
                except Website.DoesNotExist:
                    pass
            
            # Fallback to user's website or first active
            if website is None:
                if hasattr(user, 'website'):
                    website = user.website
                else:
                    website = Website.objects.filter(is_active=True).first()
        
        if not website:
            return None
        
        try:
            return NotificationService.send_notification(
                user=user,
                event=event,
                payload=payload,
                website=website,
                actor=actor,
                **kwargs
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send notification {event} to user {user.id}: {e}")
            return None
    
    @staticmethod
    def notify_order_paid(order, payment_amount, payment_method="payment method"):
        """Notify client and writer when order is paid."""
        payload = {
            "order_id": order.id,
            "order_topic": order.topic,
            "amount": str(payment_amount),
            "payment_method": payment_method,
            "website_id": order.website_id
        }
        
        notifications = []
        
        # Notify client
        if order.client:
            notifications.append(
                NotificationHelper.send_notification(
                    user=order.client,
                    event="order.paid",
                    payload=payload
                )
            )
            
            # Also send payment completed notification
            notifications.append(
                NotificationHelper.send_notification(
                    user=order.client,
                    event="payment.completed",
                    payload=payload
                )
            )
        
        # Notify assigned writer
        if order.assigned_writer:
            notifications.append(
                NotificationHelper.send_notification(
                    user=order.assigned_writer,
                    event="order.paid",
                    payload={**payload, "role": "writer"}
                )
            )
        
        return notifications
    
    @staticmethod
    def notify_payment_failed(order, amount, reason="Payment could not be processed"):
        """Notify client when payment fails."""
        payload = {
            "order_id": order.id,
            "order_topic": order.topic,
            "amount": str(amount),
            "reason": reason,
            "website_id": order.website_id
        }
        
        if order.client:
            return NotificationHelper.send_notification(
                user=order.client,
                event="payment.failed",
                payload=payload,
                is_critical=True
            )
        return None
    
    @staticmethod
    def notify_refund_processed(refund, order, amount, reason=""):
        """Notify client when refund is processed."""
        payload = {
            "order_id": order.id,
            "amount": str(amount),
            "reason": reason,
            "refund_id": refund.id,
            "website_id": order.website_id
        }
        
        if order.client:
            return NotificationHelper.send_notification(
                user=order.client,
                event="payment.refunded",
                payload=payload
            )
        return None
    
    @staticmethod
    def notify_loyalty_points_awarded(client_profile, points, reason, total_points):
        """Notify client when loyalty points are awarded."""
        payload = {
            "points": points,
            "total_points": total_points,
            "reason": reason,
            "website_id": client_profile.website_id
        }
        
        return NotificationHelper.send_notification(
            user=client_profile.user,
            event="loyalty.points_awarded",
            payload=payload
        )
    
    @staticmethod
    def notify_tier_upgraded(client_profile, tier_name, perks=""):
        """Notify client when loyalty tier is upgraded."""
        payload = {
            "tier_name": tier_name,
            "perks": perks,
            "website_id": client_profile.website_id
        }
        
        return NotificationHelper.send_notification(
            user=client_profile.user,
            event="loyalty.tier_upgraded",
            payload=payload,
            is_critical=True
        )
    
    @staticmethod
    def notify_redemption_approved(redemption_request, fulfillment_code=None):
        """Notify client when redemption is approved."""
        payload = {
            "redemption_id": redemption_request.id,
            "item_name": redemption_request.item.name,
            "points_used": redemption_request.points_used,
            "fulfillment_code": fulfillment_code or redemption_request.fulfillment_code,
            "website_id": redemption_request.website_id
        }
        
        return NotificationHelper.send_notification(
            user=redemption_request.client.user,
            event="loyalty.redemption.approved",
            payload=payload
        )
    
    @staticmethod
    def notify_redemption_rejected(redemption_request, reason):
        """Notify client when redemption is rejected."""
        payload = {
            "redemption_id": redemption_request.id,
            "item_name": redemption_request.item.name,
            "points_used": redemption_request.points_used,
            "rejection_reason": reason,
            "website_id": redemption_request.website_id
        }
        
        return NotificationHelper.send_notification(
            user=redemption_request.client.user,
            event="loyalty.redemption.rejected",
            payload=payload
        )
    
    @staticmethod
    def notify_class_bundle_created(class_bundle, client_profile):
        """Notify client when class bundle is created."""
        payload = {
            "bundle_id": class_bundle.id,
            "bundle_name": f"Class Bundle #{class_bundle.id}",
            "total_price": str(class_bundle.total_price),
            "number_of_classes": class_bundle.number_of_classes or 1,
            "deposit_required": str(class_bundle.deposit_required) if class_bundle.deposit_required else None,
            "website_id": class_bundle.website_id
        }
        
        return NotificationHelper.send_notification(
            user=client_profile.user,
            event="class.bundle.created",
            payload=payload
        )
    
    @staticmethod
    def notify_class_deposit_paid(class_bundle, amount, balance_remaining):
        """Notify client when class deposit is paid."""
        payload = {
            "bundle_id": class_bundle.id,
            "bundle_name": f"Class Bundle #{class_bundle.id}",
            "amount": str(amount),
            "balance_remaining": str(balance_remaining),
            "website_id": class_bundle.website_id
        }
        
        return NotificationHelper.send_notification(
            user=class_bundle.client.user,
            event="class.bundle.deposit_paid",
            payload=payload
        )
    
    @staticmethod
    def notify_installment_due(installment, order_id=None, special_order_id=None):
        """Notify client when installment is due."""
        from special_orders.models import InstallmentPayment
        from class_management.models import ClassInstallment
        
        payload = {
            "amount": str(installment.amount),
            "due_date": installment.due_date.strftime("%Y-%m-%d") if hasattr(installment, 'due_date') and installment.due_date else None,
            "website_id": installment.special_order.website_id if isinstance(installment, InstallmentPayment) else installment.class_bundle.website_id,
        }
        
        if isinstance(installment, InstallmentPayment):
            payload.update({
                "special_order_id": installment.special_order.id,
                "installment_number": installment.installment_number,
                "total_installments": installment.special_order.installments.count(),
                "order_id": order_id or installment.special_order.id
            })
            user = installment.special_order.client.user
            payload["bundle_name"] = f"Special Order #{installment.special_order.id}"
        elif isinstance(installment, ClassInstallment):
            payload.update({
                "bundle_id": installment.class_bundle.id,
                "installment_id": installment.id,
                "installment_number": installment.installment_number,
                "total_installments": installment.class_bundle.installments.count(),
                "bundle_name": f"Class Bundle #{installment.class_bundle.id}"
            })
            user = installment.class_bundle.client.user
        else:
            return None
        
        return NotificationHelper.send_notification(
            user=user,
            event="payment.installment_due",
            payload=payload,
            is_critical=True
        )
    
    @staticmethod
    def notify_ticket_created(ticket, creator):
        """Notify support staff when ticket is created."""
        payload = {
            "ticket_id": ticket.id,
            "ticket_number": f"#{ticket.id}",
            "subject": ticket.subject,
            "website_id": ticket.website_id
        }
        
        notifications = []
        
        # Notify creator (client)
        if creator != ticket.created_by:
            notifications.append(
                NotificationHelper.send_notification(
                    user=ticket.created_by,
                    event="ticket.created",
                    payload=payload,
                    actor=creator
                )
            )
        
        # Notify assigned support staff
        if ticket.assigned_to:
            notifications.append(
                NotificationHelper.send_notification(
                    user=ticket.assigned_to,
                    event="ticket.assigned",
                    payload={**payload, "assignee_name": ticket.assigned_to.get_full_name() or ticket.assigned_to.username},
                    actor=creator
                )
            )
        
        return notifications
    
    @staticmethod
    def notify_ticket_reply(ticket, message, replier):
        """Notify relevant users when ticket receives reply."""
        payload = {
            "ticket_id": ticket.id,
            "ticket_number": f"#{ticket.id}",
            "message_id": message.id,
            "replier_name": replier.get_full_name() or replier.username,
            "message_preview": message.content[:200] if hasattr(message, 'content') else str(message),
            "website_id": ticket.website_id
        }
        
        notifications = []
        
        # Notify ticket creator
        if ticket.created_by != replier:
            notifications.append(
                NotificationHelper.send_notification(
                    user=ticket.created_by,
                    event="ticket.replied",
                    payload=payload,
                    actor=replier
                )
            )
        
        # Notify assigned staff (if different from replier)
        if ticket.assigned_to and ticket.assigned_to != replier:
            notifications.append(
                NotificationHelper.send_notification(
                    user=ticket.assigned_to,
                    event="ticket.replied",
                    payload=payload,
                    actor=replier
                )
            )
        
        return notifications

