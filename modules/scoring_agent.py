"""Customer risk scoring agent.

This module computes a simple collection priority / risk score for each
customer.  It illustrates how a deterministic formula can be used as a
placeholder for a machine‑learning model.  The score incorporates:

* Total outstanding balance – larger unpaid balances increase risk.
* Days overdue – invoices past their due date contribute to higher risk.
* Payment history could also be incorporated (not shown here).

The result is a dictionary mapping `customer_id` to a numeric score between 0
and 100, where higher scores indicate higher priority for collection.
"""

from datetime import datetime
from typing import Dict

from .data_cache import data_cache


def _parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


def compute_scores(today: datetime | None = None) -> Dict[str, float]:
    """Compute risk scores for each customer.

    :param today: Optional reference date.  Defaults to the current date.
    :return: Mapping of customer_id to risk score.
    """
    if today is None:
        today = datetime.today()

    scores: Dict[str, float] = {}
    totals: Dict[str, float] = {}
    overdue_days: Dict[str, float] = {}

    # Aggregate outstanding amounts and overdue days by customer
    for inv in data_cache.invoices:
        cust = inv["customer_id"]
        balance = inv.get("balance", 0.0)
        totals[cust] = totals.get(cust, 0.0) + balance
        days_overdue = (today - _parse_date(inv["due_date"])).days
        if days_overdue > 0:
            overdue_days[cust] = overdue_days.get(cust, 0.0) + days_overdue

    # Compute score: simple formula to prioritise high balances and overdue days
    for cust, total in totals.items():
        overdue = overdue_days.get(cust, 0.0)
        # Weighted combination; adjust coefficients as needed
        # Decrease score with greater overdue days and outstanding amount
        raw_score = 100 - (overdue * 0.5) - (total / 100.0)
        # Clamp between 0 and 100
        score = max(0.0, min(100.0, raw_score))
        scores[cust] = round(score, 2)

    data_cache.scores = scores
    return scores