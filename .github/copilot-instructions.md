# Copilot Instructions — Ezcala MVP

## Product Context

Ezcala is a SaaS Cash Intelligence platform for finance teams. The MVP integrates with NetSuite to extract invoices, payments, customers and accounts receivable data, then processes it to generate payment matching, reconciliation, customer scoring and AI-generated cash flow insights.

The system must remain realistic, auditable and enterprise-ready. Do not overuse AI where deterministic financial logic is safer.

## Architecture Principles

Use a modular agent-based architecture:

- Sync Agent: extracts data from NetSuite or mock JSON files.
- Normalization Agent: cleans and maps raw ERP data into a canonical model.
- Matching Agent: reconciles payments and invoices.
- Scoring Agent: calculates customer risk and collection priority.
- Insights Agent: generates cash-flow summaries and recommended actions.
- Notification Agent: sends email or WhatsApp alerts.
- Approval Agent: manages human validation before write-back to ERP.

Prefer simple, testable modules over unnecessary microservices during MVP phase.

## Core Rule

Do not use LLMs for final financial reconciliation decisions.

Use:

- Deterministic logic for invoice/payment matching.
- Confidence scores for uncertain matches.
- Human approval for low-confidence or ambiguous cases.
- LLMs only for explanation, summarization and recommended next actions.

## Preferred Stack

Backend:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Celery or Temporal for async jobs
- Redis for queues/cache

Frontend:

- React or Next.js
- Simple dashboard first
- Clear tables and approval workflows

AI:

- OpenAI or Azure OpenAI
- Structured outputs
- Guardrails
- No hallucinated financial claims

Cloud:

- Azure preferred
- Azure App Service or Container Apps
- Azure PostgreSQL
- Azure Key Vault
- Application Insights

## Coding Guidelines

Write clean, production-oriented Python.

Use:

- Type hints
- Pydantic models
- Clear domain names
- Small functions
- Explicit error handling
- Docstrings for business logic
- Unit-testable services

Avoid:

- Hardcoded credentials
- Financial calculations hidden inside UI code
- LLM calls without source data
- Unvalidated ERP write-backs
- Mixing sync, matching, scoring and insights in one file
- MongoDB for core financial reconciliation data

## Data Model Guidelines

Create canonical models for:

- Customer
- Invoice
- Payment
- MatchResult
- CustomerScore
- Insight
- AuditEvent
- Tenant

Each financial object should include:

- tenant_id
- source_system
- external_id
- created_at
- updated_at
- sync_status
- raw_payload reference when applicable

## Matching Logic

Implement matching in layers:

1. Exact match:
   - invoice number
   - customer ID
   - exact amount
   - payment reference

2. Partial match:
   - one payment to one invoice
   - one payment to many invoices
   - many payments to one invoice

3. Fuzzy match:
   - similar reference
   - date proximity
   - amount tolerance
   - customer payment behavior

4. Exception queue:
   - low confidence
   - conflicting matches
   - missing references
   - overpayments
   - unapplied payments

Every match must return:

- payment_id
- invoice_id or invoice_ids
- amount_applied
- confidence_score
- match_type
- explanation
- requires_approval

## Scoring Logic

Customer scoring should consider:

- outstanding AR balance
- days overdue
- average payment delay
- invoice aging
- partial payment frequency
- dispute frequency
- payment consistency
- historical payment behavior

Return explainable reason codes, for example:

- HIGH_OVERDUE_BALANCE
- FREQUENT_LATE_PAYMENT
- LARGE_UNPAID_INVOICE
- IMPROVING_PAYMENT_TREND
- LOW_RISK_CUSTOMER

## AI Insights Guidelines

AI-generated insights must be grounded in actual system data.

Insights should answer:

- Which customers are putting cash flow at risk?
- Which invoices should be prioritized?
- What payments look suspicious or unmatched?
- What collection actions are recommended?
- What changed since the previous sync?

Use structured prompts and return JSON when possible.

Example output:

```json
{
  "summary": "Customer CUST-001 has a high outstanding balance and should be prioritized.",
  "risk_level": "HIGH",
  "recommended_action": "Contact customer before Friday and confirm payment date.",
  "supporting_data": [
    "Outstanding balance: 15000",
    "Days overdue: 28",
    "Last payment: partial"
  ]
}
```

Do not allow the AI to invent balances, dates, customer names or payment status.

## NetSuite Integration Guidelines

Design the NetSuite connector behind an interface.

Start with mock JSON data, but prepare for real NetSuite integration.

Required capabilities:

* fetch invoices
* fetch payments
* fetch customers
* incremental sync
* pagination
* retry policy
* idempotency
* rate limit handling
* token-based authentication
* secrets stored outside code

Never expose NetSuite credentials in logs.

## API Design

Use REST endpoints such as:

* POST `/sync`
* GET `/invoices`
* GET `/payments`
* POST `/matching/run`
* GET `/matching/results`
* POST `/matching/{id}/approve`
* POST `/matching/{id}/reject`
* POST `/scoring/run`
* GET `/customers/{id}/score`
* POST `/insights/generate`
* GET `/dashboard/summary`

Return consistent JSON responses.

Use HTTP status codes properly.

## Security Requirements

Always consider this a financial SaaS.

Include:

* tenant isolation
* RBAC
* audit logs
* secret management
* encryption in transit
* encryption at rest
* safe error messages
* no PII leakage to logs
* no ERP write-back without approval

## Auditability

Every important action must generate an audit event:

* sync started
* sync completed
* invoice imported
* payment imported
* match generated
* match approved
* match rejected
* score generated
* insight generated
* ERP write-back attempted
* ERP write-back completed
* ERP write-back failed

Audit events should include:

* tenant_id
* actor
* action
* entity_type
* entity_id
* timestamp
* previous_value
* new_value
* source

## MVP Priorities

Build in this order:

1. Stable data model
2. Mock NetSuite sync
3. Matching engine
4. Match result dashboard
5. Customer scoring
6. Insight generation
7. Approval workflow
8. Email notification
9. Real NetSuite connector
10. ERP write-back

Do not build complex AI agent orchestration before the financial core is stable.

## Testing Guidelines

Add tests for:

* exact matching
* partial matching
* overpayment handling
* unmatched payments
* customer scoring
* insight generation with grounded data
* API responses
* audit event creation

Use small fixture files for invoices and payments.

## Definition of Done

A feature is not done unless:

* It has clear business purpose.
* It works with sample data.
* It has error handling.
* It is testable.
* It does not break auditability.
* It does not rely on hallucinated AI output.
* It keeps financial decisions explainable.


