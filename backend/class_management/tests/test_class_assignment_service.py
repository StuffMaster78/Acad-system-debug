from __future__ import annotations

import pytest

from class_management.constants import ClassOrderStatus, ClassPaymentStatus
from class_management.exceptions import ClassAssignmentError
from class_management.services.class_assignment_service import (
    ClassAssignmentService,
)


@pytest.mark.django_db
def test_assign_writer(class_order, writer_user, admin_user):
    class_order.status = ClassOrderStatus.PAID
    class_order.payment_status = ClassPaymentStatus.PAID
    class_order.save(update_fields=["status", "payment_status"])

    assignment = ClassAssignmentService.assign_writer(
        class_order=class_order,
        writer=writer_user,
        assigned_by=admin_user,
    )

    class_order.refresh_from_db()

    assert assignment.writer == writer_user
    assert class_order.assigned_writer == writer_user
    assert class_order.status == ClassOrderStatus.ASSIGNED


@pytest.mark.django_db
def test_cannot_assign_two_active_writers(
    class_order,
    writer_user,
    another_writer_user,
    admin_user,
):
    class_order.status = ClassOrderStatus.PAID
    class_order.payment_status = ClassPaymentStatus.PAID
    class_order.save(update_fields=["status", "payment_status"])

    ClassAssignmentService.assign_writer(
        class_order=class_order,
        writer=writer_user,
        assigned_by=admin_user,
    )

    with pytest.raises(ClassAssignmentError):
        ClassAssignmentService.assign_writer(
            class_order=class_order,
            writer=another_writer_user,
            assigned_by=admin_user,
        )


@pytest.mark.django_db
def test_reassign_writer(
    class_order,
    writer_user,
    another_writer_user,
    admin_user,
):
    class_order.status = ClassOrderStatus.PAID
    class_order.payment_status = ClassPaymentStatus.PAID
    class_order.save(update_fields=["status", "payment_status"])

    ClassAssignmentService.assign_writer(
        class_order=class_order,
        writer=writer_user,
        assigned_by=admin_user,
    )

    new_assignment = ClassAssignmentService.reassign_writer(
        class_order=class_order,
        new_writer=another_writer_user,
        reassigned_by=admin_user,
        reason="Writer unavailable.",
    )

    class_order.refresh_from_db()

    assert new_assignment.writer == another_writer_user
    assert class_order.assigned_writer == another_writer_user


@pytest.mark.django_db
def test_cannot_assign_pending_payment_class(class_order, writer_user, admin_user):
    class_order.status = ClassOrderStatus.PENDING_PAYMENT
    class_order.payment_status = ClassPaymentStatus.UNPAID
    class_order.save(update_fields=["status", "payment_status"])

    with pytest.raises(ClassAssignmentError):
        ClassAssignmentService.assign_writer(
            class_order=class_order,
            writer=writer_user,
            assigned_by=admin_user,
        )
