from rest_framework import serializers

from .models import HelpArticle, HelpCategory, LegalDocument


class LegalDocumentSerializer(serializers.ModelSerializer):
    doc_type_display = serializers.CharField(source="get_doc_type_display", read_only=True)

    class Meta:
        model = LegalDocument
        fields = (
            "id", "doc_type", "doc_type_display", "title",
            "content", "version", "effective_date",
            "requires_re_acceptance",
        )


class HelpCategorySerializer(serializers.ModelSerializer):
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = HelpCategory
        fields = (
            "id", "title", "slug", "description",
            "icon", "audience", "order", "article_count",
        )

    def get_article_count(self, obj) -> int:
        return obj.articles.filter(is_published=True).count()


class HelpArticleListSerializer(serializers.ModelSerializer):
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    category_title = serializers.CharField(source="category.title", read_only=True)

    class Meta:
        model = HelpArticle
        fields = (
            "id", "title", "slug", "summary",
            "audience", "is_featured", "category_slug", "category_title",
            "updated_at",
        )


class HelpArticleDetailSerializer(serializers.ModelSerializer):
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    category_title = serializers.CharField(source="category.title", read_only=True)

    class Meta:
        model = HelpArticle
        fields = (
            "id", "title", "slug", "summary", "content",
            "audience", "is_featured", "category_slug", "category_title",
            "updated_at",
        )


class LegalDocumentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalDocument
        fields = (
            "id", "doc_type", "title", "content", "version",
            "effective_date", "is_active", "requires_re_acceptance",
        )
        read_only_fields = ("id",)


class HelpCategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpCategory
        fields = (
            "id", "title", "slug", "description",
            "icon", "audience", "order", "is_active",
        )
        read_only_fields = ("id",)


class HelpArticleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpArticle
        fields = (
            "id", "category", "title", "slug", "summary",
            "content", "audience", "is_featured", "is_published", "order",
        )
        read_only_fields = ("id",)
