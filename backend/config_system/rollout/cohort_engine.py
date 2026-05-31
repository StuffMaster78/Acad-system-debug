from __future__ import annotations

import hashlib
from typing import Any

from .context import RolloutContext
from .rules import RolloutRule
from .operators import RuleOperators


class CohortEngine:
    """
    Deterministic cohort + rule-based filtering engine.
    """

    # -------------------------
    # PUBLIC ENTRY
    # -------------------------

    @classmethod
    def is_enabled(
        cls,
        *,
        key: str,
        percentage: float = 100,
        context: RolloutContext,
        rules: list[RolloutRule] | None = None,
    ) -> bool:

        if rules and not cls._matches_rules(context, rules):
            return False

        if percentage >= 100:
            return True

        if percentage <= 0:
            return False

        bucket = cls._hash_to_bucket(
            cls._build_bucket_input(key, context)
        )

        return bucket < percentage

    # -------------------------
    # RULE ENGINE
    # -------------------------

    @classmethod
    def _matches_rules(
        cls,
        context: RolloutContext,
        rules: list[RolloutRule],
    ) -> bool:

        for rule in rules:

            actual = cls._resolve_attribute(context, rule.attribute)

            if not RuleOperators.evaluate(
                actual,
                rule.operator,
                rule.value,
            ):
                return False

        return True

    @staticmethod
    def _resolve_attribute(
        context: RolloutContext,
        attribute: str,
    ) -> Any:

        if hasattr(context, attribute):
            return getattr(context, attribute)

        return context.attributes.get(attribute)

    # -------------------------
    # COHORT HASHING
    # -------------------------

    @staticmethod
    def _build_bucket_input(
        key: str,
        context: RolloutContext,
    ) -> str:

        if context.user_id is not None:
            identity = f"user:{context.user_id}"
        elif context.tenant_id is not None:
            identity = f"tenant:{context.tenant_id}"
        elif context.website_id is not None:
            identity = f"website:{context.website_id}"
        else:
            identity = "global"

        return f"rollout:v2:{key}:{identity}"

    @staticmethod
    def _hash_to_bucket(value: str) -> float:

        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        numeric = int(digest[:12], 16)

        return (numeric % 10000) / 100