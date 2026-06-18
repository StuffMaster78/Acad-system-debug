import pytest
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from authentication.api.views.impersonation_views import (
    ImpersonationCreateTokenView,
    ImpersonationEndView,
    ImpersonationStartView,
)
from authentication.models.login_session import LoginSession
from authentication.services.login_session_service import LoginSessionService


pytestmark = pytest.mark.django_db


def _admin_for_website(admin_user, website):
    admin_user.website = website
    admin_user.role = "superadmin"
    admin_user.is_staff = True
    admin_user.save(update_fields=["website", "role", "is_staff"])
    return admin_user


def _request(factory, path, payload, user, session, token=None):
    request = factory.post(path, payload, format="json")
    request.website = None
    request.session = session
    force_authenticate(request, user=user, token=token)
    return request


def test_create_token_falls_back_to_authenticated_users_website(
    admin_user,
    client_user,
    website,
    mock_request_session,
):
    admin = _admin_for_website(admin_user, website)
    factory = APIRequestFactory()
    request = _request(
        factory,
        "/api/v1/auth/impersonation/token/",
        {
            "target_user_id": client_user.pk,
            "reason": "Support investigation",
        },
        admin,
        mock_request_session,
    )

    response = ImpersonationCreateTokenView.as_view()(request)

    assert response.status_code == 201
    assert response.data["token"]


def test_jwt_only_impersonation_can_end_and_restore_refreshable_admin_session(
    admin_user,
    client_user,
    website,
    mock_request_session,
):
    admin = _admin_for_website(admin_user, website)
    factory = APIRequestFactory()
    original_session, _ = LoginSessionService.start_session(
        user=admin,
        website=website,
    )
    admin_refresh = RefreshToken.for_user(admin)
    admin_refresh["session_id"] = original_session.pk
    admin_refresh["website_id"] = website.pk

    create_request = _request(
        factory,
        "/api/v1/auth/impersonation/token/",
        {
            "target_user_id": client_user.pk,
            "reason": "Support investigation",
        },
        admin,
        mock_request_session,
        admin_refresh.access_token,
    )
    created = ImpersonationCreateTokenView.as_view()(create_request)

    start_request = _request(
        factory,
        "/api/v1/auth/impersonation/start/",
        {
            "token": created.data["token"],
            "reason": "Support investigation",
        },
        admin,
        mock_request_session,
        admin_refresh.access_token,
    )
    started = ImpersonationStartView.as_view()(start_request)
    impersonation_access = AccessToken(started.data["access_token"])

    assert impersonation_access["is_impersonation"] is True
    assert impersonation_access["impersonated_user_id"] == client_user.pk
    impersonation_session = LoginSession.objects.get(
        pk=impersonation_access["session_id"],
    )
    assert impersonation_session.session_type == (
        LoginSession.SessionType.IMPERSONATION
    )

    mock_request_session._session.clear()
    end_request = _request(
        factory,
        "/api/v1/auth/impersonation/end/",
        {
            "reason": "Support investigation complete",
            "close_tab": False,
        },
        client_user,
        mock_request_session,
        impersonation_access,
    )
    ended = ImpersonationEndView.as_view()(end_request)

    assert ended.status_code == 200
    assert ended.data["user"]["id"] == admin.pk
    restored_refresh = RefreshToken(ended.data["refresh_token"])
    assert restored_refresh["session_id"] == original_session.pk
    impersonation_session.refresh_from_db()
    assert impersonation_session.revoked_at is not None
