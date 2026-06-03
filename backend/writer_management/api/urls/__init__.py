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
    MyWriterPerformanceView,
)
from writer_management.api.views.reward_views import WriterRewardListView
from writer_management.api.views.note_views import (
    WriterNoteListView,
    CreateWriterNoteView,
    UpdateWriterNoteView,
    TogglePinNoteView,
)
from writer_management.api.views.resource_views import (
    WriterResourceListView,
    WriterResourceDetailView,
    DownloadResourceView,
)
from writer_management.api.views.application_views import WriterApplicationViewSet
from writer_management.api.views.level_settings_views import (
    WriterLevelListCreateView,
    WriterLevelDetailView,
    WriterLevelSettingsListView,
    WriterLevelSettingsDetailView,
)
from writer_management.api.views.badge_views import (
    AdminBadgeListView,
    AdminWriterBadgeAwardView,
    AdminWriterBadgeRevokeView,
    AdminWriterBadgeListView,
)

router = DefaultRouter()
router.register("applications", WriterApplicationViewSet, basename="writer-application")

urlpatterns = [
    # Profile (admin)
    path("writers/", WriterProfileListView.as_view(), name="writer-list"),
    path("writers/<str:registration_id>/", WriterProfileDetailView.as_view(), name="writer-detail"),
    path("writers/<uuid:public_uuid>/card/", WriterPublicCardView.as_view(), name="writer-public-card"),
    path("writers/<str:registration_id>/delete/", SoftDeleteWriterView.as_view(), name="writer-delete"),
    path("writers/<str:registration_id>/restore/", RestoreWriterView.as_view(), name="writer-restore"),

    # My profile (writer)
    path("me/profile/", MyWriterProfileView.as_view(), name="my-profile"),
    path("me/performance/", MyWriterPerformanceView.as_view(), name="my-performance"),

    # Availability (writer)
    path("me/availability/", MyAvailabilityView.as_view(), name="my-availability"),
    path("me/availability/declare/", DeclareUnavailableView.as_view(), name="availability-declare"),
    path("me/availability/<int:pk>/end/", EndAvailabilityWindowView.as_view(), name="availability-end-window"),
    path("me/availability/toggle/", ToggleAcceptingOrdersView.as_view(), name="availability-toggle"),
    path("me/availability/preferences/", UpdateAvailabilityPreferencesView.as_view(), name="availability-preferences"),

    # Discipline (admin)
    path("writers/<str:registration_id>/discipline/", WriterDisciplineStateView.as_view(), name="writer-discipline-state"),
    path("writers/<str:registration_id>/warnings/", WriterWarningListView.as_view(), name="writer-warning-list"),
    path("writers/<str:registration_id>/warnings/issue/", IssueWarningView.as_view(), name="writer-warning-issue"),
    path("warnings/<int:pk>/void/", VoidWarningView.as_view(), name="writer-warning-void"),
    path("writers/<str:registration_id>/strikes/", WriterStrikeListView.as_view(), name="writer-strike-list"),
    path("writers/<str:registration_id>/strikes/issue/", IssueStrikeView.as_view(), name="writer-strike-issue"),
    path("strikes/<int:pk>/void/", VoidStrikeView.as_view(), name="writer-strike-void"),
    path("writers/<str:registration_id>/suspend/", SuspendWriterView.as_view(), name="writer-suspend"),
    path("writers/<str:registration_id>/lift-suspension/", LiftSuspensionView.as_view(), name="writer-lift-suspension"),
    path("writers/<str:registration_id>/blacklist/", BlacklistWriterView.as_view(), name="writer-blacklist"),
    path("writers/<str:registration_id>/lift-blacklist/", LiftBlacklistView.as_view(), name="writer-lift-blacklist"),
    path("writers/<str:registration_id>/probation/", PlaceProbationView.as_view(), name="writer-probation"),
    path("writers/<str:registration_id>/penalties/", ApplyPenaltyView.as_view(), name="writer-penalty"),

    # Performance (admin + writer owner)
    path("writers/<str:registration_id>/performance/", WriterPerformanceView.as_view(), name="writer-performance"),
    path("writers/<str:registration_id>/performance/snapshots/", WriterPerformanceSnapshotListView.as_view(), name="writer-performance-snapshots"),
    path("writers/<str:registration_id>/performance/metrics/", WriterMetricsListView.as_view(), name="writer-performance-metrics"),

    # Rewards (admin + writer owner)
    path("writers/<str:registration_id>/rewards/", WriterRewardListView.as_view(), name="writer-reward-list"),

    # Notes (admin)
    path("writers/<str:registration_id>/notes/", WriterNoteListView.as_view(), name="writer-note-list"),
    path("writers/<str:registration_id>/notes/create/", CreateWriterNoteView.as_view(), name="writer-note-create"),
    path("notes/<int:pk>/", UpdateWriterNoteView.as_view(), name="writer-note-detail"),
    path("notes/<int:pk>/pin/", TogglePinNoteView.as_view(), name="writer-note-pin"),

    # Resources (writer)
    path("resources/", WriterResourceListView.as_view(), name="resource-list"),
    path("resources/<int:pk>/", WriterResourceDetailView.as_view(), name="resource-detail"),
    path("resources/<int:pk>/download/", DownloadResourceView.as_view(), name="resource-download"),

    # Achievements (writer)
    path("achievements/", include("writer_management.api.urls.achievement_urls")),

    # Writer levels CRUD
    path("levels/",          WriterLevelListCreateView.as_view(), name="level-list-create"),
    path("levels/<int:pk>/", WriterLevelDetailView.as_view(),     name="level-detail"),

    # Level settings (full pay/capacity/eligibility config)
    path("level-settings/",          WriterLevelSettingsListView.as_view(),   name="level-settings-list"),
    path("level-settings/<int:pk>/", WriterLevelSettingsDetailView.as_view(), name="level-settings-detail"),

    path("badges/", AdminBadgeListView.as_view(), name="badge-list"),
    path("writers/<str:registration_id>/badges/", AdminWriterBadgeListView.as_view(), name="writer-badge-list"),
    path("writers/<str:registration_id>/badges/award/", AdminWriterBadgeAwardView.as_view(), name="writer-badge-award"),
    path("writer-badges/<int:pk>/revoke/", AdminWriterBadgeRevokeView.as_view(), name="writer-badge-revoke"),

    # Applications (router)
    path("", include(router.urls)),
]
