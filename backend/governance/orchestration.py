from __future__ import annotations

from governance.command_bus import CommandBus


class GovernanceOrchestrator:
    """
    High-level governance execution orchestrator.

    Coordinates:
    - command execution
    - approval routing
    - policy checks
    - replay
    - rollback
    """

    @staticmethod
    def execute(
        *,
        user_id: int,
        tenant_id: int,
        role: str,
        command_type: str,
        payload: dict,
    ):

        return CommandBus.dispatch(
            user_id=user_id,
            tenant_id=tenant_id,
            role=role,
            command_type=command_type,
            payload=payload,
        )