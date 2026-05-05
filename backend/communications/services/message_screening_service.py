from __future__ import annotations

import re
from dataclasses import dataclass

from django.core.exceptions import ValidationError

from communications.constants import CommunicationMessageStatus
from communications.models import CommunicationModerationSeverity
from communications.models import CommunicationScreeningAction
from communications.models import CommunicationScreeningMatchType
from communications.selectors.screening_rule_selectors import (
    CommunicationScreeningRuleSelector,
)
from communications.services.link_review_service import (
    CommunicationLinkReviewService,
)
from communications.services.moderation_service import (
    CommunicationModerationService,
)


PHONE_REGEX = re.compile(
    r"(\+?\d{1,3}[\s\-]?)?"
    r"(\(?\d{2,4}\)?[\s\-]?)?"
    r"\d{3,4}[\s\-]?\d{3,4}"
)

EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
)

URL_REGEX = re.compile(
    r"(https?://[^\s]+|www\.[^\s]+)"
)


@dataclass(frozen=True)
class ScreeningResult:
    """
    Result returned after screening a message.
    """

    cleaned_text: str
    has_phone: bool
    has_email: bool
    has_link: bool
    flagged: bool
    held_for_review: bool
    blocked: bool
    matched_rules: list[str]


class CommunicationMessageScreeningService:
    """
    Central message screening service.

    Responsible for:
        - detecting phone numbers
        - detecting emails
        - detecting links
        - applying admin configured screening rules
        - masking unsafe content
        - creating moderation flags
        - creating pending link reviews
    """

    MASK = "*****"

    @classmethod
    def screen(
        cls,
        *,
        message_body: str,
        message,
        actor=None,
    ) -> ScreeningResult:
        """
        Screen a message and return sanitized output.

        This method is called by CommunicationMessageService after message
        creation and before final message state is returned.
        """
        cleaned_text = message_body
        matched_rules: list[str] = []

        has_phone = bool(PHONE_REGEX.search(cleaned_text))
        has_email = bool(EMAIL_REGEX.search(cleaned_text))
        links = URL_REGEX.findall(cleaned_text)
        has_link = bool(links)

        if has_phone:
            cleaned_text = PHONE_REGEX.sub(cls.MASK, cleaned_text)

        if has_email:
            cleaned_text = EMAIL_REGEX.sub(cls.MASK, cleaned_text)

        flagged = has_phone or has_email or has_link
        held_for_review = False
        blocked = False

        rule_result = cls._apply_configured_rules(
            website=message.website,
            text=cleaned_text,
        )

        cleaned_text = rule_result.cleaned_text
        matched_rules.extend(rule_result.matched_rules)

        flagged = flagged or rule_result.flagged
        held_for_review = rule_result.held_for_review
        blocked = rule_result.blocked

        for link in links:
            CommunicationLinkReviewService.create_review(
                message=message,
                url=link,
                submitted_by=actor,
                metadata={
                    "source": "message_screening",
                },
            )

        if blocked:
            raise ValidationError(
                "This message contains blocked content."
            )

        if held_for_review:
            message.status = CommunicationMessageStatus.HELD_FOR_REVIEW
            message.save(update_fields=["status", "updated_at"])

        elif flagged:
            message.status = CommunicationMessageStatus.FLAGGED
            message.save(update_fields=["status", "updated_at"])

        if flagged or held_for_review:
            CommunicationModerationService.flag_message(
                message=message,
                reason="message_screening",
                severity=CommunicationModerationSeverity.HIGH,
                created_by=actor,
                details="Message matched screening rules or unsafe content.",
                metadata={
                    "has_phone": has_phone,
                    "has_email": has_email,
                    "has_link": has_link,
                    "matched_rules": matched_rules,
                },
            )

        return ScreeningResult(
            cleaned_text=cleaned_text,
            has_phone=has_phone,
            has_email=has_email,
            has_link=has_link,
            flagged=flagged,
            held_for_review=held_for_review,
            blocked=blocked,
            matched_rules=matched_rules,
        )

    @classmethod
    def _apply_configured_rules(
        cls,
        *,
        website,
        text: str,
    ) -> ScreeningResult:
        """
        Apply admin configured screening rules.
        """
        cleaned_text = text
        flagged = False
        held_for_review = False
        blocked = False
        matched_rules: list[str] = []

        rules = CommunicationScreeningRuleSelector.active_for_website(
            website=website,
        )

        for rule in rules:
            if not cls._rule_matches(rule=rule, text=cleaned_text):
                continue

            matched_rules.append(rule.name)

            if rule.action == CommunicationScreeningAction.MASK:
                cleaned_text = cls._mask_rule_match(
                    rule=rule,
                    text=cleaned_text,
                )
                flagged = True

            elif rule.action == CommunicationScreeningAction.FLAG:
                flagged = True

            elif rule.action == CommunicationScreeningAction.HOLD_FOR_REVIEW:
                held_for_review = True
                flagged = True

            elif rule.action == CommunicationScreeningAction.HIDE:
                held_for_review = True
                flagged = True

            elif rule.action == CommunicationScreeningAction.BLOCK:
                blocked = True

        return ScreeningResult(
            cleaned_text=cleaned_text,
            has_phone=False,
            has_email=False,
            has_link=False,
            flagged=flagged,
            held_for_review=held_for_review,
            blocked=blocked,
            matched_rules=matched_rules,
        )

    @classmethod
    def _rule_matches(cls, *, rule, text: str) -> bool:
        """
        Return whether a screening rule matches text.
        """
        if rule.match_type == CommunicationScreeningMatchType.EXACT:
            return text.strip().lower() == rule.pattern.strip().lower()

        if rule.match_type == CommunicationScreeningMatchType.CONTAINS:
            return rule.pattern.lower() in text.lower()

        if rule.match_type == CommunicationScreeningMatchType.REGEX:
            try:
                return bool(
                    re.search(
                        rule.pattern,
                        text,
                        flags=re.IGNORECASE,
                    ),
                )
            except re.error:
                return False

        return False

    @classmethod
    def _mask_rule_match(cls, *, rule, text: str) -> str:
        """
        Mask matched text for a screening rule.
        """
        replacement = rule.replacement_text or cls.MASK

        if rule.match_type == CommunicationScreeningMatchType.EXACT:
            if text.strip().lower() == rule.pattern.strip().lower():
                return replacement
            return text

        if rule.match_type == CommunicationScreeningMatchType.CONTAINS:
            return re.sub(
                re.escape(rule.pattern),
                replacement,
                text,
                flags=re.IGNORECASE,
            )

        if rule.match_type == CommunicationScreeningMatchType.REGEX:
            try:
                return re.sub(
                    rule.pattern,
                    replacement,
                    text,
                    flags=re.IGNORECASE,
                )
            except re.error:
                return text

        return text