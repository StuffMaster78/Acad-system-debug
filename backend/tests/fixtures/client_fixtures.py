from __future__ import annotations

import pytest
from django.test import Client
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def django_client():
    return Client()


def authenticate(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
    )
    return api_client


@pytest.fixture
def authenticated_client(api_client, client_user):
    return authenticate(api_client, client_user)


@pytest.fixture
def authenticated_writer_client(api_client, writer_user):
    return authenticate(api_client, writer_user)


@pytest.fixture
def authenticated_editor_client(api_client, editor_user):
    return authenticate(api_client, editor_user)


@pytest.fixture
def authenticated_support_client(api_client, support_user):
    return authenticate(api_client, support_user)


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    return authenticate(api_client, admin_user)


@pytest.fixture
def authenticated_superadmin_client(api_client, superadmin_user):
    return authenticate(api_client, superadmin_user)


@pytest.fixture
def authenticated_writer(api_client, writer_user):
    return authenticate(api_client, writer_user)


@pytest.fixture
def authenticated_admin(api_client, admin_user):
    return authenticate(api_client, admin_user)


@pytest.fixture
def authenticated_django_client(django_client, client_user):
    django_client.force_login(client_user)
    return django_client


@pytest.fixture
def client_token(client_user):
    refresh = RefreshToken.for_user(client_user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@pytest.fixture
def writer_token(writer_user):
    refresh = RefreshToken.for_user(writer_user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@pytest.fixture
def admin_token(admin_user):
    refresh = RefreshToken.for_user(admin_user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }