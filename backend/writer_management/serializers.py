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

    def get_order_earnings(self, obj):
        return self._events_for_type(obj, "ORDER_EARNING")

    def get_special_order_earnings(self, obj):
        return self._events_for_type(obj, "SPECIAL_ORDER_EARNING")

    def get_class_earnings(self, obj):
        return self._events_for_type(obj, "CLASS_EARNING")
