from __future__ import annotations

from typing import Any

from django.db.models import Count
from django.utils import timezone


class SuspiciousLoginService:
    """
    Manages the suspicious login log for a client profile.

    Suspicious logins are recorded automatically by the login signal
    when the detected country differs from the profile's known country.
    This service provides the review and management layer for ops and
    security staff.
    """

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def list_for_client(*, client, limit: int = 50):
        """Return recent suspicious logins for a client, newest first."""
        from client_management.models import SuspiciousLogin

        return (
            SuspiciousLogin.objects.filter(client=client)
            .order_by("-timestamp")[:limit]
        )

    @staticmethod
    def get_summary(*, client) -> dict[str, Any]:
        """
        Return a summary of suspicious login activity for a client.

        Returns:
            total — total suspicious login events ever recorded
            unique_ips — distinct IPs seen in suspicious events
            countries_seen — distinct detected countries
            last_detected_at — timestamp of most recent event
        """
        from client_management.models import SuspiciousLogin

        qs = SuspiciousLogin.objects.filter(client=client)
        total = qs.count()

        if total == 0:
            return {
                "total": 0,
                "unique_ips": 0,
                "countries_seen": [],
                "last_detected_at": None,
            }

        agg = qs.aggregate(unique_ips=Count("ip_address", distinct=True))
        countries = list(
            qs.values_list("detected_country", flat=True)
            .distinct()
            .order_by("detected_country")
        )
        last = qs.order_by("-timestamp").values("timestamp").first()

        return {
            "total": total,
            "unique_ips": agg["unique_ips"],
            "countries_seen": [c for c in countries if c],
            "last_detected_at": last["timestamp"].isoformat() if last else None,
        }

    @staticmethod
    def has_recent_suspicious_activity(*, client, hours: int = 24) -> bool:
        """Return True if any suspicious logins in the last N hours."""
        from client_management.models import SuspiciousLogin

        cutoff = timezone.now() - __import__("datetime").timedelta(hours=hours)
        return SuspiciousLogin.objects.filter(
            client=client, timestamp__gte=cutoff
        ).exists()

    # ------------------------------------------------------------------
    # Management
    # ------------------------------------------------------------------

    @staticmethod
    def flag_for_review(*, client, reviewed_by, notes: str = "") -> dict[str, Any]:
        """
        Flag a client for security review based on suspicious login
        patterns. Logs an activity entry and notifies support staff.

        This does not suspend the account — use ClientProfileService.suspend()
        for that. This is a soft flag that creates an audit trail.
        """
        from client_management.models import ClientActivityLog

        ClientActivityLog.objects.create(
            client=client,
            action=(
                f"flagged_for_security_review by "
                f"{getattr(reviewed_by, 'email', str(reviewed_by))}"
                + (f": {notes}" if notes else "")
            ),
        )

        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            NotificationService.notify_staff(
                event_key="account.suspicious_login",
                website=client.website,
                context={
                    "client_id": client.pk,
                    "notes": notes,
                    "flagged_by": getattr(reviewed_by, "email", str(reviewed_by)),
                },
                triggered_by=reviewed_by,
            )
        except Exception:
            pass

        return {
            "flagged": True,
            "client_id": client.pk,
            "flagged_by": getattr(reviewed_by, "pk", None),
        }

    @staticmethod
    def clear_history(*, client, cleared_by) -> int:
        """
        Delete all suspicious login records for a client after review.

        Returns the number of records deleted.
        """
        from client_management.models import ClientActivityLog, SuspiciousLogin

        deleted_count, _ = SuspiciousLogin.objects.filter(
            client=client
        ).delete()

        ClientActivityLog.objects.create(
            client=client,
            action=(
                f"suspicious_login_history_cleared by "
                f"{getattr(cleared_by, 'email', str(cleared_by))} "
                f"({deleted_count} records removed)"
            ),
        )

        return deleted_count
