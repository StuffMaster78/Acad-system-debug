from rest_framework import serializers

from writer_management.models.writer_application import WriterApplication


class WriterApplicationSummarySerializer(serializers.ModelSerializer):
    """Compact list view for admin dashboard."""

    class Meta:
        model = WriterApplication
        fields = [
            "id",
            "full_name",
            "email",
            "country",
            "education_level",
            "years_of_experience",
            "status",
            "submitted_at",
            "reviewed_at",
        ]
        read_only_fields = fields


class WriterApplicationDetailSerializer(serializers.ModelSerializer):
    """Full detail for admin review view."""

    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = WriterApplication
        fields = [
            "id",
            "full_name",
            "email",
            "phone_number",
            "country",
            "education_level",
            "years_of_experience",
            "subjects",
            "application_text",
            "resume",
            "sample_work",
            "status",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "rejection_reason",
            "admin_notes",
            "submitted_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_reviewed_by_name(self, obj) -> str | None:
        user = obj.reviewed_by
        if user is None:
            return None
        return user.get_full_name() or user.email


class SubmitApplicationSerializer(serializers.Serializer):
    """Input for submitting a writer application."""
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone_number = serializers.CharField(
        max_length=30, required=False, allow_blank=True
    )
    country = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    education_level = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    years_of_experience = serializers.IntegerField(min_value=0, default=0)
    subjects = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )
    application_text = serializers.CharField(
        required=False, allow_blank=True
    )
    resume = serializers.FileField(required=False)
    sample_work = serializers.FileField(required=False)


class ApproveApplicationSerializer(serializers.Serializer):
    """Input for approving a writer application."""
    initial_level_id = serializers.IntegerField(
        required=False,
        help_text="Optional WriterLevel PK to assign immediately.",
    )
    require_review = serializers.BooleanField(
        default=True,
        help_text=(
            "If True, AccountProfile.status = UNDER_REVIEW. "
            "If False, status = ACTIVE immediately."
        ),
    )


class RejectApplicationSerializer(serializers.Serializer):
    """Input for rejecting a writer application."""
    rejection_reason = serializers.CharField(min_length=10)
    admin_notes = serializers.CharField(required=False, allow_blank=True)