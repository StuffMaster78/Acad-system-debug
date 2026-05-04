from __future__ import annotations

from decimal import Decimal

import pytest

from class_management.constants import (
    ClassOrderStatus,
    ClassWriterCompensationStatus,
    ClassWriterCompensationType,
)
from class_management.exceptions import ClassWriterCompensationError
from class_management.services.class_writer_compensation_service import (
    ClassWriterCompensationService,
)


@pytest.mark.django_db
def test_set_percentage_compensation(class_order, writer_user, admin_user):
    class_order.assigned_writer = writer_user
    class_order.final_amount = Decimal("400.00")
    class_order.save()

    compensation = ClassWriterCompensationService.set_compensation(
        class_order=class_order,
        writer=writer_user,
        compensation_type=ClassWriterCompensationType.PERCENTAGE,
        percentage=Decimal("50.00"),
        set_by=admin_user,
    )

    assert compensation.final_amount == Decimal("200.00")


@pytest.mark.django_db
def test_fixed_compensation_cannot_exceed_class_amount(
    class_order,
    writer_user,
    admin_user,
):
    class_order.assigned_writer = writer_user
    class_order.final_amount = Decimal("400.00")
    class_order.save()

    with pytest.raises(ClassWriterCompensationError):
        ClassWriterCompensationService.set_compensation(
            class_order=class_order,
            writer=writer_user,
            compensation_type=ClassWriterCompensationType.FIXED_AMOUNT,
            fixed_amount=Decimal("500.00"),
            set_by=admin_user,
        )


@pytest.mark.django_db
def test_compensation_mark_earned_requires_completion(
    class_order,
    writer_user,
    admin_user,
):
    class_order.assigned_writer = writer_user
    class_order.final_amount = Decimal("400.00")
    class_order.status = ClassOrderStatus.IN_PROGRESS
    class_order.save()

    compensation = ClassWriterCompensationService.set_compensation(
        class_order=class_order,
        writer=writer_user,
        compensation_type=ClassWriterCompensationType.FIXED_AMOUNT,
        fixed_amount=Decimal("200.00"),
        set_by=admin_user,
    )

    ClassWriterCompensationService.approve_compensation(
        compensation=compensation,
        approved_by=admin_user,
    )

    with pytest.raises(ClassWriterCompensationError):
        ClassWriterCompensationService.mark_earned(
            class_order=class_order,
            triggered_by=admin_user,
        )


@pytest.mark.django_db
def test_post_to_writer_wallet_once(
    class_order,
    writer_user,
    admin_user,
    monkeypatch,
):
    class_order.assigned_writer = writer_user
    class_order.final_amount = Decimal("400.00")
    class_order.status = ClassOrderStatus.COMPLETED
    class_order.save()

    compensation = ClassWriterCompensationService.set_compensation(
        class_order=class_order,
        writer=writer_user,
        compensation_type=ClassWriterCompensationType.FIXED_AMOUNT,
        fixed_amount=Decimal("200.00"),
        set_by=admin_user,
    )

    ClassWriterCompensationService.approve_compensation(
        compensation=compensation,
        approved_by=admin_user,
    )
    ClassWriterCompensationService.mark_earned(
        class_order=class_order,
        triggered_by=admin_user,
    )

    monkeypatch.setattr(
        ClassWriterCompensationService,
        "_credit_writer_wallet",
        staticmethod(lambda **kwargs: "writer_wallet_txn_1"),
    )

    updated = ClassWriterCompensationService.post_to_writer_wallet(
        compensation=compensation,
        posted_by=admin_user,
    )

    assert updated.status == ClassWriterCompensationStatus.POSTED_TO_WALLET
    assert updated.paid_amount == Decimal("200.00")

    with pytest.raises(ClassWriterCompensationError):
        ClassWriterCompensationService.post_to_writer_wallet(
            compensation=updated,
            posted_by=admin_user,
        )