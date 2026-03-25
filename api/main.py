import json
from fastapi import FastAPI, HTTPException

from engine.scorer import score_customer
from engine.router import route_customer

app = FastAPI(
    title="Customer Activation Engine",
    description="Scores and routes unactivated customers for fintech platforms",
    version="1.0.0"
)

# --- Data loading and processing on startup ---

def load_and_process_customers():
    """Load customers, score them, route them. Runs once at startup."""
    with open("data/customers.json") as f:
        raw_customers = json.load(f)
    
    processed = []
    for customer in raw_customers:
        scored = score_customer(customer)
        routed = route_customer(scored)
        processed.append(routed)
    
    # Sort by score descending — highest priority first
    processed.sort(key=lambda x: x["total_score"], reverse=True)
    return processed


# Process once, store in memory
CUSTOMERS = load_and_process_customers()

# --- Endpoints ---

@app.get("/")
def root():
    """Health check — confirms the API is running."""
    return {
        "status": "running",
        "service": "Customer Activation Engine",
        "total_customers": len(CUSTOMERS)
    }


@app.get("/customers")
def get_customers(
    priority: str = None,
    action: str = None,
    limit: int = 50
):
    """Get all customers, optionally filtered by priority or action."""
    results = CUSTOMERS
    
    if priority:
        results = [c for c in results if c["priority"] == priority]
    
    if action:
        results = [c for c in results if c["recommended_action"] == action]
    
    return {
        "count": len(results[:limit]),
        "total_matching": len(results),
        "customers": results[:limit]
    }


@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    """Get a single customer's full scored and routed record."""
    for customer in CUSTOMERS:
        if customer["customer_id"] == customer_id:
            return customer
    
    raise HTTPException(
        status_code=404,
        detail=f"Customer {customer_id} not found"
    )


@app.get("/dashboard/summary")
def get_dashboard_summary():
    """Overview stats for the dashboard."""
    # Count by priority
    priority_counts = {}
    for c in CUSTOMERS:
        p = c["priority"]
        priority_counts[p] = priority_counts.get(p, 0) + 1
    
    # Count by action
    action_counts = {}
    for c in CUSTOMERS:
        a = c["recommended_action"]
        action_counts[a] = action_counts.get(a, 0) + 1
    
    # Top 5 most urgent
    non_converted = [c for c in CUSTOMERS if c["priority"] != "converted"]
    top_5 = non_converted[:5]
    
    return {
        "total_customers": len(CUSTOMERS),
        "priority_breakdown": priority_counts,
        "action_breakdown": action_counts,
        "top_urgent": [
            {
                "customer_id": c["customer_id"],
                "score": c["total_score"],
                "priority": c["priority"],
                "action": c["recommended_action"],
                "reason": c["action_reason"]
            }
            for c in top_5
        ]
    }


@app.post("/refresh")
def refresh_data():
    """Reload and reprocess all customer data."""
    global CUSTOMERS
    CUSTOMERS = load_and_process_customers()
    return {
        "status": "refreshed",
        "total_customers": len(CUSTOMERS)
    }