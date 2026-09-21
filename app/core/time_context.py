"""As-of date handling."""

from datetime import datetime

import pandas as pd


def resolve_as_of(max_created_at: pd.Timestamp, override: str | None = None) -> pd.Timestamp:
    """Return the timestamp used for relative time calculations."""

    if not override:
        return max_created_at
    parsed = pd.to_datetime(override, errors="raise")
    if isinstance(parsed, datetime):
        return pd.Timestamp(parsed)
    return parsed
