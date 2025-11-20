from rest_framework.routers import DefaultRouter
from activity.views import ActivityLogViewSet

router = DefaultRouter()
router.register(r"activity-logs", ActivityLogViewSet, basename="activity-log")

urlpatterns = router.urls
