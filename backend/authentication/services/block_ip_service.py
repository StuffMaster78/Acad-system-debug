# services/BlockIPService.py

from authentication.models.blocked_ips import BlockedIP, BlockedIPLog
from django.utils import timezone
from django.utils.timezone import now, timedelta
import requests

class BlockIPService:
    BLOCK_DURATION_MINUTES = 15

    def is_blocked(self, ip_address):
        """
        Checks if an IP is currently blocked for this website.
        """
        blocked = BlockedIP.objects.filter(
            website=self.website,
            ip_address=ip_address,
            blocked_until__gt=timezone.now()
        ).first()
        return blocked is not None

    def block_ip(
            self,
            ip_address,
            reason="Too many failed attempts",
            duration_minutes=30
    ):
        """
        Blocks the given IP for a duration.
        """
        blocked_until = timezone.now() + timedelta(minutes=duration_minutes)
        BlockedIP.objects.update_or_create(
            website=self.website,
            ip_address=ip_address,
            defaults={"blocked_until": blocked_until}
        )

        BlockedIPLog.objects.create(
            website=self.website,
            ip_address=ip_address,
            reason=reason,
            duration_minutes=duration_minutes
        )

        self._send_admin_alert(ip_address, reason, duration_minutes)

    def unblock_ip(self, ip_address):
        """
        Removes the block on an IP.
        """
        BlockedIP.objects.filter(
            website=self.website,
            ip_address=ip_address
        ).delete()

    def _send_admin_alert(self, ip_address, reason, duration):
        webhook_url = self._get_webhook_url()
        if not webhook_url:
            return

        data = {
            "website_id": self.website.id,
            "ip_address": ip_address,
            "reason": reason,
            "duration": duration,
        }
        try:
            requests.post(webhook_url, json=data, timeout=5)
        except Exception as e:
            # Don't crash if webhook fails
            pass

    def _get_webhook_url(self):
        # Return a webhook URL set per website, or fallback to a global one
        return getattr(
            self.website,
            'security_webhook_url',
            None
        ) or "https://your-default-webhook.com"