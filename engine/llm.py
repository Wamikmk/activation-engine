from datetime import datetime
import os
import json
import requests


def build_customer_context(routed_customer: dict) -> dict:
    """Extract only the fields the LLM needs to write a good email.
    
    Principle: include what changes the email, strip system internals.
    """
    kyc_date = datetime.fromisoformat(routed_customer["kyc_completed_at"])
    days_since = (datetime.now() - kyc_date).days
    
    return {
        "first_name": routed_customer["full_name"].split()[0],
        "days_since_signup": days_since,
        "account_type": routed_customer["account_type"],
        "trading_experience": routed_customer["trading_experience"],
        "preferred_markets": routed_customer["preferred_markets"],
        "visited_deposit_page": routed_customer["visited_deposit_page"],
        "login_count": routed_customer["login_count_since_kyc"],
        "recommended_action": routed_customer["recommended_action"],
        "action_reason": routed_customer["action_reason"]
    }


def generate_email_template(context: dict) -> dict:
    """Rule-based email generator. Works without LLM API.
    
    Returns a usable email even when API credits aren't available.
    The LLM version will replace this with personalized content.
    """
    name = context["first_name"]
    markets = ", ".join(context["preferred_markets"])
    action = context["recommended_action"]
    
    templates = {
        "personalized_nudge_email": {
            "subject": f"{name}, your trading account is ready",
            "body": (
                f"Hi {name},\n\n"
                f"You signed up {context['days_since_signup']} days ago "
                f"and we noticed you haven't made your first deposit yet.\n\n"
                f"You showed interest in {markets} — great choices. "
                f"Making your first deposit takes under 2 minutes and "
                f"you'll get immediate access to live markets.\n\n"
                f"Ready to start?\n\n"
                f"Best,\nThe Trading Team"
            )
        },
        "demo_upgrade_email": {
            "subject": f"{name}, ready to trade with real money?",
            "body": (
                f"Hi {name},\n\n"
                f"We noticed you've been exploring the platform "
                f"on your demo account"
                f"{' and even checked out the deposit page' if context['visited_deposit_page'] else ''}.\n\n"
                f"Upgrading to a live account gives you access to "
                f"real {markets} markets with real returns.\n\n"
                f"Switch to live today.\n\n"
                f"Best,\nThe Trading Team"
            )
        },
        "automated_welcome_email": {
            "subject": f"Welcome to the platform, {name}",
            "body": (
                f"Hi {name},\n\n"
                f"Thanks for joining. Your account is verified "
                f"and ready to go.\n\n"
                f"Here's how to get started:\n"
                f"1. Explore {markets} markets\n"
                f"2. Make your first deposit\n"
                f"3. Place your first trade\n\n"
                f"Questions? We're here to help.\n\n"
                f"Best,\nThe Trading Team"
            )
        }
    }
    
    # Default for actions that don't need emails
    default = {
        "subject": f"Your trading account update, {name}",
        "body": (
            f"Hi {name},\n\n"
            f"Just checking in on your account. "
            f"We'd love to help you get started.\n\n"
            f"Best,\nThe Trading Team"
        )
    }
    
    email = templates.get(action, default)
    
    return {
        "subject": email["subject"],
        "body": email["body"],
        "generated_by": "template",
        "customer_context": context
    }




def generate_email_with_llm(context: dict) -> dict:
    """Generate a personalized email using Claude API.
    
    Sends customer context to Claude and gets back
    a tailored email with subject and body.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        # No API key available, fall back to template
        return None
    
    prompt = f"""You are an email copywriter for a trading platform. 
Write a short, personalized email for this customer.

Customer context:
- Name: {context['first_name']}
- Signed up {context['days_since_signup']} days ago
- Account type: {context['account_type']}
- Trading experience: {context['trading_experience']}
- Interested in: {', '.join(context['preferred_markets'])}
- Visited deposit page: {context['visited_deposit_page']}
- Login count: {context['login_count']}
- Recommended action: {context['recommended_action']}
- Reason: {context['action_reason']}

Rules:
- Match tone to their experience level (beginner = simple and encouraging, advanced = direct and market-focused)
- Reference their specific market interests
- If they visited the deposit page, acknowledge they were close
- Keep it under 100 words
- No fake urgency or pushy sales tactics

Respond ONLY with JSON in this exact format, no other text:
{{"subject": "email subject line", "body": "email body text"}}"""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 300,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=10
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Extract text from Claude's response
        text = data["content"][0]["text"]
        
        # Clean and parse JSON
        text = text.strip().replace("```json", "").replace("```", "").strip()
        email = json.loads(text)
        
        return {
            "subject": email["subject"],
            "body": email["body"],
            "generated_by": "llm"
        }
    
    except Exception as e:
        print(f"LLM generation failed: {e}")
        return None

def generate_email(routed_customer: dict, use_llm: bool = False) -> dict:
    """Generate an email for a routed customer.
    
    Args:
        routed_customer: Output from route_customer()
        use_llm: If True, attempt Claude API. Falls back to template.
    
    Returns:
        Email dict with subject, body, and metadata.
    """
    context = build_customer_context(routed_customer)
    
    if use_llm:
        llm_result = generate_email_with_llm(context)
        if llm_result:
            llm_result["customer_context"] = context
            return llm_result
    
    # Fallback to template
    return generate_email_template(context)


