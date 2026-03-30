# Customer Activation Engine

An AI-powered system that identifies, scores, and activates customers who complete KYC onboarding but never make their first deposit  the single biggest revenue leak in fintech platforms.

## The Problem

Every fintech platform faces the same brutal reality: **85-95% of users who complete identity verification never deposit a single dollar.**

At a fintech platform, which has (4M+ users, 180+ countries), this means millions of verified accounts sitting idle. The onboarding cost is already spent KYC verification, compliance checks, account setup — but the customer never generates revenue.

The industry response is usually one of two extremes:
- **Blast everyone with the same generic "Make your first deposit!" email.** Low effort, low conversion. A beginner interested in crypto gets the same message as an advanced forex trader who visited the deposit page 5 times.
- **Have sales reps manually review accounts.** High conversion but impossible to scale. A team of 10 can't meaningfully triage 50,000 idle accounts.

Neither approach answers the question that actually matters: **Who should we contact, in what order, saying what?**

## What This System Does

The Activation Engine automates that decision pipeline:

```
Customer completes KYC → Score by urgency → Decide action → Generate personalized outreach
```

**1. Priority Scoring (0-100)** : Five weighted factors using exponential decay and logarithmic scaling:
- Recency (30pts) : How recently they completed KYC. Exponential decay models the reality that urgency drops fast in week 1, then flattens.
- Engagement (25pts) : Login frequency. Logarithmic scaling captures diminishing returns — the jump from 1 to 5 logins matters more than 15 to 20.
- Intent (20pts) : Visited deposit page + account type combination. The strongest behavioral signal.
- Account Type (15pts) : Live vs demo. Live signals real-money intent.
- Profile (10pts) : Trading experience + market preferences. Weaker signal but adds targeting nuance.

**2. Action Routing** : The router examines score breakdowns, not just totals. Two customers scoring 65 can get completely different actions:
- A customer who scored 65 from high recency + low engagement → personalized nudge email (they're new, guide them)
- A customer who scored 65 from high engagement + low recency → sales call (they're interested but something is blocking them)

Routing rules, in priority order:
| Rule | Trigger | Action |
|------|---------|--------|
| Escalate | Score ≥70, 15+ logins, visited deposit page, no deposit | Manager review — likely operational blocker |
| Sales call | High engagement + high intent scores | Personal outreach to close |
| Demo upgrade | Demo account + visited deposit page | Email about switching to live |
| Personalized nudge | High recency score | Guide new users toward deposit |
| Welcome email | Medium/high priority | Standard nurture flow |
| Nurture queue | Low priority | Drip campaign |

**3. LLM-Powered Email Generation** — Claude API generates emails tailored to each customer's profile:
- Matches tone to experience level (beginner = simple, advanced = market-focused)
- References specific market interests
- Acknowledges behavioral signals ("you visited the deposit page")
- Falls back to rule-based templates when API is unavailable

**4. Real-Time Dashboard** : Sales managers see priority queues, score breakdowns, recommended actions, and can generate personalized emails with one click.

## Architecture

```
data/generate.py          → Generates 200 realistic correlated customer records
                              ↓
engine/scorer.py           → 5-factor weighted scoring (exponential decay, log scaling)
                              ↓
engine/router.py           → Maps score breakdowns to specific actions
                              ↓
engine/llm.py              → Claude API for personalized emails + template fallback
                              ↓
api/main.py                → FastAPI REST API (5 endpoints, startup caching)
                              ↓
dashboard/index.html       → Web dashboard (priority queue, detail view, email gen)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/customers` | List all scored/routed customers. Filter: `?priority=critical&limit=10` |
| GET | `/customers/{id}` | Single customer with full score breakdown and action |
| GET | `/customers/{id}/email` | Generate email. Add `?use_llm=true` for AI-powered version |
| GET | `/dashboard/summary` | Priority counts, action distribution, top urgent |
| GET | `/dashboard` | Web dashboard UI |
| POST | `/refresh` | Reload and reprocess all customer data |

## Setup

### Prerequisites
- Python 3.10+
- Anthropic API key (optional — system works without it using template emails)

### Installation

```bash
git clone https://github.com/Wamikmk/activation-engine.git
cd activation-engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Generate Data

```bash
python data/generate.py
```

### Run the API

```bash
# Without LLM features
uvicorn api.main:app --reload

# With LLM email generation
export ANTHROPIC_API_KEY="your-key-here"
uvicorn api.main:app --reload
```

Open `http://127.0.0.1:8000/dashboard` for the web dashboard.

## Design Decisions

**Why exponential decay for recency?**
Customer urgency doesn't drop linearly. A 2-day-old lead is much hotter than a 7-day-old one, but a 25-day-old lead is barely different from a 35-day-old one. Exponential decay (`score = max × 0.85^days`) models this natural curve.

**Why logarithmic scaling for engagement?**
The first few logins carry the most signal. Going from 0 to 3 logins tells you someone is interested. Going from 15 to 20 tells you almost nothing new. `log(n+1)/log(21)` captures these diminishing returns.

**Why does the router examine breakdowns, not just totals?**
Because the same total score can mean very different things. A brand-new user with no engagement needs a welcome guide. A highly engaged user who keeps coming back but won't deposit needs a sales call to remove a blocker. The total is the same, the action is not.

**Why template fallback for emails?**
LLM APIs fail. Credits run out. Networks go down. The system should always produce usable output. Templates guarantee baseline functionality; the LLM enhances it when available.

## Project Structure

```
activation-engine/
├── CLAUDE.md               ← Project context for Claude Code
├── README.md
├── requirements.txt
├── data/
│   ├── __init__.py
│   ├── generate.py         ← Fake customer data with realistic correlations
│   └── customers.json      ← Generated dataset (200 records)
├── engine/
│   ├── __init__.py
│   ├── scorer.py           ← 5-factor priority scoring
│   ├── router.py           ← Action decision engine
│   └── llm.py              ← LLM email generation + template fallback
├── api/
│   ├── __init__.py
│   └── main.py             ← FastAPI REST API
└── dashboard/
    └── index.html           ← Web dashboard
```

## What I Learned Building This

- **Data modeling**: Fields must be correlated, not random. A customer who visited the deposit page must have logged in at least twice — independent random generation produces unrealistic data.
- **Scoring systems**: Continuous weighted scoring preserves nuance that binary checklists lose. A score of 48 vs 35 should matter, and it does with the right design.
- **Decision routing**: Same score, different action. Looking at score breakdowns instead of totals enables genuinely different responses for different customer situations.
- **Graceful degradation**: The LLM layer enhances emails but the system works completely without it. Always design features that fail gracefully.
- **API design**: Cache at startup for small datasets, serve from memory, refresh on demand. Simple architecture that handles the current scale.

## Future Improvements

- Database backend (PostgreSQL) instead of JSON file
- Real-time event streaming (customer logs in → score updates immediately)
- A/B testing framework for email variants
- Webhook integrations (trigger CRM updates, Slack notifications)
- Authentication and role-based access for the dashboard
- Batch email sending with rate limiting

## Built With

- Python 3.10
- FastAPI
- Claude API (Anthropic) for LLM email generation
- Vanilla HTML/CSS/JS for the dashboard
