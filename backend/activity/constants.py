from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class ActivityActorType(models.TextChoices):
    """
    Defines the source category of an activity event.
    """

    ADMIN = "admin", _("Admin")
    CLIENT = "client", _("Client")
    WRITER = "writer", _("Writer")
    SUPPORT = "support", _("Support")
    EDITOR = "editor", _("Editor")
    SUPERADMIN = "superadmin", _("Super Admin")
    SYSTEM = "system", _("System")


class ActivityAudience(models.TextChoices):
    """
    Defines which audience may view an activity event.
    """

    CLIENT = "client", _("Client")
    WRITER = "writer", _("Writer")
    STAFF = "staff", _("Staff")
    ADMIN = "admin", _("Admin")
    SUPERADMIN = "superadmin", _("Super Admin")
    INTERNAL = "internal", _("Internal")


class ActivitySeverity(models.TextChoices):
    """
    Defines the operational importance of an activity event.
    """

    INFO = "info", _("Info")
    SUCCESS = "success", _("Success")
    WARNING = "warning", _("Warning")
    CRITICAL = "critical", _("Critical")


class ActivityVerb(models.TextChoices):
    """
    Defines canonical event verbs used across the platform.
    """

    ORDER_CREATED = "order.created", _("Order created")
    ORDER_PAID = "order.paid", _("Order paid")
    ORDER_ASSIGNED = "order.assigned", _("Order assigned")
    ORDER_SUBMITTED = "order.submitted", _("Order submitted")
    ORDER_COMPLETED = "order.completed", _("Order completed")
    ORDER_REVISION_REQUESTED = (
        "order.revision_requested",
        _("Order revision requested"),
    )


    FILE_UPLOADED = "file.uploaded", _("File uploaded")
    FILE_APPROVED = "file.approved", _("File approved")
    FILE_DOWNLOADED = "file.downloaded", _("File downloaded")

    MESSAGE_SENT = "message.sent", _("Message sent")
    THREAD_CREATED = "thread.created", _("Thread created")

    WALLET_CREDITED = "wallet.credited", _("Wallet credited")
    WALLET_DEBITED = "wallet.debited", _("Wallet debited")

    PAYMENT_RECEIVED = "payment.received", _("Payment received")
    REFUND_REQUESTED = "refund.requested", _("Refund requested")

    CLASS_CREATED = "class.created", _("Class created")
    CLASS_UPDATED = "class.updated", _("Class updated")

    SPECIAL_ORDER_CREATED = (
        "special_order.created",
        _("Special order created"),
    )
    SPECIAL_ORDER_MILESTONE_FUNDED = (
        "special_order.milestone_funded",
        _("Special order milestone funded"),
    )

    SYSTEM_NOTICE = "system.notice", _("System notice")