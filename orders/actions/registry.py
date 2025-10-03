# Minimal central registry for order actions (class- or function-based)
from __future__ import annotations
from typing import Dict, Type, Callable, Any

class OrderActionRegistry:
    _map: Dict[str, Type[Any] | Callable[..., Any]] = {}

    @classmethod
    def register(cls, key: str, handler: Type[Any] | Callable[..., Any]) -> None:
        if not key:
            raise ValueError("Action key must be non-empty")
        cls._map[key] = handler

    @classmethod
    def get(cls, key: str):
        return cls._map.get(key)

    @classmethod
    def all(cls) -> Dict[str, Type[Any] | Callable[..., Any]]:
        return dict(cls._map)


# Optional: decorator for function-style actions
def register_action(key: str):
    def deco(fn: Callable[..., Any]):
        OrderActionRegistry.register(key, fn)
        return fn
    return deco