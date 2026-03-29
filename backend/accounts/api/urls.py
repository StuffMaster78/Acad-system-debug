from django.urls import path

from accounts.api.views.account_audit_views import (
    AccountAuditLogListView,
    OnboardingSessionListView,
)
from accounts.api.views.account_role_views import (
    AssignAccountRoleView,
    ListMyAccountRolesView,
    RevokeAccountRoleView,
)
from accounts.api.views.account_status_views import (
    ActivateAccountView,
    ReactivateAccountView,
    SuspendAccountView,
)
from accounts.api.views.account_views import (
    MyAccountProfileView,
    MyAccountSummaryView,
)
from accounts.api.views.onboarding_views import (
    CompleteClientOnboardingView,
    CompleteStaffOnboardingView,
    CompleteWriterOnboardingView,
)

app_name = "accounts"

urlpatterns = [
    path("me/summary/", MyAccountSummaryView.as_view(), name="my-account-summary"),
    path("me/profile/", MyAccountProfileView.as_view(), name="my-profile"),
    path("me/roles/", ListMyAccountRolesView.as_view(), name="my-roles"),

    path(
        "<int:account_profile_id>/roles/assign/",
        AssignAccountRoleView.as_view(),
        name="assign-role",
    ),
    path(
        "<int:account_profile_id>/roles/revoke/",
        RevokeAccountRoleView.as_view(),
        name="revoke-role",
    ),

    path(
        "<int:account_profile_id>/activate/",
        ActivateAccountView.as_view(),
        name="activate-account",
    ),
    path(
        "<int:account_profile_id>/suspend/",
        SuspendAccountView.as_view(),
        name="suspend-account",
    ),
    path(
        "<int:account_profile_id>/reactivate/",
        ReactivateAccountView.as_view(),
        name="reactivate-account",
    ),

    path(
        "<int:account_profile_id>/onboarding/client/complete/",
        CompleteClientOnboardingView.as_view(),
        name="complete-client-onboarding",
    ),
    path(
        "<int:account_profile_id>/onboarding/writer/complete/",
        CompleteWriterOnboardingView.as_view(),
        name="complete-writer-onboarding",
    ),
    path(
        "<int:account_profile_id>/onboarding/staff/complete/",
        CompleteStaffOnboardingView.as_view(),
        name="complete-staff-onboarding",
    ),

    path(
        "<int:account_profile_id>/audit-logs/",
        AccountAuditLogListView.as_view(),
        name="account-audit-logs",
    ),
    path(
        "<int:account_profile_id>/onboarding-sessions/",
        OnboardingSessionListView.as_view(),
        name="onboarding-sessions",
    ),
]