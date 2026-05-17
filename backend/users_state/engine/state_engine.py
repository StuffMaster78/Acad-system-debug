from users_state.resolvers.user_state_resolver import (
    UserStateResolver,
)
from users_state.engine.rules import StateRules
from users_state.engine.events import (
    UserSuspended,
    UserBlacklisted,
    UserProbationStarted,
)
from users_state.tasks.tasks import process_user_state_event

class StateEngine:
    """
    Central engine for all user state transitions.
    """

    @staticmethod
    def transition(*, user, website, action: str, reason: str = ""):
        """
        Executes a validated state transition.
        """

        state = UserStateResolver.get(user=user, website=website)

        current = StateEngine._current_state(state)

        StateRules.validate(current, action)

        event = None

        if action == "suspend":
            state.is_suspended = True
            state.suspension_reason = reason
            event = UserSuspended(
                user_id=user.id,
                website_id=getattr(website, "id", None),
                action=action,
                reason=reason,
            )

        elif action == "lift_suspension":
            state.is_suspended = False
            state.suspension_reason = None

        elif action == "blacklist":
            state.is_blacklisted = True
            state.blacklist_reason = reason
            event = UserBlacklisted(
                user_id=user.id,
                website_id=getattr(website, "id", None),
                action=action,
                reason=reason,
            )

        elif action == "lift_blacklist":
            state.is_blacklisted = False
            state.blacklist_reason = None

        elif action == "probation":
            state.is_on_probation = True
            state.probation_reason = reason
            event = UserProbationStarted(
                user_id=user.id,
                website_id=getattr(website, "id", None),
                action=action,
                reason=reason,
            )

        elif action == "end_probation":
            state.is_on_probation = False
            state.probation_reason = None

        state.save()

        if event:
            StateEngine._emit(event)

        return state

    @staticmethod
    def _current_state(state) -> str:
        """
        Derives logical state name.
        Priority order matters.
        """

        if state.is_blacklisted:
            return "blacklisted"

        if state.is_suspended:
            return "suspended"

        if state.is_on_probation:
            return "probation"

        return "active"

    @staticmethod
    def _emit(event):
        """
        Sends event to Celery for async processing.
        """

        payload = {
            "type": event.__class__.__name__,
            "user_id": event.user_id,
            "website_id": event.website_id,
            "reason": getattr(event, "reason", ""),
            "actor_id": getattr(event, "actor_id", None),
        }

        process_user_state_event.delay(payload)