from rest_framework import serializers


class EventMetricsSerializer(serializers.Serializer):
    """
    System-wide event engine health snapshot.

    Used by:
        - ops dashboard
        - admin monitoring
        - alerting pipelines
    """

    total_events = serializers.IntegerField()
    processed = serializers.IntegerField()
    failed = serializers.IntegerField()
    dead_letter = serializers.IntegerField()
    ignored = serializers.IntegerField()

    processing_rate = serializers.FloatField()
    failure_rate = serializers.FloatField()

    avg_processing_time_ms = serializers.FloatField(allow_null=True)
    last_updated = serializers.DateTimeField(allow_null=True)