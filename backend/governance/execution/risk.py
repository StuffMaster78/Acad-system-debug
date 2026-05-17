from governance.contracts.command import Command


class RiskEngine:
    """
    Simple deterministic risk scoring.

    Later becomes ML / anomaly driven.
    """

    @staticmethod
    def score(command: Command) -> float:

        base = 10.0

        if command.command_type in [
            "user.delete",
            "user.blacklist",
        ]:
            base += 70

        if command.actor_id == 1:  # superadmin example
            base -= 30

        return max(0.0, min(100.0, base))