from rest_framework import serializers


class SubmitDraftSerializer(serializers.Serializer):
    milestone_id = serializers.IntegerField(required=False)
    note = serializers.CharField(required=False, allow_blank=True)


class ReviewDraftSerializer(serializers.Serializer):
    approve = serializers.BooleanField()