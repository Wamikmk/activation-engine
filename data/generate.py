import json
import random
from datetime import datetime, timedelta

# Configuration
NUM_CUSTOMERS = 200
DEPOSIT_RATE = 0.12  # 12% actually deposit

# Realistic value pools
COUNTRIES = ["GB", "DE", "AU", "AE", "PL", "IT", "ES", "CZ", "NL", "SE"]
DEVICES = ["mobile", "desktop", "tablet"]
ACCOUNT_TYPES = ["live", "demo"]
MARKETS = ["forex", "crypto", "stocks", "indices", "commodities"]
EMPLOYMENT_STATUSES = ["employed", "self_employed", "student", "retired", "unemployed"]
FUND_SOURCES = ["salary", "savings", "business_income", "investments", "inheritance"]
EXPERIENCE_LEVELS = ["beginner", "intermediate", "advanced"]
DEPOSIT_RANGES = ["0-100", "100-500", "500-1000", "1000-5000", "5000+"]


def generate_customer(customer_id):
  #registration date : random day in last 60 days

  days_ago = random.randint(1,60)
  registered_at = datetime.now() - timedelta(days = days_ago)

  kyc_delay_hours = random.randint(1,72)
  kyc_completed_at = registered_at + timedelta(hours = kyc_delay_hours)

  account_type = random.choices(["live", "demo"], weights = [70,30])[0]

  if account_type == "live":
    login_count = random.randint(1,20)
    visited_deposit = random.random() < 0.40
  else:
    login_count = random.randint(1,25)
    visited_deposit = random.random() < 0.10

  if visited_deposit and login_count < 2:
    login_count = random.randint(2,5)

  # Last login: between KYC completion and now
  if login_count > 0:
      days_since_kyc = (datetime.now() - kyc_completed_at).days
      last_login_offset = random.randint(0, max(days_since_kyc, 1))
      last_login_at = datetime.now() - timedelta(days=last_login_offset)
  else:
      last_login_at = kyc_completed_at
    
  # Has deposited? 12% rate, but only if conditions make sense
  if account_type == "live" and visited_deposit and login_count >= 3:
      has_deposited = random.random() < 0.30
  elif account_type == "live" and visited_deposit:
      has_deposited = random.random() < 0.10
  else:
      has_deposited = False

    # Build the customer record
  customer = {
        "customer_id": f"CUST-{customer_id:05d}",
        "full_name": generate_name(),
        "date_of_birth": generate_dob(),
        "email": f"user{customer_id}@example.com",
        "phone": f"+{random.randint(1,99)}-{random.randint(1000000000, 9999999999)}",
        "country": random.choice(COUNTRIES),
        
        "registered_at": registered_at.isoformat(),
        "kyc_completed_at": kyc_completed_at.isoformat(),
        "kyc_attempts": random.choices([1, 2, 3], weights=[70, 20, 10])[0],
        
        "device": random.choice(DEVICES),
        "account_type": account_type,
        "login_count_since_kyc": login_count,
        "visited_deposit_page": visited_deposit,
        "last_login_at": last_login_at.isoformat(),
        "preferred_markets": random.sample(MARKETS, k=random.randint(1, 3)),
        
        "employment_status": random.choice(EMPLOYMENT_STATUSES),
        "source_of_funds": random.choice(FUND_SOURCES),
        "trading_experience": random.choice(EXPERIENCE_LEVELS),
        "expected_deposit_range": random.choice(DEPOSIT_RANGES),
        
        "has_deposited": has_deposited
  }
    
  return customer

def generate_name():
    """Generate a random full name."""
    first_names = ["James", "Maria", "Ahmed", "Yuki", "Olga", "Carlos",
                   "Priya", "Stefan", "Fatima", "Liam", "Sophie", "Wei",
                   "Anna", "Ivan", "Elena", "Marco", "Aisha", "Thomas"]
    last_names = ["Smith", "Mueller", "Tanaka", "Petrov", "Garcia", "Singh",
                  "Rossi", "Nowak", "Chen", "Williams", "Brown", "Eriksson",
                  "Silva", "Ali", "Johansson", "Kowalski", "Weber", "Dumont"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def generate_name():
    """Generate a random full name."""
    first_names = ["James", "Maria", "Ahmed", "Yuki", "Olga", "Carlos",
                   "Priya", "Stefan", "Fatima", "Liam", "Sophie", "Wei",
                   "Anna", "Ivan", "Elena", "Marco", "Aisha", "Thomas"]
    last_names = ["Smith", "Mueller", "Tanaka", "Petrov", "Garcia", "Singh",
                  "Rossi", "Nowak", "Chen", "Williams", "Brown", "Eriksson",
                  "Silva", "Ali", "Johansson", "Kowalski", "Weber", "Dumont"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def generate_dob():
    """Generate date of birth for ages 21-65."""
    age = random.randint(21, 65)
    birth_year = datetime.now().year - age
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # 28 to avoid invalid dates
    return f"{birth_year}-{month:02d}-{day:02d}"

def generate_all_customers():
    """Generate the full dataset."""
    customers = [generate_customer(i) for i in range(1, NUM_CUSTOMERS + 1)]
    
    # Save to JSON
    with open("data/customers.json", "w") as f:
        json.dump(customers, f, indent=2)
    
    # Print summary stats
    total = len(customers)
    deposited = sum(1 for c in customers if c["has_deposited"])
    not_deposited = total - deposited
    
    print(f"Generated {total} customers")
    print(f"  Deposited: {deposited} ({deposited/total*100:.1f}%)")
    print(f"  Not deposited: {not_deposited} ({not_deposited/total*100:.1f}%)")
    print(f"  Saved to data/customers.json")


if __name__ == "__main__":
    generate_all_customers()

