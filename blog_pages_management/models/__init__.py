"""
Blog pages management models.
All models are imported here for easy access.
"""
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
)
from .security_models import (
    PreviewTokenRateLimit,
    AuditTrail,
)

# Import existing models from main models.py
from ..models import (
    BlogCategory,
    BlogTag,
    BlogResource,
    BlogFAQ,
    AuthorProfile,
    BlogPost,
    BlogMediaFile,
    BlogClick,
    BlogConversion,
    NewsletterCategory,
    NewsletterSubscriber,
    Newsletter,
    NewsletterAnalytics,
    BlogActionLog,
    AdminNotification,
    BlogVideo,
    BlogDarkModeImage,
    BlogABTest,
    SocialPlatform,
    BlogShare,
    BlogSlugHistory,
)

__all__ = [
    # Content Blocks
    'CTABlock',
    'BlogCTAPlacement',
    'ContentBlockTemplate',
    'BlogContentBlock',
    'BlogEditHistory',
    # SEO Models
    'BlogSEOMetadata',
    'FAQSchema',
    'AuthorSchema',
    # Draft & Editing Models
    'BlogPostRevision',
    'BlogPostAutoSave',
    'BlogPostEditLock',
    'BlogPostPreview',
    # Workflow Models
    'BlogPostWorkflow',
    'BlogPostReviewComment',
    'WorkflowTransition',
    'ContentTemplate',
    'ContentSnippet',
    # Analytics Models
    'EditorAnalytics',
    'BlogPostAnalytics',
    'ContentPerformanceMetrics',
    # Security Models
    'PreviewTokenRateLimit',
    'AuditTrail',
    # Existing Models
    'BlogCategory',
    'BlogTag',
    'BlogResource',
    'BlogFAQ',
    'AuthorProfile',
    'BlogPost',
    'BlogMediaFile',
    'BlogClick',
    'BlogConversion',
    'NewsletterCategory',
    'NewsletterSubscriber',
    'Newsletter',
    'NewsletterAnalytics',
    'BlogActionLog',
    'AdminNotification',
    'BlogVideo',
    'BlogDarkModeImage',
    'BlogABTest',
    'SocialPlatform',
    'BlogShare',
    'BlogSlugHistory',
]

