from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from activity.models import ActivityEvent
from activity.services.activity_service import ActivityService

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="pass1234",
    )


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="staff",
        email="staff@example.com",
        password="pass1234",
        is_staff=True,
    )


@pytest.fixture
def website(db):
    from websites.models.websites import Website

    return Website.objects.create(name="Test Site")


@pytest.fixture
def activity_event(db, website, user):
    from django.db import models

    class Dummy(models.Model):
        name = models.CharField(max_length=10)

        class Meta:
            app_label = "activity"

    target = Dummy.objects.create(name="x")

    return ActivityService.record_event(
        website=website,
        verb="test.created",
        target=target,
        actor=user,
        title="Test Event",
    )