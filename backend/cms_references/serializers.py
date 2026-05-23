"""
Reference API Serializers
============================
"""

from rest_framework import serializers

from cms_references.models import Citation, Reference, ReferenceTag


class ReferenceTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceTag
        fields = ["id", "name", "slug"]


class ReferenceSerializer(serializers.ModelSerializer):
    tags = ReferenceTagSerializer(many=True, read_only=True)
    display_url = serializers.CharField(read_only=True)
    formatted_authors = serializers.CharField(read_only=True)

    class Meta:
        model = Reference
        fields = [
            "id", "reference_type", "title", "authors", "formatted_authors",
            "publication_year", "publication_month",
            "journal_name", "journal_volume", "journal_issue", "pages",
            "publisher", "organization",
            "doi", "isbn", "pmid",
            "url", "url_archived", "display_url", "is_url_dead",
            "is_open_access", "is_peer_reviewed", "is_verified",
            "quality_tier", "usage_count", "tags",
        ]


class ReferenceCreateSerializer(serializers.ModelSerializer):
    """For creating/updating references. Accepts DOI/PMID for auto-fill."""

    class Meta:
        model = Reference
        fields = [
            "site", "reference_type", "title", "authors",
            "publication_year", "publication_month",
            "journal_name", "journal_volume", "journal_issue", "pages",
            "publisher", "organization",
            "doi", "isbn", "pmid", "url",
            "is_open_access", "is_peer_reviewed", "quality_tier",
            "internal_notes",
        ]


class CitationSerializer(serializers.ModelSerializer):
    reference = ReferenceSerializer(read_only=True)

    class Meta:
        model = Citation
        fields = [
            "id", "blog_post", "reference", "position",
            "page", "editor_note",
        ]


class CitationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citation
        fields = ["blog_post", "reference", "position", "page", "editor_note"]