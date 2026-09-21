"""Data cleaning helpers."""

import pandas as pd


def clean_tickets(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize categorical text and stable sort-independent values."""

    cleaned = df.copy()
    for column in ["ticket_id", "category", "priority", "status", "agent_id", "issue_summary"]:
        cleaned[column] = cleaned[column].astype(str).str.strip()
    return cleaned
