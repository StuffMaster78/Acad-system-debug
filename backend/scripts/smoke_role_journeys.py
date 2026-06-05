from __future__ import annotations

import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

import django


def bootstrap_django() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "writing_system.settings")
    django.setup()


def as_list(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("results"), list):
        return payload["results"]
    raise AssertionError(f"Expected list or paginated payload, got {type(payload).__name__}")


def require_status(response, expected: int, label: str) -> None:
    if response.status_code != expected:
        body = getattr(response, "data", None)
        if body is None:
            body = response.content.decode("utf-8", errors="replace")
        body_text = str(body)
        if len(body_text) > 1200:
            body_text = f"{body_text[:1200]}..."
        raise AssertionError(f"{label}: expected HTTP {expected}, got {response.status_code}: {body_text}")


def require_fields_absent(payload: dict[str, Any], fields: set[str], label: str) -> None:
    leaked = sorted(field for field in fields if field in payload)
    if leaked:
        raise AssertionError(f"{label}: leaked fields {leaked}")


def require_action_contract(payload: dict[str, Any], label: str) -> None:
    if not isinstance(payload.get("available_actions"), list):
        raise AssertionError(f"{label}: available_actions missing or not a list")
    if not isinstance(payload.get("blocked_actions"), list):
        raise AssertionError(f"{label}: blocked_actions missing or not a list")


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
        email="smoke.client@example.com",
        role="client",
        website=website,
    )
    writer = get_or_create_user(
        email="smoke.writer@example.com",
        role="writer",
        website=website,
    )
    admin = get_or_create_user(
        email="smoke.admin@example.com",
        role="admin",
        website=website,
        is_staff=True,
    )
    return website, client, writer, admin


def authenticated_client(user):
    from rest_framework.test import APIClient

    api = APIClient()
    api.defaults["HTTP_HOST"] = "localhost"
    api.force_authenticate(user=user)
    return api


def create_class_order(api):
    response = api.post(
        "/api/v1/class-management/classes/",
        {
            "title": "Smoke class journey",
            "institution_name": "Smoke University",
            "class_name": "Product Strategy",
            "class_code": "PSY-501",
            "class_subject": "Business",
            "academic_level": "Masters",
            "initial_client_notes": "Smoke test class order.",
        },
        format="json",
    )
    require_status(response, 201, "client creates class order")
    require_action_contract(response.data, "client class create response")
    return response.data["id"]


def create_special_order(api):
    response = api.post(
        "/api/v1/special-orders/quoted/",
        {
            "title": "Smoke special journey",
            "inquiry_details": "Build a diagram plus written explanation.",
            "budget": "250.00",
            "duration_days": 5,
            "currency": "USD",
        },
        format="json",
    )
    require_status(response, 201, "client creates quoted special order")
    require_action_contract(response.data, "client special create response")
    require_fields_absent(
        response.data,
        {"admin_notes", "client_email", "writer_pay_rule"},
        "client special create response",
    )
    return response.data["id"]


def exercise_class_journey(*, class_id: int, client, writer, admin) -> None:
    from class_management.constants import ClassOrderStatus
    from class_management.models import ClassOrder

    client_api = authenticated_client(client)
    admin_api = authenticated_client(admin)
    writer_api = authenticated_client(writer)

    response = client_api.get(f"/api/v1/class-management/classes/{class_id}/")
    require_status(response, 200, "client reads class detail")
    require_action_contract(response.data, "client class detail")

    response = client_api.post(f"/api/v1/class-management/classes/{class_id}/submit/", {}, format="json")
    require_status(response, 200, "client submits class order")

    response = admin_api.get("/api/v1/class-management/classes/")
    require_status(response, 200, "admin lists class orders")
    items = as_list(response.data)
    if items:
        require_action_contract(items[0], "admin class list item")

    response = admin_api.get(f"/api/v1/class-management/classes/{class_id}/")
    require_status(response, 200, "admin reads class detail")
    require_action_contract(response.data, "admin class detail")

    response = admin_api.get(f"/api/v1/class-management/classes/{class_id}/available-actions/")
    require_status(response, 200, "admin reads class available actions")
    require_action_contract(response.data, "admin class available actions")

    ClassOrder.objects.filter(pk=class_id).update(
        assigned_writer=writer,
        status=ClassOrderStatus.ASSIGNED,
        writer_visible_notes="Writer-safe smoke instructions.",
    )

    response = writer_api.get(f"/api/v1/class-management/classes/{class_id}/")
    require_status(response, 200, "writer reads assigned class detail")
    require_action_contract(response.data, "writer class detail")
    require_fields_absent(
        response.data,
        {
            "payment_status",
            "quoted_amount",
            "accepted_amount",
            "discount_code",
            "discount_amount",
            "final_amount",
            "paid_amount",
            "balance_amount",
            "admin_internal_notes",
        },
        "writer class detail",
    )


def exercise_special_journey(*, special_id: int, client, writer, admin, website) -> None:
    from special_orders.constants import SpecialOrderStatus
    from special_orders.models import SpecialOrder, SpecialOrderWriterPayRule

    client_api = authenticated_client(client)
    admin_api = authenticated_client(admin)
    writer_api = authenticated_client(writer)

    response = client_api.get(f"/api/v1/special-orders/{special_id}/")
    require_status(response, 200, "client reads special detail")
    require_action_contract(response.data, "client special detail")
    require_fields_absent(
        response.data,
        {"admin_notes", "client_email", "writer_pay_rule"},
        "client special detail",
    )

    response = admin_api.get("/api/v1/special-orders/")
    require_status(response, 200, "admin lists special orders")
    items = as_list(response.data)
    if items:
        require_action_contract(items[0], "admin special list item")

    response = admin_api.get(f"/api/v1/special-orders/{special_id}/")
    require_status(response, 200, "admin reads special detail")
    require_action_contract(response.data, "admin special detail")

    response = admin_api.get(f"/api/v1/special-orders/{special_id}/available-actions/")
    require_status(response, 200, "admin reads special available actions")
    require_action_contract(response.data, "admin special available actions")

    pay_rule, _created = SpecialOrderWriterPayRule.objects.update_or_create(
        website=website,
        name="Smoke fixed writer pay",
        defaults={
            "is_active": True,
            "fixed_amount": Decimal("75.00"),
            "percentage": None,
        },
    )
    SpecialOrder.objects.filter(pk=special_id).update(
        writer=writer,
        writer_pay_rule=pay_rule,
        status=SpecialOrderStatus.ASSIGNED,
    )

    response = writer_api.get(f"/api/v1/special-orders/{special_id}/")
    require_status(response, 200, "writer reads assigned special detail")
    require_action_contract(response.data, "writer special detail")
    require_fields_absent(
        response.data,
        {
            "admin_notes",
            "budget",
            "client",
            "client_email",
            "accepted_quote",
            "converted_order",
            "quoted_price",
            "quotes",
            "writer_pay_rule",
            "payment_status",
            "deadline",
            "final_price",
        },
        "writer special detail",
    )
    compensation = response.data.get("writer_compensation")
    if compensation != {"type": "fixed_amount", "amount": "75.00", "currency": "USD"}:
        raise AssertionError(f"writer special detail: unexpected compensation {compensation}")


def main() -> None:
    bootstrap_django()
    website, client, writer, admin = setup_seed_data()

    class_id = create_class_order(authenticated_client(client))
    special_id = create_special_order(authenticated_client(client))

    exercise_class_journey(
        class_id=class_id,
        client=client,
        writer=writer,
        admin=admin,
    )
    exercise_special_journey(
        special_id=special_id,
        client=client,
        writer=writer,
        admin=admin,
        website=website,
    )

    print("OK: role journeys smoke passed for class and special order surfaces.")


if __name__ == "__main__":
    main()
