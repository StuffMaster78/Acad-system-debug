from __future__ import annotations

from typing import TYPE_CHECKING, Type
import difflib

from orders.registry.decorator import get_registered_action

if TYPE_CHECKING:  # avoid runtime import cycles
    from orders.actions.base import BaseOrderAction


def get_action_or_raise(name: str) -> "Type[BaseOrderAction]":
    """
    Return a registered order action class by name.

    Raises:
        KeyError: if the action name is not registered.
    """
    action = get_registered_action(name)
    if action:
        return action

    keys = list(get_registered_action_keys())  # type: ignore[name-defined]
    # lazy import to dodge circulars
    from orders.registry.decorator import get_registered_action_keys  # noqa

    keys = list(get_registered_action_keys())
    hint = ""
    if keys:
        close = difflib.get_close_matches(name, keys, n=3, cutoff=0.5)
        if close:
            hint = f" Did you mean: {', '.join(close)}?"

    raise KeyError(f"Unknown order action '{name}'.{hint}")


def run_action_or_raise(name: str, /, **kwargs):
    """
    Instantiate and run a registered order action by name.

    Raises:
        KeyError: if the action name is not registered.
    """
    cls = get_action_or_raise(name)
    return cls(**kwargs).execute()