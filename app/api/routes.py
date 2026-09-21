"""API routes."""

from fastapi import APIRouter, Depends, Query

from app.api.schemas import QueryRequest
from app.semantic import COLUMN_DESCRIPTIONS, GLOSSARY
from app.services.anomaly_service import AnomalyService
from app.services.health_service import HealthService
from app.services.query_service import QueryService
from app.api.deps import get_anomaly_service, get_health_service, get_query_service

router = APIRouter()


@router.get("/health")
def health(service: HealthService = Depends(get_health_service)) -> dict:
    """Return health and data quality details."""

    return service.get_health()


@router.post("/query")
def query(payload: QueryRequest, service: QueryService = Depends(get_query_service)) -> dict:
    """Answer a natural-language question about support tickets."""

    return service.ask(payload.question)


@router.get("/anomalies")
def anomalies(
    rule: str | None = None,
    priority: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    service: AnomalyService = Depends(get_anomaly_service),
) -> dict:
    """Return deterministic anomaly flags."""

    return service.list_anomalies(rule=rule, priority=priority, limit=limit)


@router.get("/schema")
def schema() -> dict:
    """Return data dictionary and glossary."""

    return {"columns": COLUMN_DESCRIPTIONS, "glossary": GLOSSARY}
