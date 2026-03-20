import json
from engine.scorer import score_customer
from engine.router import route_customer

# Load your generated customers
with open("data/customers.json") as f:
    customers = json.load(f)

# Score everyone
scored = [score_customer(c) for c in customers]

# Sort by score, highest first
scored.sort(key=lambda x: x["total_score"], reverse=True)

# Print top 10
print("TOP 10 PRIORITY CUSTOMERS")
print("-" * 60)
for c in scored[:10]:
    print(f"{c['customer_id']} | Score: {c['total_score']:5.1f} | "
          f"Priority: {c['priority']:8s} | "
          f"Logins: {c['login_count_since_kyc']:2d} | "
          f"Deposit page: {c['visited_deposit_page']}")
    print(f"  Breakdown: {c['scores']}")
    print()

# After scoring
routed = [route_customer(s) for s in scored]

# Print top 10 with actions
for c in routed[:10]:
    print(f"{c['customer_id']} | Score: {c['total_score']:5.1f} | "
          f"Action: {c['recommended_action']}")
    print(f"  Reason: {c['action_reason']}")
    print()