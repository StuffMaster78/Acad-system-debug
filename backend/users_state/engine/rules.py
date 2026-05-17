class StateRules:
    """
    Defines allowed transitions.
    """

    ALLOWED = {
        "suspend": ["active", "probation"],
        "lift_suspension": ["suspended"],
        "blacklist": ["active", "suspended"],
        "lift_blacklist": ["blacklisted"],
        "probation": ["active"],
        "end_probation": ["probation"],
    }

    @staticmethod
    def validate(current: str, action: str):
        allowed = StateRules.ALLOWED.get(action, [])

        if current not in allowed:
            raise ValueError(
                f"Invalid transition: {current} -> {action}"
            )