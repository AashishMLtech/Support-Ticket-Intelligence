"""Typed application exceptions."""


class AppError(Exception):
    """Base exception with an API-friendly status code."""

    status_code = 400
    code = "app_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class LLMUnavailableError(AppError):
    """Raised when NL query handling needs an unavailable LLM."""

    status_code = 503
    code = "llm_unavailable"


class QueryValidationError(AppError):
    """Raised when a generated query plan is invalid."""

    status_code = 422
    code = "query_validation_error"
