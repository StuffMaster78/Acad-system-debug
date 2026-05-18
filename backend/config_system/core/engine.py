from __future__ import annotations

from config_system.registry import require_config_definition
from backend.config_system.rollout.cohort_engine import (
    CohortEngine,
    RolloutContext,
    RolloutRule,
)
from config_system.rollout.kill_switch import KillSwitchEngine
from config_system.services.evaluator import ConfigEvaluator


class FeatureEngine:
    """
    Central runtime feature evaluation engine.

    Responsibilities:
        - config evaluation
        - rollout orchestration
        - kill switch enforcement
        - cohort targeting
        - single runtime decision API
    """

    @classmethod
    def is_enabled(
        cls,
        *,
        key: str,
        context: RolloutContext | None = None,
        rules: list[RolloutRule] | None = None,
    ) -> bool:

        context = context or RolloutContext()

        # -----------------------------------------------------
        # Kill switch override
        # -----------------------------------------------------

        if KillSwitchEngine.is_disabled(
            key=key,
            user_id=context.user_id,
            tenant_id=context.tenant_id,
            website_id=context.website_id,
        ):
            return False

        # -----------------------------------------------------
        # Registry definition
        # -----------------------------------------------------

        definition = require_config_definition(key)

        # -----------------------------------------------------
        # Base feature enablement
        # -----------------------------------------------------

        enabled = ConfigEvaluator.get(
            key,
            user_id=context.user_id,
            tenant_id=context.tenant_id,
            website_id=context.website_id,
        )

        if not bool(enabled):
            return False

        # -----------------------------------------------------
        # Rollout support
        # -----------------------------------------------------

        if not definition.enable_rollout:
            return True

        rollout_percentage = cls._get_rollout_percentage(
            key=key,
            context=context,
        )

        return CohortEngine.is_enabled(
            key=key,
            percentage=rollout_percentage,
            context=context,
            rules=rules,
        )

    # ---------------------------------------------------------
    # Rollout resolution
    # ---------------------------------------------------------

    @classmethod
    def _get_rollout_percentage(
        cls,
        *,
        key: str,
        context: RolloutContext,
    ) -> float:

        rollout_key = f"{key}.rollout_percentage"

        percentage = ConfigEvaluator.get(
            rollout_key,
            user_id=context.user_id,
            tenant_id=context.tenant_id,
            website_id=context.website_id,
        )

        if percentage is None:
            return 100

        try:
            percentage = float(percentage)
        except (TypeError, ValueError):
            return 0

        return max(0, min(100, percentage))