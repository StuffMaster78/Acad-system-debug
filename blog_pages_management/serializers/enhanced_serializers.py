"""
Enhanced serializers for CMS features - CTAs, Content Blocks, SEO, Edit History.
"""
from rest_framework import serializers
from ..models.content_blocks import (
    CTABlock, BlogCTAPlacement, ContentBlockTemplate, BlogContentBlock, BlogEditHistory
)
from ..models.seo_models import BlogSEOMetadata, FAQSchema, AuthorSchema
from ..models.pdf_samples import PDFSampleSection
from ..serializers.pdf_serializers import PDFSampleSectionSerializer
try:
    from ..models import BlogPost, AuthorProfile
except ImportError:
    from blog_pages_management.models import BlogPost, AuthorProfile


class CTABlockSerializer(serializers.ModelSerializer):
    """Serializer for CTA blocks."""
    
    class Meta:
        model = CTABlock
        fields = [
            'id', 'website', 'name', 'cta_type', 'title', 'description',
            'button_text', 'button_url', 'style', 'background_color', 'text_color',
            'custom_html', 'image', 'is_active', 'display_order',
            'conversion_goal', 'tracking_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class BlogCTAPlacementSerializer(serializers.ModelSerializer):
    """Serializer for CTA placements in blogs."""
    cta_block = CTABlockSerializer(read_only=True)
    cta_block_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = BlogCTAPlacement
        fields = [
            'id', 'blog', 'cta_block', 'cta_block_id', 'placement_type',
            'position', 'is_active', 'display_conditions',
            'click_count', 'conversion_count', 'created_at'
        ]
        read_only_fields = ['click_count', 'conversion_count', 'created_at']


class ContentBlockTemplateSerializer(serializers.ModelSerializer):
    """Serializer for content block templates."""
    
    class Meta:
        model = ContentBlockTemplate
        fields = [
            'id', 'website', 'name', 'block_type', 'content',
            'template_data', 'css_classes', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class BlogContentBlockSerializer(serializers.ModelSerializer):
    """Serializer for content blocks in blog posts."""
    template = ContentBlockTemplateSerializer(read_only=True)
    template_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = BlogContentBlock
        fields = [
            'id', 'blog', 'template', 'template_id', 'position',
            'auto_insert', 'custom_data', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']


class BlogEditHistorySerializer(serializers.ModelSerializer):
    """Serializer for blog edit history."""
    edited_by_username = serializers.CharField(source='edited_by.username', read_only=True)
    
    class Meta:
        model = BlogEditHistory
        fields = [
            'id', 'blog', 'edited_by', 'edited_by_username',
            'previous_content', 'current_content', 'changes_summary',
            'fields_changed', 'edit_reason', 'edited_at'
        ]
        read_only_fields = ['edited_at']


class BlogSEOMetadataSerializer(serializers.ModelSerializer):
    """Serializer for blog SEO metadata."""
    
    class Meta:
        model = BlogSEOMetadata
        fields = [
            'id', 'blog', 'article_type', 'article_section', 'keywords',
            'article_published_time', 'article_modified_time', 'article_author_url',
            'og_type', 'og_title', 'og_description', 'og_image', 'og_image_alt',
            'og_url', 'og_site_name', 'twitter_card_type', 'twitter_title',
            'twitter_description', 'twitter_image', 'twitter_site', 'twitter_creator',
            'schema_breadcrumb', 'schema_organization', 'schema_rating',
            'google_news_keywords', 'google_story', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class FAQSchemaSerializer(serializers.ModelSerializer):
    """Serializer for FAQs with Schema.org support."""
    
    class Meta:
        model = FAQSchema
        fields = [
            'id', 'blog', 'question', 'answer', 'question_slug',
            'display_order', 'is_featured', 'upvote_count',
            'accepted_answer', 'author_name', 'date_created', 'date_modified'
        ]
        read_only_fields = ['date_created', 'date_modified']


class AuthorSchemaSerializer(serializers.ModelSerializer):
    """Serializer for author schema data."""
    
    class Meta:
        model = AuthorSchema
        fields = [
            'id', 'author', 'given_name', 'family_name', 'job_title',
            'works_for', 'email', 'telephone', 'address', 'same_as',
            'knows_about', 'award', 'google_author_id', 'verified_mark',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class EnhancedBlogPostSerializer(serializers.ModelSerializer):
    """Enhanced blog post serializer with all new features."""
    # Existing fields
    authors = serializers.PrimaryKeyRelatedField(
        many=True, queryset=AuthorProfile.objects.all(), required=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=serializers.PrimaryKeyRelatedField(queryset=None), required=False
    )
    
    # New fields
    ctas = BlogCTAPlacementSerializer(many=True, read_only=True)
    content_blocks = BlogContentBlockSerializer(many=True, read_only=True)
    pdf_sample_sections = PDFSampleSectionSerializer(many=True, read_only=True)
    edit_history_count = serializers.SerializerMethodField()
    seo_metadata = BlogSEOMetadataSerializer(read_only=True)
    faqs_schema = FAQSchemaSerializer(many=True, read_only=True, source='faq_schemas')
    
    # Schema.org JSON
    schema_json = serializers.SerializerMethodField()
    og_tags = serializers.SerializerMethodField()
    twitter_tags = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'website', 'title', 'slug', 'content', 'meta_title', 'meta_description',
            'authors', 'tags', 'category', 'featured_image', 'is_published',
            'scheduled_publish_date', 'publish_date', 'created_at', 'updated_at',
            'ctas', 'content_blocks', 'pdf_sample_sections', 'edit_history_count',
            'seo_metadata', 'faqs_schema', 'schema_json', 'og_tags', 'twitter_tags'
        ]
    
    def get_edit_history_count(self, obj):
        """Get count of edit history entries."""
        try:
            from ..models.content_blocks import BlogEditHistory
            return BlogEditHistory.objects.filter(blog=obj).count()
        except Exception:
            return 0
    
    def get_schema_json(self, obj):
        """Get Schema.org structured data."""
        try:
            from ..services.seo_service import SEOService
            return SEOService.get_all_schemas_for_blog(obj)
        except Exception as e:
            return {}
    
    def get_og_tags(self, obj):
        """Get Open Graph meta tags."""
        try:
            from ..services.seo_service import SEOService
            return SEOService.get_open_graph_tags(obj)
        except Exception as e:
            return {}
    
    def get_twitter_tags(self, obj):
        """Get Twitter Card meta tags."""
        try:
            from ..services.seo_service import SEOService
            return SEOService.get_twitter_card_tags(obj)
        except Exception as e:
            return {}

