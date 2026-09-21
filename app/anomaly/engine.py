"""Deterministic anomaly detection."""

import pandas as pd


def detect_anomalies(
    tickets: pd.DataFrame,
    as_of: pd.Timestamp,
    rule: str | None = None,
    priority: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """Return explainable anomaly flags."""

    data = tickets.copy()
    if priority:
        data = data[data["priority"].eq(priority)]

    flags: list[dict] = []
    enabled = {rule} if rule else {"resolution_outlier", "stale_unresolved", "response_sla", "data_integrity"}

    if "resolution_outlier" in enabled:
        resolved = data[data["status"].eq("Resolved")]
        for pri, group in resolved.groupby("priority"):
            if len(group) < 10:
                continue
            q1 = group["resolution_time_hrs"].quantile(0.25)
            q3 = group["resolution_time_hrs"].quantile(0.75)
            fence = q3 + 1.5 * (q3 - q1)
            for _, row in group[group["resolution_time_hrs"] > fence].iterrows():
                flags.append(_flag(row, "resolution_outlier", "medium", f"Resolution time exceeds {pri} IQR fence.", row["resolution_time_hrs"], round(float(fence), 2), as_of))

    if "stale_unresolved" in enabled:
        mask = data["priority"].isin(["High", "Critical"]) & data["status"].isin(["Open", "Escalated"]) & (data["age_hours"] > 24)
        for _, row in data[mask].iterrows():
            severity = "high" if row["age_hours"] > 72 else "medium"
            flags.append(_flag(row, "stale_unresolved", severity, "High/Critical unresolved ticket older than 24 hours.", round(float(row["age_hours"]), 2), 24, as_of))

    if "response_sla" in enabled:
        for _, row in data[data["response_time_hrs"] > 4].iterrows():
            flags.append(_flag(row, "response_sla", "low", "Response time exceeds the assumed 4-hour SLA.", row["response_time_hrs"], 4, as_of))

    if "data_integrity" in enabled:
        for _, row in data[data["dq_resolution_before_response"]].iterrows():
            flags.append(_flag(row, "data_integrity", "high", "Resolution time is earlier than first response time.", row["resolution_time_hrs"], row["response_time_hrs"], as_of))

    return flags[:limit]


def _flag(row: pd.Series, rule_id: str, severity: str, reason: str, evidence: float, threshold: float, as_of: pd.Timestamp) -> dict:
    return {
        "rule_id": rule_id,
        "severity": severity,
        "ticket_id": row["ticket_id"],
        "priority": row["priority"],
        "status": row["status"],
        "reason": reason,
        "evidence": evidence,
        "threshold": threshold,
        "as_of": str(as_of),
    }
