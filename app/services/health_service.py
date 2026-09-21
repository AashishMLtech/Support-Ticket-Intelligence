"""Health service."""

from app.services.state import AppState


class HealthService:
    """Build health responses."""

    def __init__(self, state: AppState):
        self._state = state

    def get_health(self) -> dict:
        """Return system health and data quality."""

        configured = self._state.llm.configured
        return {
            "status": "ok" if configured else "degraded",
            "rows": self._state.repository.row_count,
            "as_of": str(self._state.as_of),
            "data_quality": self._state.quality_report,
            "llm": {
                "provider": "groq",
                "model": self._state.llm.model_name,
                "configured": configured,
            },
        }
