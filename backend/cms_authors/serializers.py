"""
Author API serializers.

Used by:
- Wagtail API v2 (via api_fields on AuthorPage)
- Custom DRF endpoints if needed
- Schema.org Person JSON-LD generation
"""

from rest_framework import serializers

from cms_authors.models import Author


class AuthorSerializer(serializers.ModelSerializer):
    """Full author representation for API responses."""

    same_as_links = serializers.SerializerMethodField()
    profile_photo_url = serializers.SerializerMethodField()
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            "id",
            "name",
            "slug",
            "bio",
            "credentials",
            "degrees",
            "licenses",
            "areas_of_expertise",
            "years_experience",
            "role",
            "linkedin_url",
            "orcid_id",
            "google_scholar_url",
            "personal_website",
            "profile_photo_url",
            "same_as_links",
            "post_count",
        ]

    def get_same_as_links(self, obj: Author) -> list[str]:
        return obj.get_same_as_links()

    def get_profile_photo_url(self, obj: Author) -> dict | None:
        if obj.profile_photo:
            try:
                return {
                    "url": obj.profile_photo.get_rendition("fill-200x200|format-webp").url,
                    "url_fallback": obj.profile_photo.get_rendition("fill-200x200").url,
                    "width": 200,
                    "height": 200,
                }
            except Exception:
                return None
        return None

    def get_post_count(self, obj: Author) -> int:
        try:
            return obj.blog_posts.live().count()
        except Exception:
            return 0


class AuthorMinimalSerializer(serializers.ModelSerializer):
    """Compact author representation for blog post listings."""

    class Meta:
        model = Author
        fields = [
            "id",
            "name",
            "slug",
            "credentials",
            "role",
        ]


class AuthorSchemaOrgSerializer(serializers.Serializer):
    """Schema.org Person JSON-LD output for an author."""

    def to_representation(self, author: Author) -> dict:
        data = {
            "@type": "Person",
            "name": author.name,
            "description": author.bio[:200] if author.bio else "",
            "jobTitle": author.get_role_display(),
        }

        if author.credentials:
            data["honorificSuffix"] = author.credentials

        same_as = author.get_same_as_links()
        if same_as:
            data["sameAs"] = same_as

        if author.profile_photo:
            try:
                data["image"] = author.profile_photo.get_rendition(
                    "fill-400x400"
                ).url
            except Exception:
                pass

        return data