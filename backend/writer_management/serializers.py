"""
Top-level serializer shim for writer_management.

Some views import directly from `writer_management.serializers`.  Serializers
that belong to the API layer live under `writer_management/api/serializers/`;
this module re-exports the ones referenced from outside that package.
"""

from rest_framework import serializers

from writer_management.models.configs import WriterConfig


class WriterConfigSerializer(serializers.ModelSerializer):
    """Basic read/write serializer for WriterConfig (site-level writer settings)."""

    class Meta:
        model = WriterConfig
        fields = [
            "id",
            "website",
            "takes_enabled",
            "max_requests_per_writer",
            "max_takes_per_writer",
        ]
        read_only_fields = ["id"]


class WriterPaymentViewSerializer(serializers.Serializer):
    """
    Returns earnings lists for a WriterProfile grouped by source type.

    Queries CompensationEvent — the single source of truth for writer earnings.
    Groups:
      order_earnings         ORDER_EARNING events
      special_order_earnings SPECIAL_ORDER_EARNING events
      class_earnings         CLASS_EARNING events

    Each item: { id, amount, title, reference, source_id, created_at, status }
    """

    order_earnings = serializers.SerializerMethodField()
    special_order_earnings = serializers.SerializerMethodField()
    class_earnings = serializers.SerializerMethodField()

    def _events_for_type(self, writer_profile, *event_types):
        try:
            from writer_compensation.models.compensation_event import CompensationEvent
            events = (
                CompensationEvent.objects
                .filter(
                    writer=writer_profile,
                    event_type__in=event_types,
                    is_visible_to_writer=True,
                )
                .order_by("-created_at")[:50]
            )
            return [
                {
                    "id":         e.id,
                    "amount":     str(e.amount),
                    "title":      e.title,
                    "reference":  e.reference or "",
                    "source_id":  e.source_id,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                    "status":     e.status,
                }
                for e in events
            ]
        except Exception:
            return []

    def _has_any_compensation_events(self, writer_profile) -> bool:
        try:
            from writer_compensation.models.compensation_event import CompensationEvent
            return CompensationEvent.objects.filter(writer=writer_profile).exists()
        except Exception:
            return False

    def _order_earnings_fallback(self, writer_profile) -> list:
        """
        Synthesise order earnings from completed Order rows when no
        CompensationEvent rows exist yet (pre-Celery history).
        """
        try:
            from orders.models.orders.order_assignment import OrderAssignment
            assignments = (
                OrderAssignment.objects
                .filter(writer=writer_profile, is_current=True)
                .select_related("order")
                .filter(order__status="completed")
                .order_by("-order__completed_at")[:50]
            )
            results = []
            for a in assignments:
                order = a.order
                amount = order.writer_compensation or 0
                if not amount:
                    continue
                results.append({
                    "id":         None,
                    "amount":     str(amount),
                    "title":      f"Order #{order.pk}",
                    "reference":  str(order.pk),
                    "source_id":  order.pk,
                    "created_at": order.completed_at.isoformat() if order.completed_at else None,
                    "status":     "matured",
                })
            return results
        except Exception:
            return []

    def get_order_earnings(self, obj):
        events = self._events_for_type(obj, "ORDER_EARNING")
        if not events and not self._has_any_compensation_events(obj):
            return self._order_earnings_fallback(obj)
        return events

    def get_special_order_earnings(self, obj):
        return self._events_for_type(obj, "SPECIAL_ORDER_EARNING")

    def get_class_earnings(self, obj):
        return self._events_for_type(obj, "CLASS_EARNING")
