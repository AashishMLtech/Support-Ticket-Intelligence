"""FastAPI dependencies."""

from fastapi import Request

from app.services.anomaly_service import AnomalyService
from app.services.health_service import HealthService
from app.services.query_service import QueryService


def get_health_service(request: Request) -> HealthService:
    return HealthService(request.app.state.app_state)


def get_query_service(request: Request) -> QueryService:
    return QueryService(request.app.state.app_state)


def get_anomaly_service(request: Request) -> AnomalyService:
    return AnomalyService(request.app.state.app_state)
