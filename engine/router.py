from datetime import datetime


# Thresholds — pulled out as constants so they're easy to tune
ESCALATION_LOGIN_THRESHOLD = 15
ESCALATION_SCORE_THRESHOLD = 70
SALES_CALL_ENGAGEMENT_THRESHOLD = 18.0
SALES_CALL_INTENT_THRESHOLD = 15.0
HIGH_RECENCY_THRESHOLD = 20.0


def route_customer(scored_customer: dict) -> dict:
    """Decide what action to take for a scored customer.
    
    Looks at score breakdown, not just total, to match
    the action to the customer's specific situation.
    
    Returns the scored customer enriched with:
    - action: what to do
    - reason: why this action was chosen
    - urgency: how quickly to act
    """
    scores = scored_customer["scores"]
    total = scored_customer["total_score"]
    priority = scored_customer["priority"]
    account_type = scored_customer["account_type"]
    visited_deposit = scored_customer["visited_deposit_page"]
    
    # Already converted — no action needed
    if priority == "converted":
        return _build_result(
            scored_customer,
            action="none",
            reason="Customer has already deposited",
            urgency="none"
        )
    
    # Rule 4 first — Escalate (wins over everything)
    # Something is likely blocking them, not motivational
    if (total >= ESCALATION_SCORE_THRESHOLD
            and scores["engagement"] >= SALES_CALL_ENGAGEMENT_THRESHOLD
            and visited_deposit
            and scored_customer["login_count_since_kyc"] 
                >= ESCALATION_LOGIN_THRESHOLD):
        return _build_result(
            scored_customer,
            action="escalate_to_manager",
            reason="High engagement and intent but no deposit — "
                   "possible operational blocker",
            urgency="immediate"
        )
    
    # Rule 1 — Sales call
    # Warm lead with strong engagement + intent
    if (scores["engagement"] >= SALES_CALL_ENGAGEMENT_THRESHOLD
            and scores["intent"] >= SALES_CALL_INTENT_THRESHOLD):
        return _build_result(
            scored_customer,
            action="sales_call",
            reason="High engagement and intent — "
                   "personal outreach can close",
            urgency="same_day"
        )
    
    # Rule 3 — Demo upgrade email
    # Demo user showing real-money curiosity
    if account_type == "demo" and visited_deposit:
        return _build_result(
            scored_customer,
            action="demo_upgrade_email",
            reason="Demo user visited deposit page — "
                   "interested in going live",
            urgency="within_24h"
        )
    
    # Rule 2 — Personalized nudge email
    # New user who hasn't explored yet
    if scores["recency"] >= HIGH_RECENCY_THRESHOLD:
        return _build_result(
            scored_customer,
            action="personalized_nudge_email",
            reason="Recent signup with room for engagement — "
                   "guide toward first deposit",
            urgency="within_24h"
        )
    
    # Rule 5 — Medium score, some signals
    if priority in ("medium", "high"):
        return _build_result(
            scored_customer,
            action="automated_welcome_email",
            reason="Moderate interest — standard nurture flow",
            urgency="within_48h"
        )
    
    # Default — Low priority, nurture queue
    return _build_result(
        scored_customer,
        action="nurture_queue",
        reason="Low engagement — add to drip campaign",
        urgency="low"
    )

def _build_result(scored_customer: dict, action: str, 
                  reason: str, urgency: str) -> dict:
    """Attach routing decision to the scored customer record."""
    return {
        **scored_customer,
        "recommended_action": action,
        "action_reason": reason,
        "urgency": urgency,
        "routed_at": datetime.now().isoformat()
    }