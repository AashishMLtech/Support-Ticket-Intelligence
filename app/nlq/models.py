"""Natural-language query models."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class QueryPlan(BaseModel):
    """Validated LLM query plan."""

    intent: Literal[
        "open_count",
        "top_resolved_agent_this_month",
        "critical_not_resolved_12h",
        "avg_rating_by_category",
        "anomaly_resolution_this_week",
        "out_of_scope",
    ]
    category: str | None = None
    assumptions: list[str] = Field(default_factory=list)

    @field_validator("assumptions", mode="before")
    @classmethod
    def normalize_assumptions(cls, value: object) -> list[str]:
        """Accept common LLM variants while preserving a list internally."""

        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [str(item) for item in value if str(item).strip()]
        return [str(value)]


class QueryResult(BaseModel):
    """Response envelope for NL queries."""

    answer: str
    intent: str
    rows: list[dict]
    row_count: int
    assumptions: list[str]
    warnings: list[str]
    as_of: str
    model: str
