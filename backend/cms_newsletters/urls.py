from django.urls import path

from cms_newsletters.views import (
    SubscribeView,
    SubscriberStatsView,
    UnsubscribeView,
)

app_name = "cms_newsletters"

urlpatterns = [
    path("subscribe/", SubscribeView.as_view(), name="subscribe"),
    path("unsubscribe/", UnsubscribeView.as_view(), name="unsubscribe"),
    path("stats/", SubscriberStatsView.as_view(), name="stats"),
]
