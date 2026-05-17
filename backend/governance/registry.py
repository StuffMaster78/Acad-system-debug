from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommandDefinition:
    command_type: str
    reversible: bool
    requires_approval: bool


COMMAND_REGISTRY = {
    "user.suspend": CommandDefinition(
        command_type="user.suspend",
        reversible=True,
        requires_approval=True,
    ),
    "user.unsuspend": CommandDefinition(
        command_type="user.unsuspend",
        reversible=False,
        requires_approval=False,
    ),
    "user.blacklist": CommandDefinition(
        command_type="user.blacklist",
        reversible=True,
        requires_approval=True,
    ),
}