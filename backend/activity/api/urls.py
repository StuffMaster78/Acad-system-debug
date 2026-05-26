from __future__ import annotations

from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from activity.api.views import ActivityFeedViewSet

router = DefaultRouter()
router.register(
    "feed",
    ActivityFeedViewSet,
    basename="activity-feed",
)

urlpatterns = [
    path(
        "",
        ActivityFeedViewSet.as_view({"get": "list"}),
        name="activity-list",
    ),
    path("", include(router.urls)),
]
