"""
Blog pages management models package.
Contains both legacy models (from _legacy_models.py) and new models from submodules.
"""
import os
import sys
import importlib.util

# Import new models from submodules first
from .content_blocks import (
    CTABlock,
    BlogCTAPlacement,
    ContentBlockTemplate,
    BlogContentBlock,
    BlogEditHistory,
)
from .seo_models import (
    BlogSEOMetadata,
    FAQSchema,
    AuthorSchema,
)
from .pdf_samples import (
    PDFSampleSection,
    PDFSample,
    PDFSampleDownload,
)
from .draft_editing import (
    BlogPostRevision,
    BlogPostAutoSave,
    BlogPostEditLock,
    BlogPostPreview,
)
from .workflow_models import (
    BlogPostWorkflow,
    BlogPostReviewComment,
    WorkflowTransition,
    ContentTemplate,
    ContentSnippet,
)
from .analytics_models import (
    EditorAnalytics,
    BlogPostAnalytics,
    ContentPerformanceMetrics,
    WebsiteContentMetrics,
    WebsitePublishingTarget,
    CategoryPublishingTarget,
    ContentFreshnessReminder,
)
from .editor_usage_tracking import (
    EditorSession,
    EditorAction,
    EditorProductivityMetrics,
)
from .collaborative_editing import (
    CollaborativeSession,
    CollaborativeEditor,
    CollaborativeChange,
    CollaborativePresence,
)
from .security_models import (
    PreviewTokenRateLimit,
    AuditTrail,
)

# Import legacy models from _legacy_models.py
# Use a different approach: import the module directly and extract models
def _import_legacy_models():
    """Import legacy models from _legacy_models.py"""
    # Get the path to _legacy_models.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)  # blog_pages_management/
    legacy_models_path = os.path.join(parent_dir, '_legacy_models.py')
    
    if not os.path.exists(legacy_models_path):
        raise FileNotFoundError(f"Could not find _legacy_models.py at {legacy_models_path}")
    
    # Import using importlib with proper module naming
    spec = importlib.util.spec_from_file_location("blog_pages_management._legacy_models", legacy_models_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create spec for {legacy_models_path}")
    
    # Create module and set __package__ so Django recognizes it
    module = importlib.util.module_from_spec(spec)
    module.__package__ = "blog_pages_management"
    module.__name__ = "blog_pages_management._legacy_models"
    
    # Execute the module
    spec.loader.exec_module(module)
    
    return module

# Import legacy models
_legacy_module = _import_legacy_models()

# Extract and assign legacy models
BlogCategory = _legacy_module.BlogCategory
BlogTag = _legacy_module.BlogTag
BlogResource = _legacy_module.BlogResource
BlogFAQ = _legacy_module.BlogFAQ
AuthorProfile = _legacy_module.AuthorProfile
BlogPost = _legacy_module.BlogPost
BlogMediaFile = _legacy_module.BlogMediaFile
BlogClick = _legacy_module.BlogClick
BlogConversion = _legacy_module.BlogConversion
NewsletterCategory = _legacy_module.NewsletterCategory
NewsletterSubscriber = _legacy_module.NewsletterSubscriber
Newsletter = _legacy_module.Newsletter
NewsletterAnalytics = _legacy_module.NewsletterAnalytics
BlogActionLog = _legacy_module.BlogActionLog
AdminNotification = _legacy_module.AdminNotification
BlogVideo = _legacy_module.BlogVideo
BlogDarkModeImage = _legacy_module.BlogDarkModeImage
BlogABTest = _legacy_module.BlogABTest
SocialPlatform = _legacy_module.SocialPlatform
BlogShare = _legacy_module.BlogShare
BlogSlugHistory = _legacy_module.BlogSlugHistory

# Extract helper functions from legacy module
generate_tracking_id = _legacy_module.generate_tracking_id

# Update __module__ attribute for all legacy models so Django knows they belong to this app
for model_name in [
    'BlogCategory', 'BlogTag', 'BlogResource', 'BlogFAQ', 'AuthorProfile',
    'BlogPost', 'BlogMediaFile', 'BlogClick', 'BlogConversion',
    'NewsletterCategory', 'NewsletterSubscriber', 'Newsletter', 'NewsletterAnalytics',
    'BlogActionLog', 'AdminNotification', 'BlogVideo', 'BlogDarkModeImage',
    'BlogABTest', 'SocialPlatform', 'BlogShare', 'BlogSlugHistory'
]:
    model = globals()[model_name]
    if hasattr(model, '_meta'):
        model._meta.app_label = 'blog_pages_management'
        model.__module__ = 'blog_pages_management.models'

__all__ = [
    # New models from submodules
    'CTABlock', 'BlogCTAPlacement', 'ContentBlockTemplate', 'BlogContentBlock', 'BlogEditHistory',
    'BlogSEOMetadata', 'FAQSchema', 'AuthorSchema',
    'PDFSampleSection', 'PDFSample', 'PDFSampleDownload',
    'BlogPostRevision', 'BlogPostAutoSave', 'BlogPostEditLock', 'BlogPostPreview',
    'BlogPostWorkflow', 'BlogPostReviewComment', 'WorkflowTransition', 'ContentTemplate', 'ContentSnippet',
    'EditorAnalytics', 'BlogPostAnalytics', 'ContentPerformanceMetrics',
    'WebsiteContentMetrics', 'WebsitePublishingTarget', 'CategoryPublishingTarget', 'ContentFreshnessReminder',
    'EditorSession', 'EditorAction', 'EditorProductivityMetrics',
    'CollaborativeSession', 'CollaborativeEditor', 'CollaborativeChange', 'CollaborativePresence',
    'PreviewTokenRateLimit', 'AuditTrail',
    # Legacy models from _legacy_models.py
    'BlogCategory', 'BlogTag', 'BlogResource', 'BlogFAQ', 'AuthorProfile',
    'BlogPost', 'BlogMediaFile', 'BlogClick', 'BlogConversion',
    'NewsletterCategory', 'NewsletterSubscriber', 'Newsletter', 'NewsletterAnalytics',
    'BlogActionLog', 'AdminNotification', 'BlogVideo', 'BlogDarkModeImage',
    'BlogABTest', 'SocialPlatform', 'BlogShare', 'BlogSlugHistory',
]
