from .discount import Discount  # re-export for tests expecting package-level import
try:
    from .seasonal_event import SeasonalEvent
except Exception:
    SeasonalEvent = None

__all__ = [
    "Discount",
    "SeasonalEvent",
]

