"""Shared schema and glossary for prompts, API, and documentation."""

COLUMN_DESCRIPTIONS = {
    "ticket_id": "Unique ticket identifier.",
    "created_at": "Ticket creation timestamp.",
    "category": "Billing, Technical, or General.",
    "priority": "Low, Medium, High, or Critical.",
    "status": "Open, Resolved, or Escalated.",
    "response_time_hrs": "Hours from creation to first agent response.",
    "resolution_time_hrs": "Hours from creation to resolution; null if unresolved.",
    "agent_id": "Assigned support agent identifier.",
    "customer_rating": "Post-resolution rating from 1 to 5; null if unresolved.",
    "issue_summary": "Short issue description.",
}

GLOSSARY = {
    "open": "status = Open. Escalated tickets are excluded.",
    "unresolved": "status is Open or Escalated.",
    "not resolved within N hours": "Resolved tickets over N hours plus unresolved tickets older than N hours.",
    "this month": "Calendar month containing the as-of timestamp, using created_at because no resolved_at column exists.",
    "this week": "Monday-Sunday week containing the as-of timestamp.",
}
