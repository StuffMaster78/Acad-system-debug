from __future__ import annotations

from rest_framework import serializers

from reviews_system.models import OrderReview, WebsiteReview, WriterReview


class WriterReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.SerializerMethodField()
    writer_name = serializers.SerializerMethodField()

    class Meta:
        model = WriterReview
        fields = [
            "id", "reviewer", "reviewer_name",
            "writer", "writer_name",
            "website", "rating", "comment", "origin",
            "is_approved", "is_flagged", "is_shadowed",
            "submitted_at", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_reviewer_name(self, obj) -> str:
        return obj.reviewer.get_full_name() or obj.reviewer.username

    def get_writer_name(self, obj) -> str:
        return obj.writer.get_full_name() or obj.writer.username


class WebsiteReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = WebsiteReview
        fields = [
            "id", "reviewer", "reviewer_name",
            "website", "rating", "comment", "origin",
            "is_approved", "is_flagged", "is_shadowed",
            "submitted_at", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_reviewer_name(self, obj) -> str:
        return obj.reviewer.get_full_name() or obj.reviewer.username


class OrderReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.SerializerMethodField()
    writer_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderReview
        fields = [
            "id", "reviewer", "reviewer_name",
            "order", "writer", "writer_name",
            "website", "rating", "comment", "origin",
            "is_approved", "is_flagged", "is_shadowed",
            "submitted_at", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_reviewer_name(self, obj) -> str:
        return obj.reviewer.get_full_name() or obj.reviewer.username

    def get_writer_name(self, obj) -> str:
        if obj.writer:
            return obj.writer.get_full_name() or obj.writer.username
        return ""
