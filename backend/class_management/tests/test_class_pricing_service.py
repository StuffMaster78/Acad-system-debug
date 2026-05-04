from __future__ import annotations

from decimal import Decimal

import pytest

from class_management.constants import (
    ClassOrderStatus,
    ClassProposalStatus,
)
from class_management.exceptions import ClassPricingError
from class_management.services.class_pricing_service import (
    ClassPricingService,
)


@pytest.mark.django_db
def test_create_price_proposal(class_order, admin_user):
    class_order.status = ClassOrderStatus.UNDER_REVIEW
    class_order.save(update_fields=["status"])

    proposal = ClassPricingService.create_proposal(
        class_order=class_order,
        amount=Decimal("300.00"),
        discount_amount=Decimal("30.00"),
        proposed_by=admin_user,
    )

    assert proposal.amount == Decimal("300.00")
    assert proposal.discount_amount == Decimal("30.00")
    assert proposal.final_amount == Decimal("270.00")
    assert proposal.status == ClassProposalStatus.DRAFT


@pytest.mark.django_db
def test_create_proposal_rejects_invalid_discount(class_order, admin_user):
    class_order.status = ClassOrderStatus.UNDER_REVIEW
    class_order.save(update_fields=["status"])

    with pytest.raises(ClassPricingError):
        ClassPricingService.create_proposal(
            class_order=class_order,
            amount=Decimal("300.00"),
            discount_amount=Decimal("300.00"),
            proposed_by=admin_user,
        )


@pytest.mark.django_db
def test_send_proposal_updates_class_order(class_order, admin_user):
    class_order.status = ClassOrderStatus.UNDER_REVIEW
    class_order.save(update_fields=["status"])

    proposal = ClassPricingService.create_proposal(
        class_order=class_order,
        amount=Decimal("300.00"),
        discount_amount=Decimal("20.00"),
        proposed_by=admin_user,
    )

    ClassPricingService.send_proposal(
        proposal=proposal,
        sent_by=admin_user,
    )

    class_order.refresh_from_db()
    proposal.refresh_from_db()

    assert proposal.status == ClassProposalStatus.SENT
    assert class_order.status == ClassOrderStatus.PRICE_PROPOSED
    assert class_order.quoted_amount == Decimal("300.00")
    assert class_order.discount_amount == Decimal("20.00")
    assert class_order.final_amount == Decimal("280.00")


@pytest.mark.django_db
def test_accept_proposal_once(class_order, admin_user, client_user):
    class_order.status = ClassOrderStatus.UNDER_REVIEW
    class_order.save(update_fields=["status"])

    proposal = ClassPricingService.create_proposal(
        class_order=class_order,
        amount=Decimal("300.00"),
        proposed_by=admin_user,
        send_now=True,
    )

    accepted = ClassPricingService.accept_proposal(
        proposal=proposal,
        accepted_by=client_user,
    )

    class_order.refresh_from_db()

    assert accepted.status == ClassProposalStatus.ACCEPTED
    assert class_order.status == ClassOrderStatus.ACCEPTED
    assert class_order.accepted_amount == Decimal("300.00")


@pytest.mark.django_db
def test_accepting_accepted_proposal_fails(
    class_order,
    admin_user,
    client_user,
):
    class_order.status = ClassOrderStatus.UNDER_REVIEW
    class_order.save(update_fields=["status"])

    proposal = ClassPricingService.create_proposal(
        class_order=class_order,
        amount=Decimal("300.00"),
        proposed_by=admin_user,
        send_now=True,
    )

    ClassPricingService.accept_proposal(
        proposal=proposal,
        accepted_by=client_user,
    )

    with pytest.raises(ClassPricingError):
        ClassPricingService.accept_proposal(
            proposal=proposal,
            accepted_by=client_user,
        )