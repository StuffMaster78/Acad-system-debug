from __future__ import annotations

from decimal import Decimal

TIP_CURRENCY = "USD"

TIP_IDEMPOTENCY_KEY_LENGTH = 128

TIP_REASON_MAX_LENGTH = 500

TIP_POLICY_CACHE_KEY = "tips:active_policy"

ABSOLUTE_TIP_SAFETY_LIMIT = Decimal("1000000.00")