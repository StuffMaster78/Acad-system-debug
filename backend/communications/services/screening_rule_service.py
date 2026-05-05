from __future__ import annotations

from communications.models.screening_rule import (
    CommunicationScreeningRule,
)
from communications.validators import CommunicationScreeningRuleValidator


class CommunicationScreeningRuleService:
    """
    Manage admin configurable communication screening rules.
    """

    @staticmethod
    def create_rule(
        *,
        name: str,
        pattern: str,
        match_type: str,
        action: str,
        severity: str,
        website=None,
        replacement_text: str = "*****",
        reason: str = "",
        is_platform_rule: bool = False,
        created_by=None,
        metadata: dict | None = None,
    ) -> CommunicationScreeningRule:
        """
        Create a screening rule.
        """
        CommunicationScreeningRuleValidator.validate_pattern(
            pattern=pattern,
            match_type=match_type,
        )
        CommunicationScreeningRuleValidator.validate_platform_rule(
            website=website,
            is_platform_rule=is_platform_rule,
        )
        
        return CommunicationScreeningRule.objects.create(
            website=website,
            name=name,
            pattern=pattern,
            match_type=match_type,
            action=action,
            severity=severity,
            replacement_text=replacement_text,
            reason=reason,
            is_platform_rule=is_platform_rule,
            created_by=created_by,
            updated_by=created_by,
            metadata=metadata or {},
        )

    @staticmethod
    def update_rule(
        *,
        rule,
        actor=None,
        name: str | None = None,
        pattern: str | None = None,
        match_type: str | None = None,
        action: str | None = None,
        severity: str | None = None,
        replacement_text: str | None = None,
        reason: str | None = None,
        is_active: bool | None = None,
        metadata: dict | None = None,
    ):
        """
        Update a screening rule.
        """
        update_fields: list[str] = []

        if name is not None:
            rule.name = name
            update_fields.append("name")

        if pattern is not None:
            rule.pattern = pattern
            update_fields.append("pattern")

        if match_type is not None:
            rule.match_type = match_type
            update_fields.append("match_type")

        if action is not None:
            rule.action = action
            update_fields.append("action")

        if severity is not None:
            rule.severity = severity
            update_fields.append("severity")

        if replacement_text is not None:
            rule.replacement_text = replacement_text
            update_fields.append("replacement_text")

        if reason is not None:
            rule.reason = reason
            update_fields.append("reason")

        if is_active is not None:
            rule.is_active = is_active
            update_fields.append("is_active")

        if metadata is not None:
            rule.metadata = metadata
            update_fields.append("metadata")

        if actor is not None:
            rule.updated_by = actor
            update_fields.append("updated_by")

        if update_fields:
            update_fields.append("updated_at")
            rule.save(update_fields=update_fields)

        return rule

    @staticmethod
    def deactivate_rule(*, rule, actor=None):
        """
        Deactivate a screening rule.
        """
        rule.is_active = False
        if actor is not None:
            rule.updated_by = actor
            rule.save(update_fields=["is_active", "updated_by", "updated_at"])
            return rule

        rule.save(update_fields=["is_active", "updated_at"])
        return rule