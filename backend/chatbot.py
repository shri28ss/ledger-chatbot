import os
from collections import defaultdict
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase Client
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ivbrlminlzhpitiyczze.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_KEY is None:
    raise ValueError("Missing SUPABASE_KEY in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

import re

def detect_intent(query: str) -> str:
    query = query.lower()
    
    # Use Regex for smarter intent matching
    if re.search(r'\b(max|highest|biggest|maximum|most|largest|top)\b.*\b(spend|spent|amount|transaction)\b|\bmax\b', query):
        return "MAX_SPEND"
    
    # E.g. "how much did I spend", "total spend", "total amount"
    if re.search(r'\b(how much|total|sum)\b.*\b(spend|spent|amount)\b|\b(total)\b', query):
        return "TOTAL"
        
    # E.g. "show categories", "food spending", "where did I spend"
    if re.search(r'\b(category|categories|food|travel|merchant|where)\b', query):
        return "CATEGORY"
        
    # E.g. "bank split", "which account"
    if re.search(r'\b(bank|account|card)\b', query):
        return "BANK"
        
    # E.g. "when did I spend", "daily split"
    if re.search(r'\b(when|date|daily|day|month)\b', query):
        return "TIME"
        
    return "UNKNOWN"

def get_user_accounts(user_id: str) -> list:
    """Fetch all accounts linked to the user."""
    try:
        response = supabase.table("accounts").select("account_id, account_name").eq("user_id", user_id).execute()
        return response.data if response.data else []
    except Exception:
        return []

def get_total_spend(user_id: str) -> dict:
    """Sum amounts where transaction_type = 'debit'."""
    try:
        response = supabase.table("transactions") \
            .select("amount, document_id") \
            .eq("user_id", user_id) \
            .eq("transaction_type", "debit") \
            .execute()
        
        data = response.data if response.data else []
        total = sum(float(item.get("amount", 0) or 0) for item in data)
        distinct_docs = len(set(item["document_id"] for item in data if item.get("document_id")))
        
        return {"total": total, "statements": distinct_docs}
    except Exception:
        return {"total": 0, "statements": 0}

def get_max_spend(user_id: str) -> dict:
    """Find the single highest spending transaction."""
    try:
        response = supabase.table("transactions") \
            .select("amount, details, transaction_date") \
            .eq("user_id", user_id) \
            .eq("transaction_type", "debit") \
            .execute()
        
        data = response.data if response.data else []
        if not data:
            return {}
            
        # Extract the highest transaction
        max_txn = max(data, key=lambda x: float(x.get("amount", 0) or 0))
        return {
            "amount": float(max_txn.get("amount", 0) or 0),
            "details": max_txn.get("details", "Unknown Merchant"),
            "date": max_txn.get("transaction_date", "Unknown Date")
        }
    except Exception:
        return {}

def guess_category(details: str) -> str:
    """Intelligently map a raw transaction detail string to a clean category."""
    if not details:
        return "Other"
        
    d = details.lower()
    
    # Define mapping rules
    rules = {
        "Food & Dining": ["swiggy", "zomato", "restaurant", "cafe", "baker", "pizza", "burger", "mcdonalds", "kfc", "starbucks", "eats"],
        "Travel & Transport": ["uber", "ola", "irctc", "flight", "airways", "indigo", "spicejet", "metro", "redbus", "petrol", "fuel", "hpcl", "bpcl", "ioc"],
        "Shopping": ["amazon", "flipkart", "myntra", "zepto", "blinkit", "instamart", "bigbasket", "mall", "dmart", "reliance"],
        "Bills & Utilities": ["airtel", "jio", "vi", "vodafone", "electricity", "bescom", "water", "gas", "bill", "recharge", "broadband"],
        "Entertainment": ["netflix", "prime", "hotstar", "spotify", "bookmyshow", "pvrcinemas", "movie"],
        "Finance & Taxes": ["emi", "loan", "tax", "gst", "insurance", "lic", "mutual fund", "zerodha", "groww", "upstox"],
        "UPI/Transfers": ["upi", "paytm", "phonepe", "gpay", "transfer", "neft", "imps", "rtgs", "cash withdrawal", "atm"]
    }
    
    for category, keywords in rules.items():
        if any(keyword in d for keyword in keywords):
            return category
            
    return "Other"

def get_category_spend(user_id: str) -> dict:
    """Group spend by intelligent category mapping based on details."""
    try:
        response = supabase.table("transactions") \
            .select("amount, details") \
            .eq("user_id", user_id) \
            .eq("transaction_type", "debit") \
            .execute()
        
        data = response.data if response.data else []
        categories = {}
        
        for item in data:
            raw_details = item.get("details", "")
            cat = guess_category(raw_details)
            amt = float(item.get("amount", 0) or 0)
            categories[cat] = categories.get(cat, 0.0) + amt
            
        # Limit to top 5 for readability
        def get_val(item): return item[1]
        sorted_cats = sorted(categories.items(), key=get_val, reverse=True)[:5]
        return dict(sorted_cats)
    except Exception:
        return {}

def get_bank_spend(user_id: str) -> dict:
    """Show spend aggregated by user."""
    try:
        response = supabase.table("transactions") \
            .select("amount") \
            .eq("user_id", user_id) \
            .eq("transaction_type", "debit") \
            .execute()
        
        data = response.data if response.data else []
        total = sum(float(item.get("amount", 0) or 0) for item in data)
        
        accounts = get_user_accounts(user_id)
        if not accounts:
            return {"Aggregated Account": total} if total > 0 else {}
            
        # If we just have user-level transactions, we display them against their accounts list
        num_accounts = len(accounts)
        return {f"Total across {num_accounts} Account(s)": total} if total > 0 else {}
    except Exception:
        return {}

def get_time_spend(user_id: str) -> dict:
    """Group spend by date."""
    try:
        response = supabase.table("transactions") \
            .select("amount, transaction_date") \
            .eq("user_id", user_id) \
            .eq("transaction_type", "debit") \
            .execute()
        
        data = response.data if response.data else []
        timeline = {}
        for item in data:
            dt = item.get("transaction_date") or "Unknown Date"
            amt = float(item.get("amount", 0) or 0)
            timeline[dt] = timeline.get(dt, 0.0) + amt
            
        # Get top 5 highest spending days
        def get_val(item): return item[1]
        sorted_dates = sorted(timeline.items(), key=get_val, reverse=True)[:5]
        return dict(sorted_dates)
    except Exception:
        return {}

def format_response(intent: str, data: Optional[dict], user_id: str) -> str:
    """Create clean formatted strings for the chatbot output."""
    if intent == "MAX_SPEND":
        if not data:
            return f"💰 No spending data found for User ID: {user_id}. Please ensure statements are uploaded."
        return (
            f"🔥 **Highest Single Spend:**\n"
            f"You spent **₹{data['amount']:,.2f}** at **{data['details']}** on {data['date']}."
        )

    if intent == "TOTAL":
        if not data:
            return f"💰 No spending data found for User ID: {user_id}. Please ensure statements are uploaded."
        total = data.get("total", 0)
        statements = data.get("statements", 0)
        if total == 0:
            return f"💰 No spending data found for User ID: {user_id}. Please ensure statements are uploaded."
        return (
            f"📊 **Summary Across Your Statements**\n"
            f"You have uploaded {statements} statements.\n"
            f"💰 **Total Spend:** ₹{total:,.2f}"
        )
    
    if intent == "CATEGORY":
        if not data: return "No category/merchant spending data found."
        resp = "🏆 **Top Spending Destinations:**\n"
        for cat, amt in data.items():
            resp += f"- {cat}: ₹{amt:,.2f}\n"
        return resp.strip()

    if intent == "BANK":
        if not data: return "No bank-wise spending found for this user."
        resp = "🏦 **Bank / Account Split:**\n"
        for bank, amt in data.items():
            resp += f"- {bank}: ₹{amt:,.2f}\n"
        return resp.strip()

    if intent == "TIME":
        if not data: return "No daily spending history found."
        resp = "📅 **Highest Spending Days:**\n"
        for dt, amt in data.items():
            resp += f"- {dt}: ₹{amt:,.2f}\n"
        return resp.strip()

    return "I'm sorry, I didn't catch that. You can ask for your 'highest spend', 'total spend', 'top categories', or 'daily spending'."

def chatbot(query: str, user_id: str) -> str:
    """Main chatbot function to coordinate intent detection and query execution."""
    intent = detect_intent(query)
    
    if intent == "MAX_SPEND":
        result = get_max_spend(user_id)
    elif intent == "TOTAL":
        result = get_total_spend(user_id)
    elif intent == "CATEGORY":
        result = get_category_spend(user_id)
    elif intent == "BANK":
        result = get_bank_spend(user_id)
    elif intent == "TIME":
        result = get_time_spend(user_id)
    else:
        return format_response(intent, None, user_id)
    
    return format_response(intent, result, user_id)
