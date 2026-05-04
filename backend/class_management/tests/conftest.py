from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from class_management.models.class_order import (
    ClassOrder,
)

@pytest.fixture
def client_user(db):
    UserModel = get_user_model()
    return UserModel.objects.create_user(
        username="client",
        email="client@example.com",
        password="pass",
    )


@pytest.fixture
def writer_user(db):
    UserModel = get_user_model()
    return UserModel.objects.create_user(
        username="writer",
        email="writer@example.com",
        password="pass",
    )


@pytest.fixture
def another_writer_user(db):
    UserModel = get_user_model()
    return UserModel.objects.create_user(
        username="writer2",
        email="writer2@example.com",
        password="pass",
    )


@pytest.fixture
def admin_user(db):
    UserModel = get_user_model()
    return UserModel.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="pass",
        is_staff=True,
    )


@pytest.fixture
def website(db):
    from websites.models.websites import Website

    return Website.objects.create(
        name="Main Website",
        domain="example.com",
    )


@pytest.fixture
def class_order(db, website, client_user):
    return ClassOrder.objects.create(
        website=website,
        client=client_user,
        title="Nursing Class Support",
    )