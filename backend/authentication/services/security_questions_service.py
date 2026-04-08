"""
Security Questions Service.

Manage security questions for account recovery.
"""

from typing import List

from django.core.exceptions import ValidationError
from django.db import transaction

from authentication.models.security_questions import (
    SecurityQuestion,
    UserSecurityQuestion,
)
from authentication.services.security_event_service import (
    SecurityEventService,
)
from authentication.models.security_events import SecurityEvent


class SecurityQuestionsService:
    """
    Manage security questions for a user within a website.
    """

    MIN_QUESTIONS = 2
    MAX_QUESTIONS = 5

    def __init__(self, user, website):
        if website is None:
            raise ValueError("Website context is required")

        self.user = user
        self.website = website

    def get_available_questions(self) -> List[SecurityQuestion]:
        return list(
            SecurityQuestion.objects.filter(is_active=True)
            .order_by("question_text")
        )

    def get_user_questions(self) -> List[UserSecurityQuestion]:
        return list(
            UserSecurityQuestion.objects.filter(
                user=self.user,
                website=self.website,
                is_active=True,
            ).select_related("question")
        )

    @transaction.atomic
    def set_security_questions(
        self,
        questions_data: List[dict],
    ) -> List[UserSecurityQuestion]:
        if len(questions_data) < self.MIN_QUESTIONS:
            raise ValidationError(
                f"At least {self.MIN_QUESTIONS} questions required"
            )

        if len(questions_data) > self.MAX_QUESTIONS:
            raise ValidationError(
                f"Maximum {self.MAX_QUESTIONS} questions allowed"
            )

        # deactivate existing
        UserSecurityQuestion.objects.filter(
            user=self.user,
            website=self.website,
        ).update(is_active=False)

        created = []
        used_ids = set()

        for q_data in questions_data:
            question_id = q_data.get("question_id")
            answer = (q_data.get("answer") or "").strip()

            if not question_id:
                raise ValidationError("question_id is required")

            if question_id in used_ids:
                raise ValidationError("Duplicate questions not allowed")

            used_ids.add(question_id)

            if len(answer) < 3:
                raise ValidationError("Answer too short")

            try:
                question = SecurityQuestion.objects.get(
                    id=question_id,
                    is_active=True,
                )
            except SecurityQuestion.DoesNotExist:
                raise ValidationError("Invalid question")

            uq = UserSecurityQuestion.objects.create(
                user=self.user,
                website=self.website,
                question=question,
                is_active=True,
            )

            uq.set_answer(answer)
            uq.save()

            created.append(uq)

        SecurityEventService.log(
            user=self.user,
            website=self.website,
            event_type=SecurityEvent.EventType.PROFILE_UPDATED,
            metadata={"action": "security_questions_set"},
        )

        return created

    def verify_answers(self, answers: List[dict]) -> bool:
        user_questions = self.get_user_questions()

        if len(answers) != len(user_questions):
            return False

        question_map = {
            q.question.pk: q for q in user_questions
        }

        correct = 0

        for answer_data in answers:
            qid = answer_data.get("question_id")
            answer = (answer_data.get("answer") or "").strip()

            uq = question_map.get(qid)
            if not uq:
                continue

            if uq.verify_answer(answer):
                correct += 1
            else:
                uq.failed_attempts += 1
                uq.save(update_fields=["failed_attempts"])

        success = correct == len(user_questions)

        SecurityEventService.log(
            user=self.user,
            website=self.website,
            event_type=(
                SecurityEvent.EventType.PROFILE_UPDATED
                if success
                else SecurityEvent.EventType.SUSPICIOUS_ACTIVITY
            ),
            severity=(
                SecurityEvent.Severity.LOW
                if success
                else SecurityEvent.Severity.MEDIUM
            ),
            is_suspicious=not success,
            metadata={
                "action": "security_questions_verification",
                "correct_answers": correct,
                "total": len(user_questions),
            },
        )

        return success

    def can_use_for_recovery(self) -> bool:
        return (
            len(self.get_user_questions()) >= self.MIN_QUESTIONS
        )

    def delete_all_questions(self) -> None:
        UserSecurityQuestion.objects.filter(
            user=self.user,
            website=self.website,
        ).delete()