import math
from datetime import datetime


def score_recency(kyc_completed_at: str, max_points: float = 30.0,
                  decay_rate: float = 0.85) -> float:
    """Score based on days since KYC completion.
    
    Exponential decay — urgency drops fast in first week, flattens after.
    Day 1: ~25.5 | Day 7: ~10.2 | Day 14: ~3.5 | Day 30: ~0.3
    """
    kyc_date = datetime.fromisoformat(kyc_completed_at)
    days_since = max((datetime.now() - kyc_date).days, 0)
    
    score = max_points * (decay_rate ** days_since)
    return round(score, 2)


def score_engagement(login_count: int, max_points: float = 25.0) -> float:
    """Score based on login frequency since KYC.
    
    Logarithmic scaling — first few logins matter most,
    diminishing returns after. 5 logins ≈ 15pts, 20 logins ≈ 25pts.
    """
    if login_count <= 0:
        return 0.0
    
    score = max_points * (math.log(login_count + 1) / math.log(21))
    return round(min(score, max_points), 2)


def score_intent(visited_deposit_page: bool, account_type: str,
                 max_points: float = 20.0) -> float:
    """Score based on deposit page visit + account type combination.
    
    Visited + live = strongest signal (20pts)
    Visited + demo = curious but uncommitted (12pts)
    Not visited + live = has intent but hasn't explored (7pts)
    Not visited + demo = just browsing (0pts)
    """
    if visited_deposit_page and account_type == "live":
        return max_points          # 20 — best case
    elif visited_deposit_page and account_type == "demo":
        return max_points * 0.6    # 12 — showed action, wrong account type
    elif not visited_deposit_page and account_type == "live":
        return max_points * 0.35   # 7 — right account, no action yet
    else:
        return 0.0                 # demo + didn't visit = cold


def score_account_type(account_type: str, max_points: float = 15.0) -> float:
    """Score based on account type. Live signals real intent."""
    if account_type == "live":
        return max_points    # 15
    else:
        return 5.0           # demo still gets something — engaged demo users matter


def score_profile(trading_experience: str, preferred_markets: list,
                  max_points: float = 10.0) -> float:
    """Score based on experience level and market interest breadth.
    
    Advanced traders with specific market picks = clearest intent.
    """
    experience_scores = {
        "beginner": 1,
        "intermediate": 3,
        "advanced": 5
    }
    
    exp_score = experience_scores.get(trading_experience, 0)
    market_score = len(preferred_markets)
    
    return min(exp_score + market_score, max_points)


def score_customer(customer: dict) -> dict:
    """Calculate total priority score for a customer.
    
    Returns the original customer data enriched with:
    - Individual score breakdowns (so dashboard can show WHY)
    - Total priority score (0-100)
    - Priority tier label (critical/high/medium/low)
    """
    # Already converted — no need to activate
    if customer.get("has_deposited", False):
        return {
            **customer,
            "scores": {
                "recency": 0,
                "engagement": 0,
                "intent": 0,
                "account_type": 0,
                "profile": 0
            },
            "total_score": 0,
            "priority": "converted"
        }
    
    # Calculate each component
    scores = {
        "recency": score_recency(customer["kyc_completed_at"]),
        "engagement": score_engagement(customer["login_count_since_kyc"]),
        "intent": score_intent(
            customer["visited_deposit_page"],
            customer["account_type"]
        ),
        "account_type": score_account_type(customer["account_type"]),
        "profile": score_profile(
            customer["trading_experience"],
            customer["preferred_markets"]
        )
    }
    
    total = round(sum(scores.values()), 2)
    
    # Assign priority tier
    if total >= 70:
        priority = "critical"
    elif total >= 50:
        priority = "high"
    elif total >= 30:
        priority = "medium"
    else:
        priority = "low"
    
    return {
        **customer,
        "scores": scores,
        "total_score": total,
        "priority": priority
    }
