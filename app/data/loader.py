"""CSV loading and validation."""

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "ticket_id",
    "created_at",
    "category",
    "priority",
    "status",
    "response_time_hrs",
    "resolution_time_hrs",
    "agent_id",
    "customer_rating",
    "issue_summary",
}

ALIASES = {
    "resp_time_hrs": "response_time_hrs",
    "resol_time_hrs": "resolution_time_hrs",
    "cust_rating": "customer_rating",
}


def load_tickets(path: Path) -> pd.DataFrame:
    """Load the support-ticket CSV and validate expected columns."""

    df = pd.read_csv(path).rename(columns=ALIASES)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"CSV is missing required columns: {missing_list}")
    df = df[list(REQUIRED_COLUMNS)].copy()
    df["created_at"] = pd.to_datetime(df["created_at"], errors="raise")
    return df
