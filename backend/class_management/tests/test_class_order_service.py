from __future__ import annotations

from decimal import Decimal

import pytest

from class_management.constants import (
    ClassOrderStatus,
    ClassPaymentStatus,
    ClassTaskStatus,
)
from class_management.exceptions import ClassOrderStateError
from class_management.models import ClassTask
from class_management.services.class_order_service import ClassOrderService


@pytest.mark.django_db
def test_create_draft_creates_class_order(website, client_user):
    class_order = ClassOrderService.create_draft(
        website=website,
        client=client_user,
        title="BIO 101 Support",
        created_by=client_user,
    )

    assert class_order.website == website
    assert class_order.client == client_user
    assert class_order.title == "BIO 101 Support"
    assert class_order.status == ClassOrderStatus.DRAFT


@pytest.mark.django_db
def test_submit_draft_class_order(website, client_user):
    class_order = ClassOrderService.create_draft(
        website=website,
        client=client_user,
        title="BIO 101 Support",
        created_by=client_user,
    )

    updated = ClassOrderService.submit(
        class_order=class_order,
        submitted_by=client_user,
    )

    assert updated.status == ClassOrderStatus.SUBMITTED
    assert updated.submitted_at is not None


@pytest.mark.django_db
def test_submit_non_draft_fails(class_order, client_user):
    class_order.status = ClassOrderStatus.SUBMITTED
    class_order.save(update_fields=["status"])

    with pytest.raises(ClassOrderStateError):
        ClassOrderService.submit(
            class_order=class_order,
            submitted_by=client_user,
        )


@pytest.mark.django_db
def test_apply_payment_marks_partially_paid(class_order, admin_user):
    class_order.final_amount = Decimal("300.00")
    class_order.balance_amount = Decimal("300.00")
    class_order.save()

    updated = ClassOrderService.apply_payment(
        class_order=class_order,
        amount=Decimal("100.00"),
        triggered_by=admin_user,
    )

    assert updated.paid_amount == Decimal("100.00")
    assert updated.balance_amount == Decimal("200.00")
    assert updated.payment_status == ClassPaymentStatus.PARTIALLY_PAID
    assert updated.status == ClassOrderStatus.PARTIALLY_PAID


@pytest.mark.django_db
def test_apply_payment_marks_paid(class_order, admin_user):
    class_order.final_amount = Decimal("300.00")
    class_order.balance_amount = Decimal("300.00")
    class_order.save()

    updated = ClassOrderService.apply_payment(
        class_order=class_order,
        amount=Decimal("300.00"),
        triggered_by=admin_user,
    )

    assert updated.paid_amount == Decimal("300.00")
    assert updated.balance_amount == Decimal("0.00")
    assert updated.payment_status == ClassPaymentStatus.PAID
    assert updated.status == ClassOrderStatus.PAID


@pytest.mark.django_db
def test_complete_requires_full_payment(class_order, admin_user):
    class_order.status = ClassOrderStatus.IN_PROGRESS
    class_order.payment_status = ClassPaymentStatus.PARTIALLY_PAID
    class_order.save()

    with pytest.raises(ClassOrderStateError):
        ClassOrderService.complete(
            class_order=class_order,
            completed_by=admin_user,
        )


@pytest.mark.django_db
def test_complete_fails_with_unfinished_tasks(class_order, admin_user):
    class_order.status = ClassOrderStatus.IN_PROGRESS
    class_order.payment_status = ClassPaymentStatus.PAID
    class_order.save()

    ClassTask.objects.create(
        class_order=class_order,
        title="Quiz 1",
        status=ClassTaskStatus.IN_PROGRESS,
    )

    with pytest.raises(ClassOrderStateError):
        ClassOrderService.complete(
            class_order=class_order,
            completed_by=admin_user,
        )


@pytest.mark.django_db
def test_complete_succeeds_when_paid_and_tasks_done(class_order, admin_user):
    class_order.status = ClassOrderStatus.IN_PROGRESS
    class_order.payment_status = ClassPaymentStatus.PAID
    class_order.save()

    ClassTask.objects.create(
        class_order=class_order,
        title="Quiz 1",
        status=ClassTaskStatus.COMPLETED,
    )

    updated = ClassOrderService.complete(
        class_order=class_order,
        completed_by=admin_user,
    )

    assert updated.status == ClassOrderStatus.COMPLETED
    assert updated.completed_at is not None