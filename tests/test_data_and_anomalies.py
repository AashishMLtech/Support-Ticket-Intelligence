"""Dataset and anomaly regression tests."""

import pandas as pd

from app.anomaly.engine import detect_anomalies
from app.core.config import Settings
from app.services.state import build_state


def test_dataset_facts_match_assessment_csv():
    state = build_state(Settings(groq_api_key=None))
    df = state.repository.tickets

    assert len(df) == 500
    assert df["status"].value_counts().to_dict() == {
        "Resolved": 327,
        "Open": 111,
        "Escalated": 62,
    }
    assert int(df["resolution_time_hrs"].isna().sum()) == 173
    assert int(df["customer_rating"].isna().sum()) == 173
    assert str(df["created_at"].min()) == "2024-01-01 08:54:00"
    assert str(df["created_at"].max()) == "2024-03-30 18:06:00"
    assert int(df["dq_resolution_before_response"].sum()) == 28


def test_important_query_ground_truth_values():
    state = build_state(Settings(groq_api_key=None))
    df = state.repository.tickets
    as_of = state.as_of

    critical_late = (
        df["priority"].eq("Critical")
        & (
            (df["status"].eq("Resolved") & (df["resolution_time_hrs"] > 12))
            | (~df["status"].eq("Resolved") & (df["age_hours"] > 12))
        )
    )
    stale = df["priority"].isin(["High", "Critical"]) & df["status"].isin(["Open", "Escalated"]) & (df["age_hours"] > 24)
    march_resolved = df[df["status"].eq("Resolved") & df["created_month"].eq(as_of.strftime("%Y-%m"))]

    assert int(df["status"].eq("Open").sum()) == 111
    assert int(critical_late.sum()) == 34
    assert int(stale.sum()) == 80
    assert march_resolved.groupby("agent_id").size().idxmax() == "AGT-01"
    assert int(march_resolved.groupby("agent_id").size().max()) == 16


def test_anomaly_rules_return_expected_counts():
    state = build_state(Settings(groq_api_key=None))
    df = state.repository.tickets

    assert len(detect_anomalies(df, state.as_of, rule="data_integrity", limit=1000)) == 28
    assert len(detect_anomalies(df, state.as_of, rule="stale_unresolved", limit=1000)) == 80
    assert len(detect_anomalies(df, state.as_of, rule="resolution_outlier", limit=1000)) == 18
