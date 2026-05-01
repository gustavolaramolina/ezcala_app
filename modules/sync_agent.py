"""Synchronisation agent.

This module simulates pulling invoice and payment data from NetSuite.
In a real integration this would connect to NetSuite’s SuiteTalk REST API and
retrieve invoices, payments, customers, etc.  For example, NetSuite exposes
endpoints like `GET /invoice` and `GET /payment`【747782438211344†L280-L297】.  The
function below reads sample data from the `data/` directory instead and stores
them in a shared cache.
"""

import json
from pathlib import Path
from typing import List, Dict

from .data_cache import data_cache


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def sync() -> Dict[str, List[Dict]]:
    """Load invoices and payments from local JSON files into the cache.

    Returns a dictionary with lists of invoices and payments.  Subsequent
    calls overwrite the previous cache contents.
    """
    # Reset existing data
    data_cache.reset()

    # Read invoices
    invoices_path = DATA_DIR / "invoices.json"
    with invoices_path.open("r", encoding="utf-8") as f:
        data_cache.invoices = json.load(f)

    # Read payments
    payments_path = DATA_DIR / "payments.json"
    with payments_path.open("r", encoding="utf-8") as f:
        data_cache.payments = json.load(f)

    return {
        "invoices": data_cache.invoices,
        "payments": data_cache.payments,
    }