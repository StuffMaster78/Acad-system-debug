from django.urls import path

from cms_newsletters.views import (
    SubscribeView,
    SubscriberStatsView,
    UnsubscribeView,
    AdminSubscriberListView,
    AdminSubscriberActionView,
    AdminNewsletterListView,
    AdminNewsletterDetailView,
    AdminSubscriberCategoryListView,
)

app_name = "cms_newsletters"

urlpatterns = [
    # Public
    path("subscribe/", SubscribeView.as_view(), name="subscribe"),
    path("unsubscribe/", UnsubscribeView.as_view(), name="unsubscribe"),
    path("stats/", SubscriberStatsView.as_view(), name="stats"),

    # Admin — subscribers
    path("admin/subscribers/", AdminSubscriberListView.as_view(), name="admin-subscribers"),
    path("admin/subscribers/<int:pk>/<str:action>/", AdminSubscriberActionView.as_view(), name="admin-subscriber-action"),

    # Admin — newsletters
    path("admin/newsletters/", AdminNewsletterListView.as_view(), name="admin-newsletters"),
    path("admin/newsletters/<int:pk>/", AdminNewsletterDetailView.as_view(), name="admin-newsletter-detail"),

    # Admin — categories
    path("admin/categories/", AdminSubscriberCategoryListView.as_view(), name="admin-categories"),
]
