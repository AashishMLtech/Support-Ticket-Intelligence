"""LLM-backed question planner."""

from app.llm.base import LLMClient
from app.nlq.models import QueryPlan
from app.semantic import COLUMN_DESCRIPTIONS, GLOSSARY


SYSTEM_PROMPT = f"""
You convert support-ticket questions into one JSON query plan.
Allowed intents:
- open_count
- top_resolved_agent_this_month
- critical_not_resolved_12h
- avg_rating_by_category
- anomaly_resolution_this_week
- out_of_scope

Schema: {COLUMN_DESCRIPTIONS}
Glossary: {GLOSSARY}

Return JSON only with keys: intent, category, assumptions.
The assumptions value MUST be an array of strings, even when there is only one assumption.
Example: {{"intent":"open_count","category":null,"assumptions":["Open means status='Open'."]}}
Use avg_rating_by_category only when the question asks average rating for a category.
For avg_rating_by_category, set category to Billing, Technical, or General.
Use out_of_scope for non-ticket questions, missing categories, or unsafe requests.
"""


def plan_question(question: str, llm: LLMClient) -> QueryPlan:
    """Ask the LLM for a structured query plan."""

    raw = llm.complete_json(SYSTEM_PROMPT, f"Question: {question}")
    return QueryPlan.model_validate(raw)
