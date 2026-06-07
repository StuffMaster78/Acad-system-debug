"""
writer_management/api/urls.py

Complete URL configuration for writer_management API.

MOUNT IN ROOT urls.py:
    path(
        "api/writer-management/",
        include("writer_management.api.urls", namespace="writer_management"),
    ),

FULL ROUTE MAP
--------------
Profile (admin):
    GET writers/ list all writers
    GET writers/<rid>/ writer detail
    GET writers/<uuid>/card/ public client card
    POST writers/<rid>/delete/ soft delete
    POST writers/<rid>/restore/ restore

My Profile (writer):
    GET me/profile/ own profile
    PATCH me/profile/ update own profile

Availability (writer):
    GET me/availability/ active + upcoming windows
    POST me/availability/declare/ declare unavailability
    POST me/availability/<pk>/end/ end window early
    POST me/availability/toggle/ toggle is_accepting_orders
    PATCH me/availability/preferences/ update preferences

Discipline (admin):
    GET writers/<rid>/discipline/
    GET writers/<rid>/warnings/
    POST writers/<rid>/warnings/issue/
    POST warnings/<pk>/void/
    GET writers/<rid>/strikes/
    POST writers/<rid>/strikes/issue/
    POST strikes/<pk>/void/
    POST writers/<rid>/suspend/
    POST writers/<rid>/lift-suspension/
    POST writers/<rid>/blacklist/
    POST writers/<rid>/lift-blacklist/
    POST writers/<rid>/probation/
    POST writers/<rid>/penalties/

Performance (admin + writer owner):
    GET writers/<rid>/performance/
    GET writers/<rid>/performance/snapshots/
    GET writers/<rid>/performance/metrics/

Rewards (admin + writer owner):
    GET writers/<rid>/rewards/

Notes (admin):
    GET writers/<rid>/notes/
    POST writers/<rid>/notes/
    PATCH notes/<pk>/
    DELETE notes/<pk>/
    POST notes/<pk>/pin/

Resources (writer):
    GET resources/
    GET resources/<pk>/
    POST resources/<pk>/download/

Applications (router):
    GET applications/ admin list
    GET applications/<pk>/ admin detail
    POST applications/submit/ public submit
    POST applications/<pk>/review/ admin mark under review
    POST applications/<pk>/approve/ admin approve
    POST applications/<pk>/reject/ admin reject
    POST applications/<pk>/withdraw/ applicant withdraw
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from writer_management.api.views.profile_views import (
    WriterProfileListView,
    WriterProfileDetailView,
    MyWriterProfileView,
    WriterPublicCardView,
    SoftDeleteWriterView,
    RestoreWriterView,
)
from writer_management.api.views.discipline_views import (
    WriterDisciplineStateView,
    WriterWarningListView,
    IssueWarningView,
    VoidWarningView,
    WriterStrikeListView,
    IssueStrikeView,
    VoidStrikeView,
    SuspendWriterView,
    LiftSuspensionView,
    BlacklistWriterView,
    LiftBlacklistView,
    PlaceProbationView,
    ApplyPenaltyView,
)
from writer_management.api.views.availability_views import (
    MyAvailabilityView,
    DeclareUnavailableView,
    EndAvailabilityWindowView,
    ToggleAcceptingOrdersView,
    UpdateAvailabilityPreferencesView,
)
from writer_management.api.views.performance_views import (
    WriterPerformanceView,
    WriterPerformanceSnapshotListView,
    WriterMetricsListView,
)
from writer_management.api.views.reward_views import WriterRewardListView
from writer_management.api.views.badge_views import (
    AdminBadgeListView,
    AdminWriterBadgeAwardView,
    AdminWriterBadgeRevokeView,
    AdminWriterBadgeListView,
)
from writer_management.api.views.note_views import (
    WriterNoteListView,
    CreateWriterNoteView,
    UpdateWriterNoteView,
    TogglePinNoteView,
)
from writer_management.api.views.resource_views import (
    AdminWriterResourceCategoryListCreateView,
    AdminWriterResourceDetailView,
    AdminWriterResourceListCreateView,
    WriterResourceListView,
    WriterResourceDetailView,
    DownloadResourceView,
)
from writer_management.api.views.application_views import (
    WriterApplicationViewSet,
)

app_name = "writer_management"

router = DefaultRouter()
router.register(
    "applications",
    WriterApplicationViewSet,
    basename="writer-application",
)

urlpatterns = [

    # ----------------------------------------------------------------
    # WRITER LIST / DETAIL (admin)
    # ----------------------------------------------------------------
    path(
        "writers/",
        WriterProfileListView.as_view(),
        name="writer-list",
    ),
    path(
        "writers/<str:registration_id>/",
        WriterProfileDetailView.as_view(),
        name="writer-detail",
    ),
    path(
        "writers/<uuid:public_uuid>/card/",
        WriterPublicCardView.as_view(),
        name="writer-public-card",
    ),
    path(
        "writers/<str:registration_id>/delete/",
        SoftDeleteWriterView.as_view(),
        name="writer-delete",
    ),
    path(
        "writers/<str:registration_id>/restore/",
        RestoreWriterView.as_view(),
        name="writer-restore",
    ),

    # ----------------------------------------------------------------
    # MY PROFILE (writer)
    # ----------------------------------------------------------------
    path(
        "me/profile/",
        MyWriterProfileView.as_view(),
        name="my-profile",
    ),

    # ----------------------------------------------------------------
    # AVAILABILITY (writer)
    # ----------------------------------------------------------------
    path(
        "me/availability/",
        MyAvailabilityView.as_view(),
        name="my-availability",
    ),
    path(
        "me/availability/declare/",
        DeclareUnavailableView.as_view(),
        name="availability-declare",
    ),
    path(
        "me/availability/<int:pk>/end/",
        EndAvailabilityWindowView.as_view(),
        name="availability-end-window",
    ),
    path(
        "me/availability/toggle/",
        ToggleAcceptingOrdersView.as_view(),
        name="availability-toggle",
    ),
    path(
        "me/availability/preferences/",
        UpdateAvailabilityPreferencesView.as_view(),
        name="availability-preferences",
    ),

    # ----------------------------------------------------------------
    # DISCIPLINE (admin)
    # ----------------------------------------------------------------
    path(
        "writers/<str:registration_id>/discipline/",
        WriterDisciplineStateView.as_view(),
        name="writer-discipline-state",
    ),
    path(
        "writers/<str:registration_id>/warnings/",
        WriterWarningListView.as_view(),
        name="writer-warning-list",
    ),
    path(
        "writers/<str:registration_id>/warnings/issue/",
        IssueWarningView.as_view(),
        name="writer-warning-issue",
    ),
    path(
        "warnings/<int:pk>/void/",
        VoidWarningView.as_view(),
        name="writer-warning-void",
    ),
    path(
        "writers/<str:registration_id>/strikes/",
        WriterStrikeListView.as_view(),
        name="writer-strike-list",
    ),
    path(
        "writers/<str:registration_id>/strikes/issue/",
        IssueStrikeView.as_view(),
        name="writer-strike-issue",
    ),
    path(
        "strikes/<int:pk>/void/",
        VoidStrikeView.as_view(),
        name="writer-strike-void",
    ),
    path(
        "writers/<str:registration_id>/suspend/",
        SuspendWriterView.as_view(),
        name="writer-suspend",
    ),
    path(
        "writers/<str:registration_id>/lift-suspension/",
        LiftSuspensionView.as_view(),
        name="writer-lift-suspension",
    ),
    path(
        "writers/<str:registration_id>/blacklist/",
        BlacklistWriterView.as_view(),
        name="writer-blacklist",
    ),
    path(
        "writers/<str:registration_id>/lift-blacklist/",
        LiftBlacklistView.as_view(),
        name="writer-lift-blacklist",
    ),
    path(
        "writers/<str:registration_id>/probation/",
        PlaceProbationView.as_view(),
        name="writer-probation",
    ),
    path(
        "writers/<str:registration_id>/penalties/",
        ApplyPenaltyView.as_view(),
        name="writer-penalty",
    ),

    # ----------------------------------------------------------------
    # PERFORMANCE (admin + writer owner)
    # ----------------------------------------------------------------
    path(
        "writers/<str:registration_id>/performance/",
        WriterPerformanceView.as_view(),
        name="writer-performance",
    ),
    path(
        "writers/<str:registration_id>/performance/snapshots/",
        WriterPerformanceSnapshotListView.as_view(),
        name="writer-performance-snapshots",
    ),
    path(
        "writers/<str:registration_id>/performance/metrics/",
        WriterMetricsListView.as_view(),
        name="writer-performance-metrics",
    ),

    # ----------------------------------------------------------------
    # REWARDS (admin + writer owner)
    # ----------------------------------------------------------------
    path(
        "writers/<str:registration_id>/rewards/",
        WriterRewardListView.as_view(),
        name="writer-reward-list",
    ),

    # ----------------------------------------------------------------
    # NOTES (admin)
    # ----------------------------------------------------------------
    path(
        "writers/<str:registration_id>/notes/",
        WriterNoteListView.as_view(),
        name="writer-note-list",
    ),
    path(
        "writers/<str:registration_id>/notes/create/",
        CreateWriterNoteView.as_view(),
        name="writer-note-create",
    ),
    path(
        "notes/<int:pk>/",
        UpdateWriterNoteView.as_view(),
        name="writer-note-detail",
    ),
    path(
        "notes/<int:pk>/pin/",
        TogglePinNoteView.as_view(),
        name="writer-note-pin",
    ),

    # ----------------------------------------------------------------
    # RESOURCES (admin + writer)
    # ----------------------------------------------------------------
    path(
        "admin/resource-categories/",
        AdminWriterResourceCategoryListCreateView.as_view(),
        name="admin-resource-category-list",
    ),
    path(
        "admin/resources/",
        AdminWriterResourceListCreateView.as_view(),
        name="admin-resource-list",
    ),
    path(
        "admin/resources/<int:pk>/",
        AdminWriterResourceDetailView.as_view(),
        name="admin-resource-detail",
    ),
    path(
        "resources/",
        WriterResourceListView.as_view(),
        name="resource-list",
    ),
    path(
        "resources/<int:pk>/",
        WriterResourceDetailView.as_view(),
        name="resource-detail",
    ),
    path(
        "resources/<int:pk>/download/",
        DownloadResourceView.as_view(),
        name="resource-download",
    ),

    # ----------------------------------------------------------------
    # BADGES
    # ----------------------------------------------------------------
    path(
        "badges/",
        AdminBadgeListView.as_view(),
        name="badge-list",
    ),
    path(
        "writers/<str:registration_id>/badges/",
        AdminWriterBadgeListView.as_view(),
        name="writer-badge-list",
    ),
    path(
        "writers/<str:registration_id>/badges/award/",
        AdminWriterBadgeAwardView.as_view(),
        name="writer-badge-award",
    ),
    path(
        "writer-badges/<int:pk>/revoke/",
        AdminWriterBadgeRevokeView.as_view(),
        name="writer-badge-revoke",
    ),

    # ----------------------------------------------------------------
    # APPLICATIONS (router handles CRUD + custom actions)
    # ----------------------------------------------------------------
    path("", include(router.urls)),
]
