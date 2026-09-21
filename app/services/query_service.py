"""Natural-language query service."""

from app.nlq.executor import execute_plan
from app.nlq.planner import plan_question
from app.services.state import AppState


class QueryService:
    """Coordinate LLM planning and deterministic execution."""

    def __init__(self, state: AppState):
        self._state = state

    def ask(self, question: str) -> dict:
        """Answer a support-ticket question."""

        plan = plan_question(question, self._state.llm)
        result = execute_plan(
            plan,
            self._state.repository.tickets,
            self._state.as_of,
            self._state.llm.model_name,
        )
        return result.model_dump()
