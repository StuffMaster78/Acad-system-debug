"""
Blog serializers - import all serializers here.
"""
from .enhanced_serializers import (
    CTABlockSerializer,
    BlogCTAPlacementSerializer,
    ContentBlockTemplateSerializer,
    BlogContentBlockSerializer,
    BlogEditHistorySerializer,
    BlogSEOMetadataSerializer,
    FAQSchemaSerializer,
    AuthorSchemaSerializer,
    EnhancedBlogPostSerializer,
)

# Import legacy serializers from serializers_legacy.py file
import os
import sys
import importlib.util

def _import_legacy_serializers():
    """Import legacy serializers from serializers_legacy.py"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)  # blog_pages_management/
    legacy_serializers_path = os.path.join(parent_dir, 'serializers_legacy.py')
    
    if not os.path.exists(legacy_serializers_path):
        return None
    
    spec = importlib.util.spec_from_file_location("blog_pages_management.serializers_legacy", legacy_serializers_path)
    if spec is None or spec.loader is None:
        return None
    
    module = importlib.util.module_from_spec(spec)
    module.__package__ = "blog_pages_management"
    module.__name__ = "blog_pages_management.serializers_legacy"
    spec.loader.exec_module(module)
    
    return module

# Import legacy serializers
_legacy_serializers_module = _import_legacy_serializers()

if _legacy_serializers_module:
    BlogCategorySerializer = _legacy_serializers_module.BlogCategorySerializer
    BlogTagSerializer = _legacy_serializers_module.BlogTagSerializer
    BlogResourceSerializer = _legacy_serializers_module.BlogResourceSerializer
    BlogFAQSerializer = _legacy_serializers_module.BlogFAQSerializer
    AuthorProfileSerializer = _legacy_serializers_module.AuthorProfileSerializer
    BlogPostSerializer = _legacy_serializers_module.BlogPostSerializer
    BlogMediaFileSerializer = _legacy_serializers_module.BlogMediaFileSerializer
    BlogClickSerializer = _legacy_serializers_module.BlogClickSerializer
    BlogConversionSerializer = _legacy_serializers_module.BlogConversionSerializer
    NewsletterCategorySerializer = _legacy_serializers_module.NewsletterCategorySerializer
    NewsletterSubscriberSerializer = _legacy_serializers_module.NewsletterSubscriberSerializer
    NewsletterSerializer = _legacy_serializers_module.NewsletterSerializer
    NewsletterAnalyticsSerializer = _legacy_serializers_module.NewsletterAnalyticsSerializer
    BlogVideoSerializer = _legacy_serializers_module.BlogVideoSerializer
    BlogDarkModeImageSerializer = _legacy_serializers_module.BlogDarkModeImageSerializer
    BlogABTestSerializer = _legacy_serializers_module.BlogABTestSerializer
    SocialPlatformSerializer = _legacy_serializers_module.SocialPlatformSerializer
    BlogShareSerializer = _legacy_serializers_module.BlogShareSerializer
    BlogShareURLSerializer = _legacy_serializers_module.BlogShareURLSerializer
    AdminNotificationSerializer = _legacy_serializers_module.AdminNotificationSerializer
else:
    raise ImportError("Could not import legacy serializers from serializers_legacy.py")

__all__ = [
    # Enhanced serializers
    'CTABlockSerializer',
    'BlogCTAPlacementSerializer',
    'ContentBlockTemplateSerializer',
    'BlogContentBlockSerializer',
    'BlogEditHistorySerializer',
    'BlogSEOMetadataSerializer',
    'FAQSchemaSerializer',
    'AuthorSchemaSerializer',
    'EnhancedBlogPostSerializer',
    # Existing serializers
    'BlogCategorySerializer',
    'BlogTagSerializer',
    'BlogResourceSerializer',
    'BlogFAQSerializer',
    'AuthorProfileSerializer',
    'BlogPostSerializer',
    'BlogMediaFileSerializer',
    'BlogClickSerializer',
    'BlogConversionSerializer',
    'NewsletterCategorySerializer',
    'NewsletterSubscriberSerializer',
    'NewsletterSerializer',
    'NewsletterAnalyticsSerializer',
    'BlogVideoSerializer',
    'BlogDarkModeImageSerializer',
    'BlogABTestSerializer',
    'SocialPlatformSerializer',
    'BlogShareSerializer',
    'BlogShareURLSerializer',
    'AdminNotificationSerializer',
]

