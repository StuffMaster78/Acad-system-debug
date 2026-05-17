# superadmin_management/services/governance_state_machine.py

class GovernanceStateMachine:
    """
    Enforces valid transitions for user governance states.
    """

    VALID_TRANSITIONS = {
        "active": {"suspended", "blacklisted"},
        "suspended": {"active", "blacklisted"},
        "blacklisted": {"active"},
        "probation": {"suspended", "active"},
    }

    @staticmethod
    def can_transition(from_state: str, to_state: str) -> bool:
        return to_state in GovernanceStateMachine.VALID_TRANSITIONS.get(
            from_state, set()
        )