from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    EmailCampaignViewSet,
    EmailRecipientViewSet,
    CampaignAttachmentViewSet,
    EmailTemplateViewSet,
    EmailServiceIntegrationViewSet,
)
from .analytics import views as analytics_views
from .dashboards.campaign import CampaignAnalyticsDashboard
from mass_emails.dashboards.trending import CampaignTrendingAnalytics
from mass_emails.views import UserEmailHistoryView, AdminEmailHistoryView
# Register RESTful ViewSets
router = DefaultRouter()
router.register('campaigns', EmailCampaignViewSet)
router.register('recipients', EmailRecipientViewSet)
router.register('attachments', CampaignAttachmentViewSet)
router.register('templates', EmailTemplateViewSet)
router.register('providers', EmailServiceIntegrationViewSet)

# Main API URLs
urlpatterns = router.urls

# Analytics (open, click) & unsubscribe tracking
urlpatterns += [
    path('track/open/<int:recipient_id>/', analytics_views.track_open, name='email-track-open'),
    path('track/click/<int:recipient_id>/', analytics_views.track_click, name='email-track-click'),
    path('unsubscribe/<int:recipient_id>/', analytics_views.unsubscribe, name='email-unsubscribe'),
    path('analytics/campaigns/', CampaignAnalyticsDashboard.as_view(), name='campaign-analytics'),
    path('analytics/trending/', CampaignTrendingAnalytics.as_view(), name='campaign-trending'),
    path('email-history/', UserEmailHistoryView.as_view(), name='email-history'),
    path('email-history/', UserEmailHistoryView.as_view(), name='user-email-history'),
    path('admin/email-history/', AdminEmailHistoryView.as_view(), name='admin-email-history'),
]