# Ezcala MVP — Cash Intelligence Proof of Concept

This repository contains a **minimal proof‑of‑concept (MVP)** for the Ezcala cash‑intelligence SaaS described by the user.  It is not a production‑ready system, but it demonstrates how the pieces of the architecture can work together to ingest data from an ERP, perform payment/invoice matching, compute customer risk scores, surface insights, and display the results in a simple web dashboard.

## Contents

* `streamlit_app.py` – Modern Streamlit dashboard with interactive visualizations, KPI metrics, and data analysis tools.
* `modules/` – A set of Python modules implementing the core "agents" described in the architecture: `sync_agent.py`, `matching_agent.py`, `scoring_agent.py`, and `insights_agent.py`.
* `data/` – Contains sample invoice and payment data in JSON format.  These files simulate NetSuite's invoices and payments endpoints.
* `.streamlit/config.toml` – Streamlit configuration for theme and appearance.
* `requirements.txt` – Lists the Python packages required to run this MVP (Streamlit, Plotly, and Pandas).

## Getting Started

> **Note**
> This code is provided as a minimal demonstration.  It uses in‑memory data and simple algorithms; it omits authentication, authorization, secure secrets management, and production‑grade error handling.  Those concerns are critical for any real deployment.

1. **Install dependencies.**  From the root of the repository run:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the dashboard:**

   ```bash
   streamlit run streamlit_app.py
   ```

   The dashboard will be available at `http://localhost:8501`.

3. **Use the dashboard:**

   * Click **"🔄 Sync Data"** in the sidebar to load invoices and payments from JSON files.
   * View **Key Metrics** including Total AR Outstanding, Unmatched Payments, Average Days Overdue, and Collection Effectiveness.
   * Navigate between tabs:
     - **📈 Overview** for interactive charts (AR aging, risk scores, match confidence, payment timeline)
     - **🧾 Invoices** for detailed invoice table with aging analysis
     - **💳 Payments** for payment details and statistics
     - **🔗 Matches** for payment-to-invoice matching results with confidence scores
     - **💡 Insights** for AI-generated cash flow analysis and customer risk priorities
   * Use **sidebar filters** to filter by customer, date range, and confidence threshold.

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

The Streamlit dashboard (`streamlit_app.py`) provides an interactive web interface with:

* **Real-time KPI metrics** showing Total AR Outstanding, Unmatched Payments, Average Days Overdue, and Collection Effectiveness
* **Interactive Plotly visualizations** including AR aging analysis, customer risk scores, match confidence distribution, and payment timelines
* **Filterable data tables** for invoices, payments, and matches with advanced column configuration
* **Tabbed navigation** organizing different views (Overview, Invoices, Payments, Matches, Insights)
* **Sidebar controls** for manual data sync, customer filtering, date range selection, and confidence threshold adjustment
* **Session state management** to persist data between interactions without unnecessary recomputation
* **Caching** using `@st.cache_data` for efficient data loading and processing

This is a production-ready UI framework that could be extended with authentication, role-based access control, and notification services.

## Future Enhancements

This POC intentionally omits many features required for a production SaaS.  A real MVP should add:

* **Robust NetSuite integration** using token‑based authentication, handling pagination, rate limiting and incremental syncs.
* **Persistent storage** (PostgreSQL) instead of in‑memory dictionaries.
* **User management and RBAC** for multi‑tenant operation.
* **Approval workflows** for match exceptions and write‑backs to NetSuite.
* **Notification services** using providers like SendGrid or Twilio for emails and WhatsApp messages.
* **Machine‑learning models** for scoring and predictive analytics.
