from users_state.engine.state_engine import StateEngine


class UserStateService:

    @staticmethod
    def suspend_user(*, user, reason: str, website=None):
        return StateEngine.transition(
            user=user,
            website=website,
            action="suspend",
            reason=reason,
        )

    @staticmethod
    def lift_suspension(*, user, website=None):
        return StateEngine.transition(
            user=user,
            website=website,
            action="lift_suspension",
        )

    @staticmethod
    def blacklist_user(*, user, reason: str, website=None):
        return StateEngine.transition(
            user=user,
            website=website,
            action="blacklist",
            reason=reason,
        )

    @staticmethod
    def lift_blacklist(*, user, website=None):
        return StateEngine.transition(
            user=user,
            website=website,
            action="lift_blacklist",
        )

    @staticmethod
    def put_on_probation(*, user, reason: str, website=None):
        return StateEngine.transition(
            user=user,
            website=website,
            action="probation",
            reason=reason,
        )

    @staticmethod
    def end_probation(*, user, website=None):
        return StateEngine.transition(
            user=user,
            website=website,
            action="end_probation",
        )