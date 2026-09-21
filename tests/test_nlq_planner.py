"""NLQ planner regression tests."""

from app.nlq.models import QueryPlan
from app.nlq.planner import plan_question


class FakeLLM:
    """Scripted LLM for planner tests."""

    configured = True
    model_name = "fake"

    def __init__(self, response: dict):
        self.response = response

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        return self.response


def test_query_plan_normalizes_string_assumption():
    plan = QueryPlan.model_validate(
        {
            "intent": "open_count",
            "category": None,
            "assumptions": "Open tickets are those with status='Open'.",
        }
    )

    assert plan.assumptions == ["Open tickets are those with status='Open'."]


def test_planner_accepts_llm_string_assumption():
    plan = plan_question(
        "How many tickets are currently open?",
        FakeLLM(
            {
                "intent": "open_count",
                "category": None,
                "assumptions": "Open tickets exclude Escalated tickets.",
            }
        ),
    )

    assert plan.intent == "open_count"
    assert plan.assumptions == ["Open tickets exclude Escalated tickets."]
