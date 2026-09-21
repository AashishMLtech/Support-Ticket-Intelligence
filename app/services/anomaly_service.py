"""Anomaly service."""

from app.anomaly.engine import detect_anomalies
from app.services.state import AppState


class AnomalyService:
    """Run deterministic anomaly detection."""

    def __init__(self, state: AppState):
        self._state = state

    def list_anomalies(
        self,
        rule: str | None = None,
        priority: str | None = None,
        limit: int = 100,
    ) -> dict:
        """Return anomaly flags and summary counts."""

        flags = detect_anomalies(
            self._state.repository.tickets,
            self._state.as_of,
            rule=rule,
            priority=priority,
            limit=limit,
        )
        counts: dict[str, int] = {}
        for flag in flags:
            counts[flag["rule_id"]] = counts.get(flag["rule_id"], 0) + 1
        return {
            "as_of": str(self._state.as_of),
            "count": len(flags),
            "counts_by_rule": counts,
            "rows": flags,
        }
