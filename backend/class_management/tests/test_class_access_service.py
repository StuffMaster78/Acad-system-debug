from __future__ import annotations

import pytest

from class_management.exceptions import ClassAccessDeniedError
from class_management.models import ClassAccessLog
from class_management.services.class_access_service import ClassAccessService


@pytest.mark.django_db
def test_writer_cannot_view_access_without_grant(class_order, writer_user):
    class_order.assigned_writer = writer_user
    class_order.save(update_fields=["assigned_writer"])

    ClassAccessService.create_or_update_access_detail(
        class_order=class_order,
        actor=class_order.client,
        class_portal_url="https://portal.test",
        login_username="student",
        login_password="secret",
    )

    with pytest.raises(ClassAccessDeniedError):
        ClassAccessService.view_access_detail(
            class_order=class_order,
            viewer=writer_user,
        )


@pytest.mark.django_db
def test_granted_writer_can_view_access_and_log_is_created(
    class_order,
    writer_user,
    admin_user,
):
    class_order.assigned_writer = writer_user
    class_order.save(update_fields=["assigned_writer"])

    ClassAccessService.create_or_update_access_detail(
        class_order=class_order,
        actor=admin_user,
        class_portal_url="https://portal.test",
        login_username="student",
        login_password="secret",
    )

    ClassAccessService.grant_access(
        class_order=class_order,
        user=writer_user,
        granted_by=admin_user,
        reason="Assigned writer needs portal access.",
    )

    data = ClassAccessService.view_access_detail(
        class_order=class_order,
        viewer=writer_user,
        reason="Working on quiz",
    )

    assert data["login_username"] == "student"
    assert data["login_password"] == "secret"

    assert ClassAccessLog.objects.filter(
        class_order=class_order,
        viewed_by=writer_user,
    ).exists()


@pytest.mark.django_db
def test_two_factor_request_lifecycle(class_order, writer_user):
    request = ClassAccessService.request_two_factor(
        class_order=class_order,
        requested_by=writer_user,
        request_notes="Need login code.",
    )

    assert request.status == "pending"

    sent = ClassAccessService.mark_two_factor_sent(
        request=request,
        actor=class_order.client,
        notes="Code sent.",
    )

    assert sent.status == "sent"

    resolved = ClassAccessService.resolve_two_factor_request(
        request=sent,
        resolved_by=writer_user,
        notes="Logged in successfully.",
    )

    assert resolved.status == "resolved"
    assert resolved.resolved_at is not None