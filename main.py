"""Entry point for the Ezcala MVP API.

This FastAPI application exposes a handful of endpoints to demonstrate the
cash‑intelligence workflow:

* `/sync` – load invoices and payments (simulating NetSuite API calls【747782438211344†L280-L297】).
* `/match` – reconcile payments with invoices.
* `/score` – compute customer risk scores.
* `/insights` – generate a narrative summary.
* `/dashboard` – render a simple HTML dashboard summarising the data.

To run locally:

```
uvicorn main:app --reload
```
Then open `http://localhost:8000/dashboard` in your browser.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from modules import sync_agent, matching_agent, scoring_agent, insights_agent
from modules.data_cache import data_cache

app = FastAPI(title="Ezcala MVP API")
templates = Jinja2Templates(directory="templates")


@app.post("/sync")
async def sync_endpoint():
    """Synchronise invoices and payments into the cache."""
    data = sync_agent.sync()
    return JSONResponse(content=data)


@app.post("/match")
async def match_endpoint():
    """Reconcile payments with invoices."""
    matches = matching_agent.reconcile()
    return JSONResponse(content={"matches": matches})


@app.post("/score")
async def score_endpoint():
    """Compute customer risk scores."""
    scores = scoring_agent.compute_scores()
    return JSONResponse(content={"scores": scores})


@app.post("/insights")
async def insights_endpoint():
    """Generate a narrative summary of the cash‑flow status."""
    text = insights_agent.generate_insights()
    return JSONResponse(content={"insights": text})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the HTML dashboard summarising invoices, payments, matches, scores and insights."""
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "invoices": data_cache.invoices,
            "payments": data_cache.payments,
            "matches": data_cache.matches,
            "scores": data_cache.scores,
            "insights": data_cache.insights,
        },
    )