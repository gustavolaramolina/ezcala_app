"""Simple in-memory cache for invoices, payments, matches, scores and insights.

The goal of this cache is to share data between the different agents.  In a real
production system this would be replaced by persistent storage (e.g. PostgreSQL).
"""

from typing import Dict, List, Any


class DataCache:
    """A singleton‑style class to hold data across agents."""
    invoices: List[Dict[str, Any]] = []
    payments: List[Dict[str, Any]] = []
    matches: List[Dict[str, Any]] = []
    scores: Dict[str, float] = {}  # customer_id -> score
    insights: str = ""

    @classmethod
    def reset(cls) -> None:
        cls.invoices = []
        cls.payments = []
        cls.matches = []
        cls.scores = {}
        cls.insights = ""


data_cache = DataCache