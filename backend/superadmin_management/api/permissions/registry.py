from dataclasses import dataclass


@dataclass(frozen=True)
class Permission:
    code: str
    description: str