# # notifications_system/registry/decorator.py
# from __future__ import annotations
# import functools
# from .validator import validate_event_pair
# from .events import register_event

# PRIORITY_MAP = {3:"low",5:"medium",7:"high",9:"critical"}

# def notification_event(event_key: str, **cfg):
#     p = cfg.get("priority")
#     if isinstance(p, int) and p in PRIORITY_MAP:
#         cfg = {**cfg, "priority": PRIORITY_MAP[p]}

#     res = validate_event_pair(event_key, cfg)
#     if not res.ok:
#         raise ValueError(f"Invalid event {event_key}: {res.errors}")

#     def deco(obj=None):
#         register_event(event_key, **cfg)
#         if obj is None:
#             return None
#         @functools.wraps(obj)
#         def wrapper(*a, **kw): return obj(*a, **kw)
#         return wrapper
#     return deco
