from django.urls import path

from .views import (
    BookmarkPage,
    PageEngagementView,
    ReactToPage,
    SharePage,
    TrackPageView,
)

app_name = "cms_engagement"

urlpatterns = [
    # Summary for a specific page (by Wagtail content_type_id + object_id)
    path(
        "page/<int:content_type_id>/<int:object_id>/",
        PageEngagementView.as_view(),
        name="page-engagement",
    ),
    # Shortcut: resolve by Wagtail page_id  (GET ?page_id=123)
    path(
        "page/",
        PageEngagementView.as_view(),
        name="page-engagement-by-id",
    ),
    path("track-view/", TrackPageView.as_view(), name="track-view"),
    path("react/", ReactToPage.as_view(), name="react"),
    path("share/", SharePage.as_view(), name="share"),
    path("bookmark/", BookmarkPage.as_view(), name="bookmark"),
]
