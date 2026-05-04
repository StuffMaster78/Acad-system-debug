from __future__ import annotations

from decimal import Decimal

import pytest

from class_management.constants import ClassTaskStatus
from class_management.exceptions import ClassManagementError
from class_management.services.class_scope_service import ClassScopeService


@pytest.mark.django_db
def test_create_scope_assessment(class_order, admin_user):
    assessment = ClassScopeService.create_or_update_assessment(
        class_order=class_order,
        assessed_by=admin_user,
        discussion_posts_count=3,
        quizzes_count=2,
        estimated_hours=Decimal("10.00"),
    )

    assert assessment.discussion_posts_count == 3
    assert assessment.quizzes_count == 2
    assert assessment.estimated_hours == Decimal("10.00")


@pytest.mark.django_db
def test_scope_assessment_rejects_negative_counts(class_order, admin_user):
    with pytest.raises(ClassManagementError):
        ClassScopeService.create_or_update_assessment(
            class_order=class_order,
            assessed_by=admin_user,
            discussion_posts_count=-1,
        )


@pytest.mark.django_db
def test_add_scope_item(class_order, admin_user):
    item = ClassScopeService.add_scope_item(
        class_order=class_order,
        item_type="quiz",
        title="Quiz 1",
        quantity=1,
        created_by=admin_user,
    )

    assert item.title == "Quiz 1"
    assert item.item_type == "quiz"


@pytest.mark.django_db
def test_create_task_from_scope_item(class_order, admin_user):
    item = ClassScopeService.add_scope_item(
        class_order=class_order,
        item_type="quiz",
        title="Quiz 1",
        created_by=admin_user,
    )

    task = ClassScopeService.create_task_from_scope_item(
        scope_item=item,
        created_by=admin_user,
    )

    assert task.scope_item == item
    assert task.title == "Quiz 1"
    assert task.status == ClassTaskStatus.PENDING


@pytest.mark.django_db
def test_task_lifecycle(class_order, admin_user, writer_user):
    task = ClassScopeService.create_manual_task(
        class_order=class_order,
        title="Discussion Post",
        created_by=admin_user,
        assigned_writer=writer_user,
    )

    started = ClassScopeService.start_task(
        task=task,
        started_by=writer_user,
    )
    assert started.status == ClassTaskStatus.IN_PROGRESS

    submitted = ClassScopeService.submit_task(
        task=started,
        submitted_by=writer_user,
        notes="Submitted in portal.",
        portal_submitted=True,
    )
    assert submitted.status == ClassTaskStatus.SUBMITTED

    completed = ClassScopeService.complete_task(
        task=submitted,
        completed_by=admin_user,
    )
    assert completed.status == ClassTaskStatus.COMPLETED