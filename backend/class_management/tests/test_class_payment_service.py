from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import pytest

from class_management.constants import (
    ClassOrderStatus,
    ClassPaymentSourceType,
)
from class_management.exceptions import ClassPaymentError
from class_management.models import ClassPaymentAllocation
from class_management.services.class_payment_service import ClassPaymentService


@pytest.mark.django_db
def test_prepare_payment_rejects_amount_above_balance(class_order, client_user):
    class_order.final_amount = Decimal("300.00")
    class_order.balance_amount = Decimal("100.00")
    class_order.status = ClassOrderStatus.ACCEPTED
    class_order.save()

    with pytest.raises(ClassPaymentError):
        ClassPaymentService.prepare_payment(
            class_order=class_order,
            amount=Decimal("200.00"),
            payer=client_user,
            use_wallet=False,
        )


@pytest.mark.django_db
def test_apply_successful_payment_creates_allocation(class_order, client_user):
    class_order.final_amount = Decimal("300.00")
    class_order.balance_amount = Decimal("300.00")
    class_order.save()

    allocation = ClassPaymentService.apply_successful_payment(
        class_order=class_order,
        amount=Decimal("100.00"),
        source_type=ClassPaymentSourceType.EXTERNAL,
        payer=client_user,
        external_amount=Decimal("100.00"),
        payment_intent_id="pi_test_123",
        payment_transaction_id="txn_test_123",
    )

    class_order.refresh_from_db()

    assert allocation.amount == Decimal("100.00")
    assert class_order.paid_amount == Decimal("100.00")
    assert class_order.balance_amount == Decimal("200.00")


@pytest.mark.django_db
def test_payment_intent_id_is_idempotent(class_order, client_user):
    class_order.final_amount = Decimal("300.00")
    class_order.balance_amount = Decimal("300.00")
    class_order.save()

    ClassPaymentService.apply_successful_payment(
        class_order=class_order,
        amount=Decimal("100.00"),
        source_type=ClassPaymentSourceType.EXTERNAL,
        payer=client_user,
        external_amount=Decimal("100.00"),
        payment_intent_id="pi_unique_123",
        payment_transaction_id="txn_unique_123",
    )

    with pytest.raises(Exception):
        ClassPaymentService.apply_successful_payment(
            class_order=class_order,
            amount=Decimal("100.00"),
            source_type=ClassPaymentSourceType.EXTERNAL,
            payer=client_user,
            external_amount=Decimal("100.00"),
            payment_intent_id="pi_unique_123",
            payment_transaction_id="txn_other_123",
        )


@pytest.mark.django_db
def test_prepare_wallet_payment_applies_immediately(
    class_order,
    client_user,
    monkeypatch,
):
    class_order.final_amount = Decimal("300.00")
    class_order.balance_amount = Decimal("300.00")
    class_order.save()

    monkeypatch.setattr(
        ClassPaymentService,
        "_get_client_wallet_balance",
        staticmethod(lambda **kwargs: Decimal("300.00")),
    )
    monkeypatch.setattr(
        ClassPaymentService,
        "_debit_client_wallet",
        staticmethod(lambda **kwargs: "wallet_txn_1"),
    )

    result = ClassPaymentService.prepare_payment(
        class_order=class_order,
        amount=Decimal("300.00"),
        payer=client_user,
        use_wallet=True,
    )

    class_order.refresh_from_db()

    assert result.source_type == ClassPaymentSourceType.WALLET
    assert result.wallet_amount == Decimal("300.00")
    assert result.external_amount == Decimal("0.00")
    assert class_order.balance_amount == Decimal("0.00")


@pytest.mark.django_db
def test_prepare_split_payment_creates_checkout(
    class_order,
    client_user,
    monkeypatch,
):
    class_order.final_amount = Decimal("300.00")
    class_order.balance_amount = Decimal("300.00")
    class_order.save()

    monkeypatch.setattr(
        ClassPaymentService,
        "_get_client_wallet_balance",
        staticmethod(lambda **kwargs: Decimal("100.00")),
    )
    monkeypatch.setattr(
        ClassPaymentService,
        "_debit_client_wallet",
        staticmethod(lambda **kwargs: "wallet_txn_1"),
    )
    monkeypatch.setattr(
        ClassPaymentService,
        "_create_external_checkout",
        staticmethod(
            lambda **kwargs: SimpleNamespace(
                checkout_url="https://checkout.test",
                payment_intent_id="pi_split_123",
            )
        ),
    )

    result = ClassPaymentService.prepare_payment(
        class_order=class_order,
        amount=Decimal("300.00"),
        payer=client_user,
        use_wallet=True,
    )

    assert result.source_type == ClassPaymentSourceType.SPLIT
    assert result.wallet_amount == Decimal("100.00")
    assert result.external_amount == Decimal("200.00")
    assert result.checkout_url == "https://checkout.test"