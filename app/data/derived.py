"""Derived ticket columns."""

import pandas as pd


def add_derived_columns(df: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    """Add semantic columns used by query and anomaly services."""

    derived = df.copy()
    derived["is_resolved"] = derived["status"].eq("Resolved")
    derived["is_unresolved"] = derived["status"].isin(["Open", "Escalated"])
    derived["age_hours"] = (as_of - derived["created_at"]).dt.total_seconds() / 3600
    derived["created_date"] = derived["created_at"].dt.date.astype(str)
    derived["created_month"] = derived["created_at"].dt.strftime("%Y-%m")
    derived["created_week_start"] = (
        derived["created_at"] - pd.to_timedelta(derived["created_at"].dt.weekday, unit="D")
    ).dt.date.astype(str)
    derived["dq_resolution_before_response"] = (
        derived["resolution_time_hrs"].notna()
        & (derived["resolution_time_hrs"] < derived["response_time_hrs"])
    )
    return derived
