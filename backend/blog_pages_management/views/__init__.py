"""
Blog views - import all views here.
"""
from .enhanced_views import (
    CTABlockViewSet,
    BlogCTAPlacementViewSet,
    ContentBlockTemplateViewSet,
    BlogContentBlockViewSet,
    BlogEditHistoryViewSet,
    BlogSEOMetadataViewSet,
    FAQSchemaViewSet,
    AuthorSchemaViewSet,
    EnhancedBlogPostViewSet,
)

# Import legacy views from _legacy_views.py file
import os
import sys
import importlib.util

def _import_legacy_views():
    """Import legacy views from _legacy_views.py"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)  # blog_pages_management/
    legacy_views_path = os.path.join(parent_dir, '_legacy_views.py')
    
    if not os.path.exists(legacy_views_path):
        return None
    
    spec = importlib.util.spec_from_file_location("blog_pages_management._legacy_views", legacy_views_path)
    if spec is None or spec.loader is None:
        return None
    
    module = importlib.util.module_from_spec(spec)
    module.__package__ = "blog_pages_management"
    module.__name__ = "blog_pages_management._legacy_views"
    spec.loader.exec_module(module)
    
    return module

# Import legacy views
_legacy_views_module = _import_legacy_views()

if _legacy_views_module:
    # Import all ViewSets and views from legacy module dynamically
    for name in dir(_legacy_views_module):
        if not name.startswith('_') and (name.endswith('ViewSet') or name.endswith('View')):
            globals()[name] = getattr(_legacy_views_module, name)
    
    # Also import helper functions
    blog_redirect = getattr(_legacy_views_module, 'blog_redirect', None)
    
    # Verify critical views exist
    if not hasattr(_legacy_views_module, 'BlogPostViewSet'):
        raise ImportError("Could not import BlogPostViewSet from _legacy_views.py")
else:
    raise ImportError("Could not import legacy views from _legacy_views.py")

__all__ = [
    # Enhanced views
    'CTABlockViewSet',
    'BlogCTAPlacementViewSet',
    'ContentBlockTemplateViewSet',
    'BlogContentBlockViewSet',
    'BlogEditHistoryViewSet',
    'BlogSEOMetadataViewSet',
    'FAQSchemaViewSet',
    'AuthorSchemaViewSet',
    'EnhancedBlogPostViewSet',
    # Existing views
    'BlogPostViewSet',
    'BlogCategoryViewSet',
    'BlogTagViewSet',
    'AuthorProfileViewSet',
    'BlogClickViewSet',
    'BlogConversionViewSet',
    'BlogResourceViewSet',
    'BlogFAQViewSet',
    'NewsletterCategoryViewSet',
    'NewsletterSubscriberViewSet',
    'NewsletterViewSet',
]

