"""In-memory ticket repository."""

import pandas as pd


class TicketRepository:
    """Small repository wrapper around a prepared pandas DataFrame."""

    def __init__(self, tickets: pd.DataFrame):
        self._tickets = tickets

    @property
    def tickets(self) -> pd.DataFrame:
        """Return a defensive copy of ticket data."""

        return self._tickets.copy()

    @property
    def row_count(self) -> int:
        """Return loaded ticket count."""

        return int(len(self._tickets))
