from django.core.exceptions import ValidationError


class DraftWorkflow:
    TRANSITIONS = {
        "submitted": {"reviewed", "revision_requested"},
        "revision_requested": {"submitted"},
        "reviewed": set(),
    }

    @classmethod
    def ensure_can_transition(cls, current: str, next_: str):
        if next_ not in cls.TRANSITIONS.get(current, set()):
            raise ValidationError(
                f"Cannot move draft from {current} to {next_}"
            )