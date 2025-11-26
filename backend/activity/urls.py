from rest_framework.routers import DefaultRouter

from activity.views import ActivityLogViewSet, UserActivityFeedViewSet

router = DefaultRouter()
router.register(r"activity-logs", ActivityLogViewSet, basename="activity-log")
router.register(r"user-feed", UserActivityFeedViewSet, basename="user-activity-feed")

urlpatterns = router.urls
