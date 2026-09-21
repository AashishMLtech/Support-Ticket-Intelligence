"""API request and response schemas."""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Natural-language query request."""

    question: str = Field(min_length=1, max_length=500)


class ErrorBody(BaseModel):
    """Standard error payload."""

    code: str
    message: str
