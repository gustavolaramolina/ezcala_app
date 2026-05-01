"""Insights agent.

This module generates a human‑readable summary of the cash‑flow situation.
Instead of a language‑model call, it uses simple string formatting to
illustrate the type of insight a future LLM might produce.  It analyses the
customer risk scores and outstanding balances to prioritise collection actions.
"""

from typing import List

from .data_cache import data_cache


def generate_insights() -> str:
    """Generate a narrative summary of the current cash‑flow state.

    :return: A text insight.
    """
    if not data_cache.scores:
        return "No scores computed yet.  Run the scoring agent first."

    # Build list of customers sorted by risk score descending
    sorted_customers = sorted(
        data_cache.scores.items(), key=lambda item: item[1], reverse=True
    )

    lines: List[str] = []
    lines.append("Cash flow summary:")
    for cust_id, score in sorted_customers:
        # Find total outstanding for this customer
        total_outstanding = sum(
            inv.get("balance", 0.0)
            for inv in data_cache.invoices
            if inv["customer_id"] == cust_id
        )
        lines.append(
            f" • Customer {cust_id} has an outstanding balance of ${total_outstanding:,.2f} with a risk score of {score}."
        )
    # Suggest prioritisation
    if sorted_customers:
        highest_risk = sorted_customers[0][0]
        lines.append(
            f"Recommend prioritising collection efforts for {highest_risk} first."
        )
    insight_text = "\n".join(lines)
    data_cache.insights = insight_text
    return insight_text