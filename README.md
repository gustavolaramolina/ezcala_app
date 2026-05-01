# Ezcala MVP — Cash Intelligence Proof of Concept

This repository contains a **minimal proof‑of‑concept (MVP)** for the Ezcala cash‑intelligence SaaS described by the user.  It is not a production‑ready system, but it demonstrates how the pieces of the architecture can work together to ingest data from an ERP, perform payment/invoice matching, compute customer risk scores, surface insights, and display the results in a simple web dashboard.

## Contents

* `main.py` – FastAPI application exposing endpoints for synchronization, matching, scoring, and insight generation.  It also serves a simple HTML dashboard using Jinja2.
* `modules/` – A set of Python modules implementing the core “agents” described in the architecture: `sync_agent.py`, `matching_agent.py`, `scoring_agent.py`, and `insights_agent.py`.
* `data/` – Contains sample invoice and payment data in JSON format.  These files simulate NetSuite’s invoices and payments endpoints (NetSuite exposes endpoints such as `GET /invoice` and `GET /payment` to retrieve invoices and payments【747782438211344†L280-L297】).
* `templates/` – A basic Jinja2 template used to render the dashboard.
* `requirements.txt` – Lists the Python packages required to run this MVP (FastAPI, Uvicorn, Jinja2 and Pandas).

## Getting Started

> **Note**
> This code is provided as a minimal demonstration.  It uses in‑memory data and simple algorithms; it omits authentication, authorization, secure secrets management, and production‑grade error handling.  Those concerns are critical for any real deployment.

1. **Install dependencies.**  From the root of the repository run:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the API server.**  Start the FastAPI app with Uvicorn:

   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`.  Navigate to `/dashboard` in your browser to see the HTML dashboard.

3. **Explore the API.**  FastAPI automatically generates interactive docs at `http://localhost:8000/docs`.  You can call:

   * `POST /sync` – Simulates fetching invoices and payments from NetSuite and caches them.
   * `POST /match` – Runs a deterministic matching algorithm to reconcile payments with invoices.
   * `POST /score` – Computes customer risk scores based on outstanding amounts and payment behaviour.
   * `POST /insights` – Generates a textual summary of the cash‑flow situation and prioritised customers.

4. **View the dashboard.**  Open `http://localhost:8000/dashboard` to view the aggregated results.  It shows each customer’s invoices and payments, the match status, risk score, and a short insight message.

## How it Works

### Data ingestion (`sync_agent.py`)

In a real solution, this agent would call NetSuite’s SuiteTalk REST endpoints (for example `GET /invoice` and `GET /payment`【747782438211344†L280-L297】) to retrieve invoices and payments.  Here we simulate that by reading the sample JSON files in `data/`.  The invoices and payments are stored in a shared in‑memory cache (a simple Python dictionary) accessible to other agents.

### Matching (`matching_agent.py`)

The matching agent reconciles payments with invoices.  It starts by attempting exact matches on invoice number and amount.  Any unmatched amount is applied to multiple invoices in order of due date.  A confidence score is produced for each match (1.0 for exact match, lower for partial matches).  Matches requiring human review could be added to an exception list for manual approval.

### Scoring (`scoring_agent.py`)

The scoring agent computes a simple risk score for each customer based on days overdue and outstanding amounts.  In a production system you would replace this with a machine‑learning model trained on historical payment behaviour.

### Insight generation (`insights_agent.py`)

The insights agent synthesizes a human‑readable summary of the current cash‑flow situation.  It analyses which customers contribute the most to outstanding balances and highlights potential delays or risks.  In a future version this module could call a language model API like OpenAI to produce more sophisticated narratives.

### Dashboard

The `/dashboard` endpoint renders an HTML page using Jinja2.  It lists customers, invoices, matched payments, scores, and insights.  This is intentionally basic; a real MVP could use React or Next.js and integrate with authentication and notification services.

## Future Enhancements

This POC intentionally omits many features required for a production SaaS.  A real MVP should add:

* **Robust NetSuite integration** using token‑based authentication, handling pagination, rate limiting and incremental syncs.
* **Persistent storage** (PostgreSQL) instead of in‑memory dictionaries.
* **User management and RBAC** for multi‑tenant operation.
* **Approval workflows** for match exceptions and write‑backs to NetSuite.
* **Notification services** using providers like SendGrid or Twilio for emails and WhatsApp messages.
* **Machine‑learning models** for scoring and predictive analytics.
