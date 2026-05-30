from __future__ import annotations

from typing import Any

from django.db.models import Count, Sum, Q
from django.utils import timezone


class ClientDashboardService:
    """
    Aggregates all data needed for a client's dashboard landing page.

    Designed for a single database round-trip per section so the
    dashboard loads fast even for high-volume clients.
    """

    def __init__(self, *, client):
        self.client = client

    def get_snapshot(self) -> dict[str, Any]:
        """
        Return the full dashboard snapshot.

        Sections:
            profile       — identity, tier, points, account status
            orders        — counts by lifecycle state + active list
            wallet        — balance
            loyalty       — tier progress summary
            recent_activity — last 10 activity log entries
            alerts        — unread suspicious logins + account flags
        """
        return {
            "profile": self._profile_section(),
            "orders": self._orders_section(),
            "wallet": self._wallet_section(),
            "loyalty": self._loyalty_section(),
            "recent_activity": self._recent_activity_section(),
            "alerts": self._alerts_section(),
        }

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def _profile_section(self) -> dict[str, Any]:
        client = self.client
        return {
            "registration_id": client.registration_id,
            "is_active": client.is_active,
            "is_suspended": client.is_suspended,
            "is_guest": client.is_guest,
            "timezone": client.timezone,
            "country": client.country,
            "date_joined": client.date_joined.isoformat()
            if client.date_joined
            else None,
            "last_online": client.last_online.isoformat()
            if client.last_online
            else None,
            "tier": getattr(client.tier, "name", None),
        }

    def _orders_section(self) -> dict[str, Any]:
        try:
            from orders.models import Order
            from orders.models.orders.enums import OrderStatus
        except ImportError:
            return {"total": 0, "active": 0, "completed": 0, "counts_by_status": {}}

        qs = Order.objects.filter(
            client=self.client.user,
            website=self.client.website,
        )
        agg = qs.aggregate(
            total=Count("id"),
            total_spent=Sum("total_price"),
        )
        status_counts = {
            row["status"]: row["count"]
            for row in qs.values("status").annotate(count=Count("id"))
        }

        active_statuses = {
            OrderStatus.IN_PROGRESS.value,
            OrderStatus.SUBMITTED.value,
            OrderStatus.READY_FOR_STAFFING.value,
            OrderStatus.PENDING_PAYMENT.value,
        }

        return {
            "total": agg["total"] or 0,
            "total_spent": str(agg["total_spent"] or "0.00"),
            "active": sum(
                status_counts.get(s, 0) for s in active_statuses
            ),
            "completed": status_counts.get(OrderStatus.COMPLETED.value, 0),
            "counts_by_status": status_counts,
        }

    def _wallet_section(self) -> dict[str, Any]:
        try:
            balance = self.client.wallet_balance
            return {"balance": str(balance) if balance is not None else "0.00"}
        except Exception:
            return {"balance": "0.00"}

    def _loyalty_section(self) -> dict[str, Any]:
        from client_management.services.client_analytics_service import (
            ClientAnalyticsService,
        )
        analytics = ClientAnalyticsService(client=self.client, days=365)
        tier_data = analytics.get_tier_progression()
        tx_data = analytics.get_loyalty_transaction_summary()
        return {**tier_data, "loyalty_summary": tx_data}

    def _recent_activity_section(self) -> list[dict]:
        from client_management.models import ClientActivityLog

        entries = (
            ClientActivityLog.objects.filter(client=self.client)
            .order_by("-timestamp")[:10]
        )
        return [
            {
                "action": e.action,
                "timestamp": e.timestamp.isoformat(),
            }
            for e in entries
        ]

    def _alerts_section(self) -> dict[str, Any]:
        from client_management.models import SuspiciousLogin

        recent_suspicious = (
            SuspiciousLogin.objects.filter(client=self.client)
            .order_by("-timestamp")[:5]
        )
        return {
            "suspicious_login_count": SuspiciousLogin.objects.filter(
                client=self.client
            ).count(),
            "recent_suspicious_logins": [
                {
                    "ip_address": s.ip_address,
                    "detected_country": s.detected_country,
                    "timestamp": s.timestamp.isoformat(),
                }
                for s in recent_suspicious
            ],
            "is_suspended": self.client.is_suspended,
            "is_locked": self.client.is_locked,
        }
