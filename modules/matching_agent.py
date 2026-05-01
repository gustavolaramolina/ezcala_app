"""Matching agent.

This module performs deterministic reconciliation between payments and invoices.  It
implements a simple matching algorithm:

1. Exact reference match: if a payment’s `reference` field matches an invoice
   ID and the invoice has an outstanding balance, the payment amount is applied
   to that invoice.  The match is given a confidence score of 1.0.
2. Overflow matching: if a payment exceeds the referenced invoice, or the
   payment has no reference, the remaining amount is applied to the customer’s
   oldest unpaid invoices by due date.  These matches receive a lower
   confidence score (0.8) because they rely on heuristics rather than an
   explicit reference.
3. Unmatched remainder: if there is leftover payment after all invoices are
   paid, it is left unallocated and could be posted as an unapplied payment.

Each match record includes the payment ID, the invoice ID, the amount
applied and a confidence score.  All matches are stored in the shared cache.
"""

from datetime import datetime
from typing import List, Dict

from .data_cache import data_cache


def _parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


def reconcile() -> List[Dict[str, float]]:
    """Perform reconciliation of payments against invoices.

    Returns a list of match records.  Updates the invoices’ balances and
    stores the matches in the data cache.
    """
    matches: List[Dict[str, float]] = []

    # Build lookups for invoices by invoice_id and by customer_id (ordered by due date)
    invoices_by_id = {inv["invoice_id"]: inv for inv in data_cache.invoices}
    invoices_by_customer = {}
    for inv in data_cache.invoices:
        invoices_by_customer.setdefault(inv["customer_id"], []).append(inv)

    # Sort each customer's invoices by due_date ascending
    for inv_list in invoices_by_customer.values():
        inv_list.sort(key=lambda i: _parse_date(i["due_date"]))

    # Process payments one by one
    for pmt in data_cache.payments:
        remaining = pmt["amount"]
        cust_id = pmt["customer_id"]

        # Try exact match if reference provided
        ref = pmt.get("reference") or ""
        if ref and ref in invoices_by_id:
            inv = invoices_by_id[ref]
            applied = min(inv["balance"], remaining)
            if applied > 0:
                inv["balance"] -= applied
                remaining -= applied
                matches.append({
                    "payment_id": pmt["payment_id"],
                    "invoice_id": inv["invoice_id"],
                    "amount_applied": applied,
                    "confidence": 1.0,
                })

        # If payment still has remainder, apply to oldest invoices for this customer
        if remaining > 0 and cust_id in invoices_by_customer:
            for inv in invoices_by_customer[cust_id]:
                if remaining <= 0:
                    break
                if inv["balance"] <= 0:
                    continue
                applied = min(inv["balance"], remaining)
                if applied > 0:
                    inv["balance"] -= applied
                    remaining -= applied
                    matches.append({
                        "payment_id": pmt["payment_id"],
                        "invoice_id": inv["invoice_id"],
                        "amount_applied": applied,
                        "confidence": 0.8 if ref else 0.8,
                    })

        # Leftover payment can be recorded as unapplied (not added to matches)

    data_cache.matches = matches
    return matches