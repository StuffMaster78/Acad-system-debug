from __future__ import annotations

import os
import sys
from pathlib import Path

import django
from django.urls import resolve


EXPECTED_ROUTES = {
    "/api/v1/orders/orders/create/": "order-create-order",
    "/api/v1/orders/orders/1/lifecycle/": "order-lifecycle",
    "/api/v1/cms/intelligence/search-log/": "search-log-list",
    "/api/v1/cms/intelligence/personalization/": "personalization-list",
    "/api/v1/class-management/configs/seed-defaults/": "class-config-seed-defaults",
    "/api/v1/class-management/classes/1/available-actions/": "class-order-available-actions",
    (
        "/api/v1/special-orders/predefined-configs/seed-defaults/"
    ): "special-order-predefined-config-seed-defaults",
    "/api/v1/special-orders/1/available-actions/": "special-order-available-actions",
    "/api/v1/special-orders/1/milestones/": "special-order-milestones",
    "/api/v1/wallets/admin/wallets/ensure/": "admin-wallet-ensure",
}


def main() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "writing_system.settings")
    django.setup()
    failures = []
    for path, expected_name in EXPECTED_ROUTES.items():
        actual_name = resolve(path).url_name
        if actual_name != expected_name:
            failures.append(f"{path}: expected {expected_name}, got {actual_name}")

    if failures:
        raise SystemExit("\n".join(failures))

    print(f"OK: {len(EXPECTED_ROUTES)} config/CMS routes resolved.")


if __name__ == "__main__":
    main()
