"""
DownloadService
================
Handles all access-control and download logic for Attachment resources.

Gate types:
  free      — anyone can download immediately
  email     — requires email capture; link sent via email
  account   — requires authenticated user account
  customer  — requires at least one completed order
  paid      — requires payment (not yet implemented)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.core import signing

if TYPE_CHECKING:
    from django.http import HttpRequest
    from cms_attachments.models import Attachment

logger = logging.getLogger(__name__)

# Token is valid for 7 days
DOWNLOAD_TOKEN_MAX_AGE = 60 * 60 * 24 * 7


class DownloadService:

    # ── Access checking ───────────────────────────────────────────────────────

    @staticmethod
    def check_access(attachment: "Attachment", request: "HttpRequest") -> dict:
        """
        Returns a dict describing whether the request can download this attachment.

        {
            "allowed": bool,
            "requires_email": bool,
            "requires_account": bool,
            "reason": str | None,
        }
        """
        gate = attachment.gate_type

        if gate == "free":
            return {"allowed": True, "requires_email": False, "requires_account": False}

        if gate == "email":
            return {
                "allowed": False,
                "requires_email": True,
                "requires_account": False,
                "reason": "Email required to download this resource.",
            }

        if gate == "account":
            if request.user and request.user.is_authenticated:
                return {"allowed": True, "requires_email": False, "requires_account": False}
            return {
                "allowed": False,
                "requires_email": False,
                "requires_account": True,
                "reason": "Sign in to download this resource.",
            }

        if gate == "customer":
            if request.user and request.user.is_authenticated:
                # Lazy import to avoid circular dependency
                try:
                    from orders.models import Order
                    has_order = Order.objects.filter(
                        client=request.user, status="completed"
                    ).exists()
                    if has_order:
                        return {"allowed": True, "requires_email": False, "requires_account": False}
                except Exception:
                    pass
            return {
                "allowed": False,
                "requires_email": False,
                "requires_account": True,
                "reason": "This resource is available to customers with a completed order.",
            }

        # paid — not yet implemented
        return {
            "allowed": False,
            "requires_email": False,
            "requires_account": False,
            "reason": "This is a premium resource.",
        }

    # ── Free / account downloads ──────────────────────────────────────────────

    @staticmethod
    def track_and_get_url(attachment: "Attachment", request: "HttpRequest") -> str | None:
        """Record a download event and return the file URL."""
        from cms_attachments.models import AttachmentDownload

        AttachmentDownload.objects.create(
            attachment=attachment,
            user=request.user if request.user.is_authenticated else None,
            session_id=(request.session.session_key or ""),
            source_page_url=request.META.get("HTTP_REFERER", "")[:500],
            ip_address=DownloadService._get_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )

        attachment.download_count += 1
        attachment.save(update_fields=["download_count"])

        if attachment.managed_file:
            return attachment.managed_file.public_url
        return None

    # ── Email-gated downloads ─────────────────────────────────────────────────

    @staticmethod
    def capture_email_and_download(
        attachment: "Attachment",
        email: str,
        request: "HttpRequest",
        consent_marketing: bool = False,
        consent_newsletter: bool = False,
    ) -> dict:
        """
        Capture an email address, record the lead, and send the download link.
        Returns {"success": true, "message": "..."} — no direct URL in response
        (download arrives via email, like nursingpaper.com).
        """
        from cms_attachments.models import AttachmentDownload, EmailGatedAccess

        site = getattr(request, "site", None)

        # Upsert the EmailGatedAccess record
        lead, created = EmailGatedAccess.objects.update_or_create(
            site=site,
            email=email.lower().strip(),
            defaults={},
        )
        # If already exists, update counts and consent
        if not created:
            lead.download_count += 1
        lead.consent_marketing = lead.consent_marketing or consent_marketing
        lead.consent_newsletter = lead.consent_newsletter or consent_newsletter
        # Attach to this specific attachment if not already set
        if lead.attachment_id != attachment.pk:
            # New attachment for this email — update
            lead.attachment = attachment
        lead.save()

        # Track the download event
        AttachmentDownload.objects.create(
            attachment=attachment,
            email=email,
            session_id=(request.session.session_key or ""),
            source_page_url=request.META.get("HTTP_REFERER", "")[:500],
            ip_address=DownloadService._get_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )

        attachment.email_capture_count += 1
        attachment.download_count += 1
        attachment.save(update_fields=["email_capture_count", "download_count"])

        # Generate a signed download token (7 days)
        token = signing.dumps(
            {"attachment_slug": attachment.slug, "email": email},
            salt="cms_attachments_download",
        )

        # Build download URL
        site_url = getattr(settings, "SITE_URL", "").rstrip("/")
        download_url = f"{site_url}/cms-api/attachments/{attachment.slug}/serve/?token={token}"

        # Send email
        sent = DownloadService._send_download_email(
            email=email,
            attachment=attachment,
            download_url=download_url,
        )

        if sent:
            return {
                "success": True,
                "message": "Check your inbox — your download link is on its way.",
            }
        else:
            # Email failed — return direct link as fallback so user isn't left hanging
            logger.warning("Email delivery failed for %s / %s", email, attachment.slug)
            return {
                "success": True,
                "message": "Email delivery failed. Use the link below to download.",
                "download_url": download_url,
            }

    # ── Signed token download ─────────────────────────────────────────────────

    @staticmethod
    def redeem_token(token: str) -> "Attachment | None":
        """
        Validate a signed token and return the Attachment if valid.
        Called by a /serve/?token= view.
        """
        from cms_attachments.models import Attachment as AttachmentModel

        try:
            data = signing.loads(
                token,
                salt="cms_attachments_download",
                max_age=DOWNLOAD_TOKEN_MAX_AGE,
            )
            return AttachmentModel.objects.select_related("managed_file").get(
                slug=data["attachment_slug"],
                status="published",
            )
        except (signing.BadSignature, signing.SignatureExpired, AttachmentModel.DoesNotExist):
            return None

    # ── Email delivery ────────────────────────────────────────────────────────

    @staticmethod
    def _send_download_email(email: str, attachment: "Attachment", download_url: str) -> bool:
        subject = f"Your free resource: {attachment.title}"
        html_body = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>{attachment.title}</title></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
             background: #f8fafc; margin: 0; padding: 40px 16px;">
  <div style="max-width: 560px; margin: 0 auto; background: #fff;
              border-radius: 12px; overflow: hidden;
              box-shadow: 0 1px 3px rgba(0,0,0,.08);">
    <div style="background: #6d28d9; padding: 32px 40px;">
      <p style="color: #ede9fe; font-size: 11px; text-transform: uppercase;
                letter-spacing: .1em; margin: 0 0 6px;">Your free resource</p>
      <h1 style="color: #fff; font-size: 22px; margin: 0; line-height: 1.3;">
        {attachment.title}
      </h1>
    </div>
    <div style="padding: 32px 40px;">
      <p style="color: #475569; font-size: 15px; line-height: 1.6; margin: 0 0 24px;">
        Your download is ready. Click the button below — the link is valid for <strong>7 days</strong>.
      </p>
      <a href="{download_url}"
         style="display: inline-block; background: #6d28d9; color: #fff;
                font-size: 15px; font-weight: 700; text-decoration: none;
                padding: 14px 28px; border-radius: 8px;">
        Download your cheat sheet &rarr;
      </a>
      <p style="color: #94a3b8; font-size: 12px; margin: 24px 0 0;">
        If the button doesn&rsquo;t work, copy this link into your browser:<br>
        <span style="word-break: break-all;">{download_url}</span>
      </p>
    </div>
    <div style="padding: 20px 40px; border-top: 1px solid #f1f5f9;">
      <p style="color: #cbd5e1; font-size: 11px; margin: 0;">
        You received this because you requested a free resource.
        We may occasionally send you helpful academic resources and offers.
      </p>
    </div>
  </div>
</body>
</html>"""

        # Try Resend first
        resend_key = getattr(settings, "RESEND_API_KEY", None)
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "resources@noreply.com")

        if resend_key:
            try:
                import resend as resend_sdk
                resend_sdk.api_key = resend_key
                resend_sdk.Emails.send({
                    "from": from_email,
                    "to": [email],
                    "subject": subject,
                    "html": html_body,
                })
                return True
            except Exception as exc:
                logger.error("Resend delivery failed: %s", exc)

        # Django email fallback
        try:
            from django.core.mail import send_mail
            send_mail(
                subject=subject,
                message=f"Download your cheat sheet: {download_url}",
                from_email=from_email,
                recipient_list=[email],
                html_message=html_body,
                fail_silently=False,
            )
            return True
        except Exception as exc:
            logger.error("Django email delivery failed: %s", exc)
            return False

    # ── Utilities ─────────────────────────────────────────────────────────────

    @staticmethod
    def _get_ip(request: "HttpRequest") -> str | None:
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
