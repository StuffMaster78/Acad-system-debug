from __future__ import annotations

import json
from typing import Any


class CommunicationSSEEventFormatter:
    """
    Responsible for formatting events for SSE delivery.

    Keeps event structure consistent across the system.
    """

    @staticmethod
    def build_event(
        *,
        event_type: str,
        payload: dict[str, Any],
        meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Build internal event structure.
        """
        return {
            "event": event_type,
            "data": {
                "type": event_type,
                "payload": payload,
                "meta": meta or {},
            },
        }

    @staticmethod
    def format(
        *,
        event: str,
        data: dict[str, Any],
        event_id: str | None = None,
    ) -> str:
        """
        Format event into SSE protocol string.
        """
        lines: list[str] = []

        if event_id:
            lines.append(f"id: {event_id}")

        lines.append(f"event: {event}")
        lines.append(f"data: {json.dumps(data)}")

        return "\n".join(lines) + "\n\n"