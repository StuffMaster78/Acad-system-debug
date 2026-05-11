from __future__ import annotations

from typing import Any

from tips.models.tip_financial_trace import TipFinancialTrace


class TraceService:
    """
    Immutable operational execution traces.

    Used for:
        - forensic debugging
        - payment investigations
        - webhook replay analysis
        - distributed tracing
        - support diagnostics
    """

    @staticmethod
    def record(
        *,
        tip,
        step: str,
        status: str,
        metadata: dict[str, Any] | None = None,
        actor=None,
        correlation_id: str = "",
        source: str = "",
        severity: str = "info",
    ) -> TipFinancialTrace:

        return TipFinancialTrace.objects.create(
            tip=tip,
            step=step,
            status=status,
            metadata=metadata or {},
            actor=actor,
            correlation_id=correlation_id,
            source=source,
            severity=severity,
        )