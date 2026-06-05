from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any

import django


def bootstrap_django() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "writing_system.settings")
    django.setup()


def require_status(response, expected: int, label: str) -> None:
    if response.status_code != expected:
        body = getattr(response, "data", None)
        if body is None:
            body = response.content.decode("utf-8", errors="replace")
        raise AssertionError(
            f"{label}: expected HTTP {expected}, got {response.status_code}: {body}"
        )


def get_or_create_user(*, email: str, role: str, website, is_staff: bool = False):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user, _created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": email,
            "role": role,
            "website": website,
            "is_active": True,
            "is_staff": is_staff,
        },
    )
    User.objects.filter(pk=user.pk).update(
        username=email,
        role=role,
        website=website,
        is_active=True,
        is_staff=is_staff,
        is_superuser=role == "superadmin",
    )
    user.refresh_from_db()
    return user


def setup_seed_data():
    from websites.models.websites import Website

    website = (
        Website.objects.filter(domain="http://localhost").first()
        or Website.objects.filter(name="Smoke Test Website").first()
    )
    if website is None:
        website = Website.objects.create(
            domain="http://localhost",
            name="Smoke Test Website",
            is_active=True,
            is_deleted=False,
            allow_registration=True,
        )
    Website.objects.filter(pk=website.pk).update(
        domain="http://localhost",
        is_active=True,
        is_deleted=False,
        allow_registration=True,
    )
    website.refresh_from_db()

    client = get_or_create_user(
        email="smoke.wallet.client@example.com",
        role="client",
        website=website,
    )
    writer = get_or_create_user(
        email="smoke.wallet.writer@example.com",
        role="writer",
        website=website,
    )
    superadmin = get_or_create_user(
        email="smoke.wallet.superadmin@example.com",
        role="superadmin",
        website=website,
        is_staff=True,
    )
    return website, client, writer, superadmin


def authenticated_client(user):
    from rest_framework.test import APIClient

    api = APIClient()
    api.defaults["HTTP_HOST"] = "localhost"
    api.force_authenticate(user=user)
    return api


def ensure_wallet(api, *, website_id: int, user_id: int, wallet_type: str) -> dict[str, Any]:
    response = api.post(
        "/api/v1/wallets/admin/wallets/ensure/",
        {
            "website_id": website_id,
            "user_id": user_id,
            "wallet_type": wallet_type,
            "currency": "USD",
        },
        format="json",
    )
    require_status(response, 200, f"ensure {wallet_type} wallet")
    data = response.data
    if data["owner_user_id"] != user_id:
        raise AssertionError(f"ensure {wallet_type} wallet: wrong owner")
    if data["wallet_type"] != wallet_type:
        raise AssertionError(f"ensure {wallet_type} wallet: wrong wallet type")
    return data


def post_adjustment(
    api,
    *,
    website_id: int,
    wallet_id: int,
    action: str,
    amount: str,
) -> dict[str, Any]:
    response = api.post(
        f"/api/v1/wallets/admin/wallets/{wallet_id}/{action}/",
        {
            "website_id": website_id,
            "amount": amount,
            "description": f"Smoke admin wallet {action}",
            "reference": f"SMOKE-{action.upper()}-{wallet_id}-{time.time_ns()}",
            "reference_type": "smoke_test",
        },
        format="json",
    )
    require_status(response, 201, f"wallet {action}")
    data = response.data
    if not data.get("ledger_transaction_id"):
        raise AssertionError(f"wallet {action}: missing ledger transaction")
    return data


def main() -> None:
    bootstrap_django()
    website, client, writer, superadmin = setup_seed_data()
    api = authenticated_client(superadmin)

    client_wallet = ensure_wallet(
        api,
        website_id=website.id,
        user_id=client.id,
        wallet_type="client",
    )
    writer_wallet = ensure_wallet(
        api,
        website_id=website.id,
        user_id=writer.id,
        wallet_type="writer",
    )

    post_adjustment(
        api,
        website_id=website.id,
        wallet_id=client_wallet["id"],
        action="fund",
        amount="10.00",
    )
    post_adjustment(
        api,
        website_id=website.id,
        wallet_id=writer_wallet["id"],
        action="fund",
        amount="10.00",
    )
    post_adjustment(
        api,
        website_id=website.id,
        wallet_id=writer_wallet["id"],
        action="debit",
        amount="1.00",
    )

    print("OK: admin wallet ensure/fund/debit smoke passed.")


if __name__ == "__main__":
    main()
