from rest_framework import serializers


class TipPolicySnapshotSerializer(serializers.Serializer):
    """
    Immutable snapshot of policy used during tip execution.
    """

    policy_id = serializers.IntegerField()
    writer_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    platform_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2
    )