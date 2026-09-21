"""Data quality summary."""

import pandas as pd


def build_quality_report(df: pd.DataFrame) -> dict:
    """Return a compact data quality report for health/UI."""

    return {
        "null_counts": df.isna().sum().astype(int).to_dict(),
        "status_counts": df["status"].value_counts().astype(int).to_dict(),
        "category_counts": df["category"].value_counts().astype(int).to_dict(),
        "priority_counts": df["priority"].value_counts().astype(int).to_dict(),
        "resolution_before_response_count": int(df["dq_resolution_before_response"].sum()),
    }
