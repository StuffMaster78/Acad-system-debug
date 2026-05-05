from __future__ import annotations

import re

from django.core.exceptions import ValidationError

from communications.models.screening_rule import CommunicationScreeningMatchType


class CommunicationScreeningRuleValidator:
    """
    Validators for communication screening rules.
    """

    @staticmethod
    def validate_pattern(
        *,
        pattern: str,
        match_type: str,
    ) -> None:
        """
        Validate screening pattern.
        """
        if not pattern or not pattern.strip():
            raise ValidationError("Screening pattern cannot be empty.")

        if match_type == CommunicationScreeningMatchType.REGEX:
            try:
                re.compile(pattern)
            except re.error as exc:
                raise ValidationError(
                    f"Invalid regular expression: {exc}",
                ) from exc

    @staticmethod
    def validate_platform_rule(*, website, is_platform_rule: bool) -> None:
        """
        Validate platform rule consistency.
        """
        if is_platform_rule and website is not None:
            raise ValidationError(
                "Platform rules should not be tied to a website.",
            )

        if not is_platform_rule and website is None:
            raise ValidationError(
                "Website specific rules require a website.",
            )