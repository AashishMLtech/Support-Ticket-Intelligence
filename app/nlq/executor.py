"""Deterministic execution of validated NL query plans."""

import pandas as pd

from app.nlq.models import QueryPlan, QueryResult


def execute_plan(plan: QueryPlan, tickets: pd.DataFrame, as_of: pd.Timestamp, model: str) -> QueryResult:
    """Execute a supported query plan against ticket data."""

    assumptions = list(plan.assumptions)
    rows: list[dict]
    answer: str

    if plan.intent == "open_count":
        count = int(tickets["status"].eq("Open").sum())
        assumptions.append("Open means status='Open'; Escalated tickets are excluded.")
        rows = [{"status": "Open", "ticket_count": count}]
        answer = f"There are {count} currently open tickets."

    elif plan.intent == "top_resolved_agent_this_month":
        month = as_of.strftime("%Y-%m")
        filtered = tickets[(tickets["status"].eq("Resolved")) & (tickets["created_month"].eq(month))]
        counts = filtered.groupby("agent_id").size().reset_index(name="resolved_tickets")
        if counts.empty:
            rows = []
            answer = f"No tickets were resolved in {month}."
        else:
            max_count = int(counts["resolved_tickets"].max())
            rows = counts[counts["resolved_tickets"].eq(max_count)].to_dict("records")
            agents = ", ".join(row["agent_id"] for row in rows)
            answer = f"{agents} resolved the most tickets this month, with {max_count} tickets."
        assumptions.append("This month uses created_at month because the dataset has no resolved_at column.")

    elif plan.intent == "critical_not_resolved_12h":
        mask = (tickets["priority"].eq("Critical")) & (
            ((tickets["status"].eq("Resolved")) & (tickets["resolution_time_hrs"] > 12))
            | ((~tickets["status"].eq("Resolved")) & (tickets["age_hours"] > 12))
        )
        rows = tickets.loc[
            mask,
            ["ticket_id", "created_at", "status", "priority", "age_hours", "resolution_time_hrs", "agent_id"],
        ].copy()
        rows["created_at"] = rows["created_at"].astype(str)
        rows = rows.to_dict("records")
        answer = f"There are {len(rows)} Critical tickets not resolved within 12 hours."
        assumptions.append("Unresolved tickets are checked using age_hours at the as-of timestamp.")

    elif plan.intent == "avg_rating_by_category":
        category = plan.category or "Technical"
        filtered = tickets[(tickets["category"].eq(category)) & (tickets["customer_rating"].notna())]
        average = round(float(filtered["customer_rating"].mean()), 3) if not filtered.empty else None
        rows = [{"category": category, "average_customer_rating": average, "n": int(len(filtered))}]
        answer = (
            f"The average customer rating for {category} tickets is {average} from n={len(filtered)} rated tickets."
            if average is not None
            else f"There are no rated {category} tickets."
        )
        assumptions.append("Average rating uses rated tickets only.")

    elif plan.intent == "anomaly_resolution_this_week":
        week_start = as_of - pd.to_timedelta(as_of.weekday(), unit="D")
        week_end = week_start + pd.Timedelta(days=7)
        week = tickets[(tickets["created_at"] >= week_start) & (tickets["created_at"] < week_end)]
        resolved = week[week["status"].eq("Resolved")]
        q1 = resolved.groupby("priority")["resolution_time_hrs"].quantile(0.25)
        q3 = resolved.groupby("priority")["resolution_time_hrs"].quantile(0.75)
        iqr = q3 - q1
        fences = (q3 + 1.5 * iqr).to_dict()
        flagged = resolved[resolved.apply(lambda row: row["resolution_time_hrs"] > fences.get(row["priority"], float("inf")), axis=1)]
        rows = flagged[["ticket_id", "priority", "resolution_time_hrs", "agent_id"]].to_dict("records")
        answer = f"There are {len(rows)} resolution-time anomalies this week."
        assumptions.append("This week is the Monday-Sunday week containing the as-of timestamp.")

    else:
        rows = []
        answer = "I can only answer questions about the provided support-ticket dataset."

    return QueryResult(
        answer=answer,
        intent=plan.intent,
        rows=rows,
        row_count=len(rows),
        assumptions=assumptions,
        warnings=[],
        as_of=str(as_of),
        model=model,
    )
