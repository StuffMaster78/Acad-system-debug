from rest_framework import serializers
from event_system.models.event_outbox import EventOutbox


class EventOutboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventOutbox
        fields = "__all__"