import pytest

from activity.services.activity_service import ActivityService

pytestmark = pytest.mark.django_db


def test_record_event_creates_event(website, user):
    from django.db import models

    class Dummy(models.Model):
        name = models.CharField(max_length=10)

        class Meta:
            app_label = "activity"

    target = Dummy.objects.create(name="x")

    event = ActivityService.record_event(
        website=website,
        verb="test.created",
        target=target,
        actor=user,
        title="Hello",
    )

    assert event.id is not None
    assert event.verb == "test.created"
    assert event.title == "Hello"
    assert event.actor_object_id == str(user.pk)


def test_invalid_verb_raises(website, user):
    from django.db import models

    class Dummy(models.Model):
        name = models.CharField(max_length=10)

        class Meta:
            app_label = "activity"

    target = Dummy.objects.create(name="x")

    with pytest.raises(Exception):
        ActivityService.record_event(
            website=website,
            verb="invalid.verb",
            target=target,
        )