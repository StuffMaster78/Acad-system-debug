from activity.models import ActivityLog


class ActivityLogger:
    """Service for logging system and user activity events."""

    @staticmethod
    def log_activity(
        *,
        user,
        website,
        action_type,
        description,
        metadata=None,
        triggered_by=None
    ):
        """Create a generic activity log entry.

        Args:
            user (User): The user the activity is associated with.
            website (Website): The related website instance.
            action_type (str): Category of the action (e.g., "ORDER").
            description (str): Human-readable description of the action.
            metadata (dict, optional): Additional metadata for context.
            triggered_by (User, optional): The actor who initiated the action.

        Returns:
            ActivityLog: The created activity log entry.
        """
        if not user and triggered_by:
            user = triggered_by

        return ActivityLog.objects.create(
            user=user,
            triggered_by=triggered_by,
            website=website,
            action_type=action_type,
            description=description,
            metadata=metadata or {},
        )

    @staticmethod
    def log_order_created(order, triggered_by=None):
        """Log when a new order is created.

        Args:
            order (Order): The order that was created.
            triggered_by (User, optional): Who triggered the action.

        Returns:
            ActivityLog: The log entry.
        """
        return ActivityLogger.log_activity(
            user=order.client,
            triggered_by=triggered_by,
            website=order.website,
            action_type="ORDER",
            description=f"New order #{order.id} placed.",
            metadata={"order_id": order.id, "status": order.status},
        )

    @staticmethod
    def log_order_updated(order, triggered_by=None):
        """Log when an order is updated.

        Args:
            order (Order): The order that was updated.
            triggered_by (User, optional): Who triggered the update.

        Returns:
            ActivityLog: The log entry.
        """
        return ActivityLogger.log_activity(
            user=order.client,
            triggered_by=triggered_by,
            website=order.website,
            action_type="ORDER",
            description=(
                f"Order #{order.id} updated. Status: {order.status}."
            ),
            metadata={"order_id": order.id, "status": order.status},
        )

    @staticmethod
    def log_order_deleted(order, triggered_by=None):
        """Log when an order is deleted.

        Args:
            order (Order): The order being deleted.
            triggered_by (User, optional): Who deleted the order.

        Returns:
            ActivityLog: The log entry.
        """
        return ActivityLogger.log_activity(
            user=order.client,
            triggered_by=triggered_by,
            website=order.website,
            action_type="ORDER",
            description=f"Order #{order.id} was deleted.",
            metadata={"order_id": order.id},
        )

    @staticmethod
    def log_user_created(user):
        """Log when a new user account is created.

        Args:
            user (User): The user that was created.

        Returns:
            ActivityLog: The log entry.
        """
        return ActivityLogger.log_activity(
            user=user,
            website=user.website,
            action_type="USER",
            description=(
                f"New user account created: {user.username}."
            ),
        )

    @staticmethod
    def log_user_updated(user):
        """Log when a user updates their profile.

        Args:
            user (User): The user that was updated.

        Returns:
            ActivityLog: The log entry.
        """
        return ActivityLogger.log_activity(
            user=user,
            website=user.website,
            action_type="USER",
            description=f"User {user.username} profile updated.",
        )

    @staticmethod
    def log_payment_created(payment, triggered_by=None):
        """Log when a new payment is received.

        Args:
            payment (Payment): The payment that was created.
            triggered_by (User, optional): Who triggered the action.

        Returns:
            ActivityLog: The log entry.
        """
        return ActivityLogger.log_activity(
            user=payment.client,
            triggered_by=triggered_by,
            website=payment.website,
            action_type="PAYMENT",
            description=(
                f"Payment of ${payment.amount} received for "
                f"Order #{payment.order.id}."
            ),
            metadata={
                "order_id": payment.order.id,
                "amount": str(payment.amount),
                "status": payment.status,
            },
        )

    @staticmethod
    def log_payment_updated(payment, triggered_by=None):
        """Log when a payment is updated.

        Args:
            payment (Payment): The payment that was updated.
            triggered_by (User, optional): Who triggered the update.

        Returns:
            ActivityLog: The log entry.
        """
        return ActivityLogger.log_activity(
            user=payment.client,
            triggered_by=triggered_by,
            website=payment.website,
            action_type="PAYMENT",
            description=(
                f"Payment updated for Order #{payment.order.id}. "
                f"New Status: {payment.status}."
            ),
            metadata={
                "order_id": payment.order.id,
                "amount": str(payment.amount),
                "status": payment.status,
            },
        )

    @staticmethod
    def log_notification_sent(notification, triggered_by=None):
        """Log when a notification is sent to a user.

        Args:
            notification (Notification): The notification that was sent.
            triggered_by (User, optional): Who triggered the notification.

        Returns:
            ActivityLog: The log entry.
        """
        return ActivityLogger.log_activity(
            user=notification.user,
            triggered_by=triggered_by,
            website=notification.website,
            action_type="NOTIFICATION",
            description=(
                f"Notification sent to {notification.user.username}: "
                f"{notification.message}."
            ),
            metadata={
                "notification_id": notification.id,
                "message": notification.message,
            },
        )

    @staticmethod
    def log_communication_sent(communication, triggered_by=None):
        """Log when a communication is sent to a user.

        Args:
            communication (Communication): The communication that was sent.
            triggered_by (User, optional): Who triggered the communication.

        Returns:
            ActivityLog: The log entry.
        """
        return ActivityLogger.log_activity(
            user=communication.user,
            triggered_by=triggered_by,
            website=communication.website,
            action_type="COMMUNICATION",
            description=(
                f"Communication sent to {communication.user.username}: "
                f"{communication.message}."
            ),
            metadata={
                "communication_id": communication.id,
                "message": communication.message,
            },
        )

    @staticmethod
    def log_loyalty_points_updated(loyalty, triggered_by=None):
        """Log when a user's loyalty points are updated.

        Args:
            loyalty (Loyalty): The loyalty instance with updated points.
            triggered_by (User, optional): Who triggered the update.

        Returns:
            ActivityLog: The log entry.
        """
        return ActivityLogger.log_activity(
            user=loyalty.user,
            triggered_by=triggered_by,
            website=loyalty.website,
            action_type="LOYALTY",
            description=(
                f"Loyalty points updated for {loyalty.user.username}: "
                f"{loyalty.points} points."
            ),
            metadata={
                "loyalty_id": loyalty.id,
                "points": loyalty.points,
            },
        )

    @staticmethod
    def log_system_event(event, triggered_by=None):
        """Log a system event that doesn't directly relate to a user action.

        Args:
            event (SystemEvent): The system event instance.
            triggered_by (User, optional): Who triggered the event.

        Returns:
            ActivityLog: The log entry.
        """
        return ActivityLogger.log_activity(
            user=None,
            triggered_by=triggered_by,
            website=event.website,
            action_type="SYSTEM",
            description=f"System event: {event.description}.",
            metadata={
                "event_id": event.id,
                "details": event.details,
            },
        )