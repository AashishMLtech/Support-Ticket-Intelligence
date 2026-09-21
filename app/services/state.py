"""Application state construction."""

from dataclasses import dataclass

import pandas as pd

from app.core.config import Settings
from app.core.time_context import resolve_as_of
from app.data.cleaning import clean_tickets
from app.data.derived import add_derived_columns
from app.data.loader import load_tickets
from app.data.quality import build_quality_report
from app.data.repository import TicketRepository
from app.llm.groq_client import GroqClient


@dataclass
class AppState:
    """Shared application state."""

    repository: TicketRepository
    quality_report: dict
    as_of: pd.Timestamp
    llm: GroqClient


def build_state(settings: Settings) -> AppState:
    """Load data and construct application state."""

    raw = clean_tickets(load_tickets(settings.data_path))
    as_of = resolve_as_of(raw["created_at"].max(), settings.as_of_date)
    prepared = add_derived_columns(raw, as_of)
    return AppState(
        repository=TicketRepository(prepared),
        quality_report=build_quality_report(prepared),
        as_of=as_of,
        llm=GroqClient(settings),
    )
