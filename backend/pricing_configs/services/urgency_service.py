from dataclasses import dataclass
from typing import Optional, Dict
import math


@dataclass
class UrgencyResult:
  """Result of urgency validation and normalization."""
  requested_hours: float
  normalized_hours: float
  was_adjusted: bool
  reason: Optional[str]
  level: str  # 'rush', 'same_day', 'standard'


class UrgencyService:
  """
  Pure-code urgency rules for rush orders.

  This service does NOT touch pricing directly (that is handled by
  DeadlineMultiplierService). Instead, it:
  - Enforces sane combinations of pages vs. minimum hours.
  - Classifies urgency level for UX (rush mode, same-day, standard).
  - Suggests safer deadlines when the request is too aggressive.

  These defaults follow the brainstormed rules:
    - 1 page:  >= 1 hour
    - 2 pages: >= 1–2 hours
    - 3 pages: >= 2–3 hours
    - 4 pages: >= 3 hours
    - 5 pages: >= 4 hours
    - 6 pages: >= 5 hours
    - 7+ pages: scale by ~1.5–2 hours per 5 pages, with same‑day cap.
  """

  @staticmethod
  def _min_hours_for_pages(pages: int) -> float:
    """
    Compute a minimum safe deadline (in hours) for a given page count.

    Business rules (from your brainstorm):
      - 1 page:  >= 1 hour
      - 2 pages: >= 1–2 hours  → min 1h
      - 3 pages: >= 2–3 hours  → min 2h
      - 4 pages: >= 3–4 hours  → min 3h
      - 5 pages: >= 5–6 hours  → min 5h
      - 6 pages: >= 5–7 hours  → min 5h
      - 7+ pages: no extra hard limit here (pricing handles the pressure),
        so we return 0 to indicate "no adjustment" beyond the global 1h floor.
    """
    if pages <= 0:
      return 1.0
    if pages == 1:
      return 1.0
    if pages == 2:
      return 1.0
    if pages == 3:
      return 2.0
    if pages == 4:
      return 3.0
    if pages == 5:
      return 5.0
    if pages == 6:
      return 5.0

    # For 7+ pages we don't enforce a special minimum – the global
    # lower bound in normalize_deadline (>=1h) plus price multipliers
    # will handle extreme rush pricing. Returning 0 means "no extra floor".
    return 0.0

  @staticmethod
  def classify_level(hours: float) -> str:
    """
    Classify urgency level for UX.

    - <= 6h  => 'rush'
    - <= 24h => 'same_day'
    - > 24h  => 'standard'
    """
    if hours <= 6:
      return 'rush'
    if hours <= 24:
      return 'same_day'
    return 'standard'

  @staticmethod
  def normalize_deadline(pages: int, requested_hours: float) -> UrgencyResult:
    """
    Normalize a requested deadline based on page count.

    If the requested deadline is too short for the number of pages,
    we bump it up to the minimum safe hours and mark the request
    as adjusted, so the frontend can message this to the client.
    """
    if requested_hours <= 0:
      requested_hours = 1.0

    min_hours = UrgencyService._min_hours_for_pages(pages)
    normalized = requested_hours
    was_adjusted = False
    reason = None

    if min_hours > 0 and requested_hours < min_hours:
      normalized = min_hours
      was_adjusted = True
      reason = (
        f"Requested deadline ({requested_hours:.1f}h) is too short for "
        f"{pages} page(s). Minimum allowed is {min_hours:.1f}h."
      )

    level = UrgencyService.classify_level(normalized)
    # Round to 1 decimal place to avoid tiny float noise
    normalized = round(normalized, 1)

    return UrgencyResult(
      requested_hours=requested_hours,
      normalized_hours=normalized,
      was_adjusted=was_adjusted,
      reason=reason,
      level=level,
    )

  @staticmethod
  def to_dict(result: UrgencyResult) -> Dict:
    """Convert UrgencyResult to a JSON‑friendly dict."""
    return {
      "requested_hours": float(result.requested_hours),
      "normalized_hours": float(result.normalized_hours),
      "was_adjusted": result.was_adjusted,
      "reason": result.reason,
      "level": result.level,
    }


