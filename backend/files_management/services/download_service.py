"""
Download Service
==================

Handles the complete download flow for attachments:
1. Gate check (free / email / account / customer / paid)
2. Email capture (for email-gated downloads)
3. Download event tracking with attribution
4. Signed URL generation
5. Newsletter subscriber creation (for email-gated)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils import timezone

if TYPE_CHECKING:
    from django.http import HttpRequest

    from cms_attachments.models import Attachment

logger = logging.getLogger(__name__)


class DownloadService:
    """Handle gated downloads, email capture, and tracking."""

    @classmethod
    def check_access(cls, attachment: Attachment, request: HttpRequest) -> dict:
        """
        Check whether the current user/session can download this attachment.

        Returns:
            {
                "allowed": True/False,
                "gate_type": str,
                "reason": str if not allowed,
                "requires_email": bool,
                "requires_login": bool,
                "requires_payment": bool,
            }
        """
        gate = attachment.gate_type

        if gate == "free":
            return {"allowed": True, "gate_type": gate}

        if gate == "email":
            # Check if email already captured in this session
            from cms_attachments.models import EmailGatedAccess

            session_email = request.session.get("gated_email")
            if session_email:
                exists = EmailGatedAccess.objects.filter(
                    site=attachment.site,
                    email=session_email,
                    attachment=attachment,
                ).exists()
                if exists:
                    return {"allowed": True, "gate_type": gate}

            return {
                "allowed": False,
                "gate_type": gate,
                "reason": "Email required to download this resource",
                "requires_email": True,
                "requires_login": False,
                "requires_payment": False,
            }

        if gate == "account":
            if request.user.is_authenticated:
                return {"allowed": True, "gate_type": gate}
            return {
                "allowed": False,
                "gate_type": gate,
                "reason": "Please log in to download this resource",
                "requires_email": False,
                "requires_login": True,
                "requires_payment": False,
            }

        if gate == "customer":
            if not request.user.is_authenticated:
                return {
                    "allowed": False,
                    "gate_type": gate,
                    "reason": "Please log in to download this resource",
                    "requires_login": True,
                }
            # Check for completed order
            try:
                from orders.models import Order

                has_order = Order.objects.filter(
                    client__user=request.user,
                    website=attachment.site.website_config,
                    status="completed",
                ).exists()
                if has_order:
                    return {"allowed": True, "gate_type": gate}
            except (ImportError, Exception):
                pass

            return {
                "allowed": False,
                "gate_type": gate,
                "reason": "This resource is available to customers with completed orders",
                "requires_email": False,
                "requires_login": False,
                "requires_payment": False,
            }

        if gate == "paid":
            # Check payment — implementation depends on your payment system
            return {
                "allowed": False,
                "gate_type": gate,
                "reason": f"This resource costs ${attachment.price}",
                "requires_email": False,
                "requires_login": True,
                "requires_payment": True,
            }

        return {"allowed": False, "gate_type": gate, "reason": "Unknown gate type"}

    @classmethod
    def capture_email_and_download(
        cls,
        attachment: Attachment,
        email: str,
        request: HttpRequest,
        consent_marketing: bool = False,
        consent_newsletter: bool = False,
    ) -> dict:
        """
        Process an email-gated download:
        1. Create or update EmailGatedAccess record
        2. Create newsletter subscriber (if consent given)
        3. Enroll in automation sequence
        4. Track the download
        5. Return the download URL

        Returns:
            {
                "success": True,
                "download_url": str,
                "subscriber_created": bool,
            }
        """
        from cms_attachments.models import EmailGatedAccess

        # 1. Email capture
        email_record, created = EmailGatedAccess.objects.update_or_create(
            site=attachment.site,
            email=email,
            defaults={
                "attachment": attachment,
                "consent_marketing": consent_marketing,
                "consent_newsletter": consent_newsletter,
                "utm_source": request.GET.get("utm_source", ""),
                "utm_medium": request.GET.get("utm_medium", ""),
                "utm_campaign": request.GET.get("utm_campaign", ""),
            },
        )

        if not created:
            email_record.download_count += 1
            email_record.save(update_fields=["download_count", "last_download"])

        # Store email in session for future downloads
        request.session["gated_email"] = email

        # Update attachment counters
        attachment.email_capture_count += 1
        attachment.save(update_fields=["email_capture_count"])

        # 2. Newsletter subscriber creation
        subscriber_created = False
        if consent_newsletter or consent_marketing:
            subscriber_created = cls._create_subscriber(
                attachment=attachment,
                email=email,
                consent_marketing=consent_marketing,
            )

        # 3. Automation enrollment
        if created: # Only enroll on first capture
            cls._enroll_in_automation(attachment, email)

        # 4. Track download
        download_url = cls.track_and_get_url(attachment, request, email=email)

        logger.info(
            "Email-gated download: %s → %s (subscriber: %s)",
            email,
            attachment.title,
            subscriber_created,
        )

        return {
            "success": True,
            "download_url": download_url,
            "subscriber_created": subscriber_created,
        }

    @classmethod
    def track_and_get_url(
        cls,
        attachment: Attachment,
        request: HttpRequest,
        email: str = "",
    ) -> str:
        """
        Track a download event and return the download URL.

        For free/account/customer downloads (no email gate needed).
        """
        from cms_attachments.models import AttachmentDownload

        # Record the download
        AttachmentDownload.objects.create(
            attachment=attachment,
            user=request.user if request.user.is_authenticated else None,
            session_id=request.session.session_key or "",
            email=email,
            source_page_url=request.META.get("HTTP_REFERER", ""),
            referrer=request.META.get("HTTP_REFERER", ""),
            ip_address=cls._get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )

        # Update download counter
        attachment.download_count += 1
        attachment.save(update_fields=["download_count"])

        # Generate download URL
        if attachment.managed_file:
            from files_management.services.storage_service import StorageService

            return StorageService.get_download_url(
                attachment.managed_file,
                force_download=True,
            )

        return ""

    @classmethod
    def _create_subscriber(
        cls,
        attachment: Attachment,
        email: str,
        consent_marketing: bool,
    ) -> bool:
        """Create a newsletter subscriber from an email-gated download."""
        try:
            from cms_newsletters.models import Subscriber

            _, created = Subscriber.objects.get_or_create(
                site=attachment.site,
                email=email,
                defaults={
                    "is_active": True,
                    "consent_marketing": consent_marketing,
                    "consent_date": timezone.now(),
                    "source": "attachment_gate",
                    "source_detail": f"Attachment: {attachment.title} (id={attachment.pk})",
                },
            )
            return created

        except ImportError:
            logger.debug("cms_newsletters not installed — skipping subscriber creation")
            return False
        except Exception as exc:
            logger.warning("Failed to create subscriber for %s: %s", email, exc)
            return False

    @classmethod
    def _enroll_in_automation(cls, attachment: Attachment, email: str):
        """Enroll the new subscriber in the attachment_download automation."""
        try:
            from cms_newsletters.models import (
                AutomationEnrollment,
                AutomationSequence,
                Subscriber,
            )

            subscriber = Subscriber.objects.filter(
                site=attachment.site,
                email=email,
            ).first()

            if not subscriber:
                return

            sequence = AutomationSequence.objects.filter(
                site=attachment.site,
                trigger_type="attachment_download",
                is_active=True,
            ).first()

            if not sequence:
                return

            # Don't re-enroll
            if AutomationEnrollment.objects.filter(
                subscriber=subscriber,
                sequence=sequence,
            ).exists():
                return

            first_step = sequence.steps.filter(is_active=True).order_by("step_order").first()
            if not first_step:
                return

            from datetime import timedelta

            AutomationEnrollment.objects.create(
                subscriber=subscriber,
                sequence=sequence,
                current_step=0,
                next_send_at=timezone.now() + timedelta(days=first_step.delay_days),
                status="active",
            )
            logger.info(
                "Enrolled %s in automation '%s'",
                email,
                sequence.name,
            )

        except ImportError:
            pass
        except Exception as exc:
            logger.warning("Automation enrollment failed: %s", exc)

    @staticmethod
    def _get_client_ip(request: HttpRequest) -> str:
        """Extract client IP from request headers."""
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")
