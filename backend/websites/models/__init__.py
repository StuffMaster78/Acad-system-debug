"""
Websites Models Package
"""
from .websites import Website
from .action_log import WebsiteActionLog
from .static_pages import WebsiteStaticPage
from .website_settings import WebsiteSettings, WebsiteTermsAcceptance, GuestAccessToken, ExternalReviewLink
from .website_niche import WebsiteNiche

try:
    from .tenant_features import TenantBranding, TenantFeatureToggle
except ImportError:
    TenantBranding = None
    TenantFeatureToggle = None

try:
    from .website_branding import WebsiteBranding, PaymentDisclosureAcknowledgement
except ImportError:
    WebsiteBranding = None
    PaymentDisclosureAcknowledgement = None

__all__ = [
    'Website',
    'WebsiteActionLog',
    'WebsiteStaticPage',
    'WebsiteSettings',
    'WebsiteTermsAcceptance',
    'GuestAccessToken',
    'ExternalReviewLink',
    'WebsiteNiche',
    'TenantBranding',
    'TenantFeatureToggle',
    'WebsiteBranding',
    'PaymentDisclosureAcknowledgement',
]
