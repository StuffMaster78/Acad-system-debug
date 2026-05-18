from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class ConfigType(str, Enum):
    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    JSON = "json"
    LIST = "list"


@dataclass(slots=True)
class ConfigDefinition:
    """
    Master runtime config definition.
    """

    key: str

    config_type: ConfigType

    default: Any

    description: str = ""

    category: str = "general"

    is_sensitive: bool = False

    is_runtime_editable: bool = True

    requires_restart: bool = False

    is_locked: bool = False

    enable_rollout: bool = False

    cache_ttl_seconds: int = 300

    validator: Callable[[Any], bool] | None = None

    choices: list[Any] | None = None

    allowed_environments: list[str] = field(
        default_factory=lambda: [
            "dev",
            "staging",
            "prod",
        ]
    )