# writer_management/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from writer_management.views.badge_analytics import BadgeAnalyticsViewSet, BadgeAchievementViewSet, BadgePerformanceViewSet
from writer_management.views import (
    WriterProfileViewSet,
    WriterConfigViewSet,
    WriterLevelConfigViewSet,
    WriterOrderRequestViewSet,
    WriterOrderTakeViewSet,
    WriterSupportTicketViewSet,
    WriterSuspensionViewSet,
    WriterDeadlineExtensionRequestViewSet,
)
# Import WriterStatusViewSet from main views.py (not from views/__init__.py)
# This is needed because WriterStatusViewSet is defined in views.py, not views/__init__.py
try:
    import sys
    import os
    import importlib.util
    views_py_path = os.path.join(os.path.dirname(__file__), 'views.py')
    if os.path.exists(views_py_path):
        # Use a unique module name to avoid conflicts with the views/ package
        spec = importlib.util.spec_from_file_location("writer_management.views_legacy", views_py_path)
        if spec and spec.loader:
            views_main = importlib.util.module_from_spec(spec)
            # Don't set __name__ to avoid conflicts - use the unique name from spec
            spec.loader.exec_module(views_main)
            WriterStatusViewSet = getattr(views_main, 'WriterStatusViewSet', None)
        else:
            WriterStatusViewSet = None
    else:
        WriterStatusViewSet = None
except Exception as e:
    # Silently handle import errors - the ViewSet is optional
    WriterStatusViewSet = None
# Import performance views from views package
from writer_management.views import (
    WriterPerformanceSnapshotViewSet, 
    WriterPerformanceDashboardView, 
    WriterLevelViewSet,
)

# Import discipline ViewSets - they may be None if import fails
try:
    from writer_management.views import (
        WriterStrikeViewSet,
        WriterDisciplineConfigViewSet,
        WriterWarningViewSet,
    )
except (ImportError, AttributeError):
    # Fallback: import directly from main views.py if package import fails
    import sys
    import os
    import importlib.util
    # Try to import directly first
    try:
        import writer_management.views as views_main
        WriterStrikeViewSet = views_main.WriterStrikeViewSet
        WriterDisciplineConfigViewSet = views_main.WriterDisciplineConfigViewSet
        WriterWarningViewSet = getattr(views_main, 'WriterWarningViewSet', None)
    except (ImportError, AttributeError):
        # Fallback: import directly from main views.py file
        import sys
        import os
        import importlib.util
        views_py_path = os.path.join(os.path.dirname(__file__), 'views.py')
        if os.path.exists(views_py_path):
            spec = importlib.util.spec_from_file_location("writer_management.views", views_py_path)
            if spec and spec.loader:
                views_main = importlib.util.module_from_spec(spec)
                views_main.__package__ = 'writer_management'
                views_main.__name__ = 'writer_management.views'
                spec.loader.exec_module(views_main)
                WriterStrikeViewSet = views_main.WriterStrikeViewSet
                WriterDisciplineConfigViewSet = views_main.WriterDisciplineConfigViewSet
                WriterWarningViewSet = getattr(views_main, 'WriterWarningViewSet', None)
        else:
            raise ImportError("Could not find writer_management/views.py")
from writer_management.views_dashboard import WriterDashboardViewSet
from writer_management.views_realtime import WriterDashboardRealtimeStream
from writer_management.views_advance import WriterAdvancePaymentRequestViewSet
# Import Tip views from views.tips module
from writer_management.views.tips import TipViewSet, TipListView
# Import new feature ViewSets
from writer_management.views.capacity import WriterCapacityViewSet, EditorWorkloadViewSet
from writer_management.views.feedback import FeedbackViewSet, FeedbackHistoryViewSet
from writer_management.views.portfolio import WriterPortfolioViewSet, PortfolioSampleViewSet
# Import pen name and resource views directly from views.py
try:
    import sys
    import os
    import importlib.util
    views_py_path = os.path.join(os.path.dirname(__file__), 'views.py')
    if os.path.exists(views_py_path):
        spec = importlib.util.spec_from_file_location("writer_management.views_direct", views_py_path)
        if spec and spec.loader:
            views_main = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(views_main)
            WriterPenNameChangeRequestViewSet = getattr(views_main, 'WriterPenNameChangeRequestViewSet', None)
            WriterResourceViewSet = getattr(views_main, 'WriterResourceViewSet', None)
            WriterResourceCategoryViewSet = getattr(views_main, 'WriterResourceCategoryViewSet', None)
        else:
            WriterPenNameChangeRequestViewSet = None
            WriterResourceViewSet = None
            WriterResourceCategoryViewSet = None
    else:
        WriterPenNameChangeRequestViewSet = None
        WriterResourceViewSet = None
        WriterResourceCategoryViewSet = None
except (ImportError, AttributeError, Exception) as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Failed to import writer resource viewsets: {e}")
    WriterPenNameChangeRequestViewSet = None
    WriterResourceViewSet = None
    WriterResourceCategoryViewSet = None

# app_name removed to allow explicit namespaces in main urls.py
# app_name = "writer_management"

# Create router for badge analytics
router = DefaultRouter()
router.register(r'badge-analytics', BadgeAnalyticsViewSet, basename='badge-analytics')
router.register(r'badge-achievements', BadgeAchievementViewSet, basename='badge-achievements')
router.register(r'badge-performance', BadgePerformanceViewSet, basename='badge-performance')
router.register(r'writers', WriterProfileViewSet, basename='writers')
router.register(r'writer-configs', WriterConfigViewSet, basename='writer-configs')
router.register(r'writer-level-configs', WriterLevelConfigViewSet, basename='writer-level-configs')
router.register(r'writer-levels', WriterLevelViewSet, basename='writer-levels')
router.register(r'writer-order-requests', WriterOrderRequestViewSet, basename='writer-order-requests')
router.register(r'writer-order-takes', WriterOrderTakeViewSet, basename='writer-order-takes')
router.register(r'writer-support-tickets', WriterSupportTicketViewSet, basename='writer-support-tickets')
router.register(r'writer-suspensions', WriterSuspensionViewSet, basename='writer-suspensions')
if WriterStrikeViewSet:
    router.register(r'writer-strikes', WriterStrikeViewSet, basename='writer-strikes')
if WriterDisciplineConfigViewSet:
    router.register(r'writer-discipline-configs', WriterDisciplineConfigViewSet, basename='writer-discipline-configs')
if WriterWarningViewSet:
    router.register(r'writer-warnings', WriterWarningViewSet, basename='writer-warnings')
if WriterStatusViewSet:
    router.register(r'writer-status', WriterStatusViewSet, basename='writer-status')
router.register(r'writer-deadline-extension-requests', WriterDeadlineExtensionRequestViewSet, basename='writer-deadline-extension-requests')
router.register(r'writer-performance-snapshots', WriterPerformanceSnapshotViewSet, basename='writer-performance-snapshots')
router.register(r'dashboard', WriterDashboardViewSet, basename='writer-dashboard')
router.register(r'advance-payments', WriterAdvancePaymentRequestViewSet, basename='advance-payments')
router.register(r'tips', TipViewSet, basename='tips')
if WriterPenNameChangeRequestViewSet:
    router.register(r'pen-name-change-requests', WriterPenNameChangeRequestViewSet, basename='pen-name-change-requests')
if WriterResourceViewSet:
    router.register(r'writer-resources', WriterResourceViewSet, basename='writer-resources')
if WriterResourceCategoryViewSet:
    router.register(r'writer-resource-categories', WriterResourceCategoryViewSet, basename='writer-resource-categories')
router.register(r'writer-capacity', WriterCapacityViewSet, basename='writer-capacity')
router.register(r'editor-workload', EditorWorkloadViewSet, basename='editor-workload')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'feedback-history', FeedbackHistoryViewSet, basename='feedback-history')
router.register(r'writer-portfolios', WriterPortfolioViewSet, basename='writer-portfolio')
router.register(r'portfolio-samples', PortfolioSampleViewSet, basename='portfolio-sample')

urlpatterns = [
    path('', include(router.urls)),
    path('writer-performance-dashboard/<int:pk>/', WriterPerformanceDashboardView.as_view(), name='writer-performance-dashboard'),
    # Legacy endpoint for backward compatibility
    path('tips/list/', TipListView.as_view(), name='tip-list'),
    path('dashboard/realtime/stream/', WriterDashboardRealtimeStream.as_view(), name='writer-dashboard-realtime'),
]