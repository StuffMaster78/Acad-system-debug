import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications_system.services.notification_service import (
    NotificationService,
)

from .models import ExternalFileLink, FileDeletionRequest, OrderFile

logger = logging.getLogger(__name__)


@receiver(post_save, sender=OrderFile)
def notify_file_uploaded(sender, instance, created, **kwargs):
    """Notify users when a new file is uploaded.

    Notifies:
    1. The uploader
    2. The other party
    """
    if not created:
        return

    order = instance.order
    uploaded_by = instance.uploaded_by
    website = getattr(order, "website", None)

    if not website:
        return

    file_name = (
        instance.file.name.split("/")[-1]
        if instance.file else "a file"
    )
    uploader_role = (
        getattr(uploaded_by, "role", None)
        if uploaded_by else None
    )

    if uploaded_by:
        try:
            NotificationService.notify(
                event_key="order.file_uploaded",
                recipient=uploaded_by,
                website=website,
                context={
                    "order_id": order.id,
                    "file_id": instance.id,
                    "file_name": file_name,
                    "uploaded_by_you": True,
                    "uploader_role": uploader_role,
                    "message": (
                        f"You uploaded {file_name} to order #{order.id}"
                    ),
                },
                channels=["in_app"],
                triggered_by=uploaded_by,
                priority="normal",
                is_broadcast=False,
                is_critical=False,
                is_digest=False,
                is_silent=False,
                digest_group=None,
            )
        except Exception as exc:
            logger.warning(
                "Failed to notify uploader about file upload: %s",
                exc,
            )

    if (
        uploader_role == "writer"
        and order.client
        and order.client != uploaded_by
    ):
        try:
            NotificationService.notify(
                event_key="order.file_uploaded",
                recipient=order.client,
                website=website,
                context={
                    "order_id": order.id,
                    "file_id": instance.id,
                    "file_name": file_name,
                    "uploaded_by_you": False,
                    "uploader_role": uploader_role,
                    "message": (
                        f"Writer uploaded {file_name} to order #{order.id}"
                    ),
                },
                channels=["in_app"],
                triggered_by=uploaded_by,
                priority="normal",
                is_broadcast=False,
                is_critical=False,
                is_digest=False,
                is_silent=False,
                digest_group=None,
            )
        except Exception as exc:
            logger.warning(
                "Failed to notify client about file upload: %s",
                exc,
            )

    elif (
        uploader_role == "client"
        and order.assigned_writer
        and order.assigned_writer != uploaded_by
    ):
        try:
            NotificationService.notify(
                event_key="order.file_uploaded",
                recipient=order.assigned_writer,
                website=website,
                context={
                    "order_id": order.id,
                    "file_id": instance.id,
                    "file_name": file_name,
                    "uploaded_by_you": False,
                    "uploader_role": uploader_role,
                    "message": (
                        f"Client uploaded {file_name} to order #{order.id}"
                    ),
                },
                channels=["in_app"],
                triggered_by=uploaded_by,
                priority="normal",
                is_broadcast=False,
                is_critical=False,
                is_digest=False,
                is_silent=False,
                digest_group=None,
            )
        except Exception as exc:
            logger.warning(
                "Failed to notify writer about file upload: %s",
                exc,
            )


@receiver(post_save, sender=FileDeletionRequest)
def notify_deletion_request(sender, instance, created, **kwargs):
    """Notify admin when a file deletion request is submitted."""
    if not created:
        return

    order = instance.file.order
    website = getattr(instance, "website", None) or getattr(
        order,
        "website",
        None,
    )
    admin = getattr(order, "admin", None)

    if not website or not admin:
        return

    try:
        NotificationService.notify(
            event_key="order.file_deletion_requested",
            recipient=admin,
            website=website,
            context={
                "order_id": order.id,
                "file_id": instance.file.id,
                "file_name": str(instance.file),
                "requested_by_id": (
                    instance.requested_by.id
                    if instance.requested_by else None
                ),
                "requested_by_name": str(instance.requested_by),
                "reason": instance.reason,
                "request_id": instance.id,
                "message": (
                    f"Deletion request for {instance.file} by "
                    f"{instance.requested_by}."
                ),
            },
            channels=["in_app"],
            triggered_by=instance.requested_by,
            priority="high",
            is_broadcast=False,
            is_critical=False,
            is_digest=False,
            is_silent=False,
            digest_group=None,
        )
    except Exception as exc:
        logger.warning(
            "Failed to notify admin about deletion request: %s",
            exc,
        )


@receiver(post_save, sender=ExternalFileLink)
def notify_external_link_uploaded(sender, instance, created, **kwargs):
    """Notify admin when a new external file link is uploaded."""
    if not created:
        return

    order = instance.order
    website = getattr(instance, "website", None) or getattr(
        order,
        "website",
        None,
    )
    admin = getattr(order, "admin", None)

    if not website or not admin:
        return

    try:
        NotificationService.notify(
            event_key="order.external_file_link_uploaded",
            recipient=admin,
            website=website,
            context={
                "order_id": order.id,
                "external_file_link_id": instance.id,
                "uploaded_by_id": (
                    instance.uploaded_by.id
                    if instance.uploaded_by else None
                ),
                "uploaded_by_name": str(instance.uploaded_by),
                "link": instance.link,
                "description": instance.description,
                "message": (
                    f"New external file link submitted for Order "
                    f"{order.id} by {instance.uploaded_by}."
                ),
            },
            channels=["in_app"],
            triggered_by=instance.uploaded_by,
            priority="normal",
            is_broadcast=False,
            is_critical=False,
            is_digest=False,
            is_silent=False,
            digest_group=None,
        )
    except Exception as exc:
        logger.warning(
            "Failed to notify admin about external file link: %s",
            exc,
        )