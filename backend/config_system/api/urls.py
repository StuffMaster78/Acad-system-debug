from django.urls import path

from config_system.api.admin_views import (
    ConfigDeleteView,
    ConfigDetailView,
    ConfigListView,
    ConfigRegistryView,
    ConfigUpdateView,
    FeatureCheckView,
)

urlpatterns = [
    path(
        "",
        ConfigListView.as_view(),
        name="config-list",
    ),

    path(
        "registry/",
        ConfigRegistryView.as_view(),
        name="config-registry",
    ),

    path(
        "update/",
        ConfigUpdateView.as_view(),
        name="config-update",
    ),

    path(
        "feature-check/",
        FeatureCheckView.as_view(),
        name="feature-check",
    ),

    path(
        "<str:key>/",
        ConfigDetailView.as_view(),
        name="config-detail",
    ),

    path(
        "<str:key>/delete/",
        ConfigDeleteView.as_view(),
        name="config-delete",
    ),
]