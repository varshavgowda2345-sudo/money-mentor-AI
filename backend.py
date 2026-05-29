import os
import re
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import google.generativeai as genai

app = FastAPI(title="WealthPath AI API", version="1.0.0")

# Enable CORS for Frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock this down to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini API
# Ensure GEMINI_API_KEY environment variable is set
GENI_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
if GENI_KEY and GENI_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=GENI_KEY)

# --- SCHEMAS ---
class UserProfile(BaseModel):
    name: str = "User"
    occupation: str
    location: str
    knowledge_level: str  # Beginner, Intermediate, Expert
    income: float
    expenses: float
    debts: float
    investments: float

class ChatMessage(BaseModel):
    text: str
    profile: UserProfile

class SmsPayload(BaseModel):
    message: str

class SimulationPayload(BaseModel):
    scenario: str # "car", "house", "luxury"
    cost: float
    profile: UserProfile

# --- HELPER SECURITY LOGIC ---
def verify_and_clean_sms(text: str) -> Optional[str]:
    """
    Strict security rule: Instantly drop and ignore messages 
    containing security keys, authentication, codes, or OTPs.
    """
    blacklisted_keywords = [r"otp", r"verification", r"password", r"auth", r"code", r"secret"]
    for pattern in blacklisted_keywords:
        if re.search(pattern, text, re.IGNORECASE):
            return None
    return text

# --- CORE API ENDPOINTS ---

@app.post("/api/ai/mentor-chat")
async def mentor_chat(payload: ChatMessage):
    """
    Context-aware AI bot that translates financial jargon into easy beginner analogies.
    """
    try:
        # Graceful fallback if API key is not configured
        if not GENI_KEY or GENI_KEY == "YOUR_GEMINI_API_KEY_HERE":
            return {
                "response": (
                    f"Hi {payload.profile.name}! I would love to mentor you, but my Gemini API key is currently not configured. "
                    "Please set the `GEMINI_API_KEY` environment variable so I can share personalized financial wisdom with you! "
                    "In the meantime, remember that managing finance is like planting fruit trees—patience and steady watering (saving) "
                    "always lead to sweet returns!"
                )
            }
            
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Inject system instructions and user profile context safely
        prompt_context = f"""
        You are a supportive, wise, and simple financial mentor helping everyday users. 
        The current user profile is:
        - Name: {payload.profile.name}
        - Knowledge Level: {payload.profile.knowledge_level}
        - Net monthly income: {payload.profile.income - payload.profile.expenses}
        
        CRITICAL RULE: Avoid complex, scary financial terms. If you must use them, explain them with an easy real-world analogy (e.g., compare Compound Interest to planting fruit trees, or mutual funds to a shared group pot-luck dinner). Be brief and conversational.
        
        User question: {payload.text}
        """
        
        response = model.generate_content(prompt_context)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sms/parse")
async def parse_sms(payload: SmsPayload):
    """
    Smart SMS parser engine guarding user privacy.
    """
    cleaned_text = verify_and_clean_sms(payload.message)
    if not cleaned_text:
        return {
            "status": "DROPPED_SECURITY_GUARD",
            "category": "Ignored",
            "amount": 0,
            "description": "Message contained an authentication token or OTP. Instantly destroyed for security."
        }
        
    # Basic structural Regex extraction for transaction alerts supporting commas
    amount_match = re.search(r"\$?([0-9,]+(?:\.[0-9]{2})?)", cleaned_text)
    if amount_match:
        try:
            amount = float(amount_match.group(1).replace(",", ""))
        except ValueError:
            amount = 0.0
    else:
        amount = 0.0
    
    category = "General Utilities"
    if "mart" in cleaned_text.lower() or "store" in cleaned_text.lower() or "grocery" in cleaned_text.lower():
        category = "Groceries & Food"
    elif "streamflix" in cleaned_text.lower() or "sub" in cleaned_text.lower() or "premium" in cleaned_text.lower():
        category = "Subscriptions"
        
    return {
        "status": "PARSED_SUCCESSFULLY",
        "category": category,
        "amount": amount,
        "description": f"Tracked transaction safely from alerts text"
    }

@app.post("/api/finance/metrics")
async def get_financial_metrics(profile: UserProfile):
    """
    Calculates Financial Independence timelines & your custom Health Score.
    """
    net_savings = profile.income - profile.expenses
    target_nest_egg = profile.expenses * 12 * 25  # Calculate target standard nest egg (25x rule)
    
    if net_savings <= 0:
        score = 35  # Financial Danger Zone
        years_to_independence = 40.0
    else:
        # Simple dynamic index metrics
        debt_ratio = profile.debts / (profile.income * 12) if profile.income > 0 else 1
        score = int(90 - (debt_ratio * 40) + (profile.investments / 5000))
        score = max(10, min(100, score))  # Limit range between 10-100
        
        # Calculate years to independence (assuming simple linear savings rate)
        if profile.investments >= target_nest_egg:
            years_to_independence = 0.0
        else:
            annual_savings = net_savings * 12
            years_to_independence = (target_nest_egg - profile.investments) / annual_savings
            years_to_independence = max(0.0, years_to_independence)
            
    return {
        "health_score": score,
        "net_savings": net_savings,
        "target_nest_egg": target_nest_egg,
        "years_to_independence": round(years_to_independence, 1)
    }

@app.post("/api/finance/simulate")
async def simulate_decision(payload: SimulationPayload):
    """
    Simulates the impact of a financial decision (e.g. buying a car, house, luxury item)
    on the user's financial health score and independence timeline.
    """
    profile = payload.profile
    cost = payload.cost
    scenario = payload.scenario.lower()
    
    # Calculate original metrics
    original_net_savings = profile.income - profile.expenses
    original_debt_ratio = profile.debts / (profile.income * 12) if profile.income > 0 else 1
    original_score = int(90 - (original_debt_ratio * 40) + (profile.investments / 5000))
    original_score = max(10, min(100, original_score))
    
    # Calculate target standard nest egg (25x rule)
    original_target_nest_egg = profile.expenses * 12 * 25
    if original_net_savings <= 0:
        original_years = 40.0
    else:
        if profile.investments >= original_target_nest_egg:
            original_years = 0.0
        else:
            original_years = max(0.0, (original_target_nest_egg - profile.investments) / (original_net_savings * 12))
        
    # Simulate based on scenario
    simulated_expenses = profile.expenses
    simulated_debts = profile.debts
    simulated_investments = profile.investments
    impact_description = ""
    
    if scenario == "car":
        # Let's assume car is financed: 80% debt, 20% down payment from investments
        down_payment = cost * 0.20
        financed_amount = cost * 0.80
        simulated_investments = max(0.0, profile.investments - down_payment)
        simulated_debts += financed_amount
        # Car adds monthly payments and insurance/maintenance (say 1.5% of cost monthly)
        added_monthly_expense = (financed_amount / 60) + (cost * 0.015)  # 5-year loan + maintenance
        simulated_expenses += added_monthly_expense
        impact_description = f"Financing the car increases your monthly expenses by ${added_monthly_expense:.2f} (loan payment + maintenance) and increases your debt by ${financed_amount:.2f}."
    elif scenario == "house":
        # Let's assume house is financed: 20% down payment from investments, 80% mortgage
        down_payment = cost * 0.20
        financed_amount = cost * 0.80
        simulated_investments = max(0.0, profile.investments - down_payment)
        simulated_debts += financed_amount
        # Mortgage adds monthly payment (say 0.5% of cost monthly)
        added_monthly_expense = cost * 0.005
        simulated_expenses += added_monthly_expense
        impact_description = f"Buying the house increases your debt by ${financed_amount:.2f} and adds a net monthly expense of ${added_monthly_expense:.2f} (mortgage, tax, maintenance)."
    else:  # luxury or other
        # One-time luxury purchase: fully out of investments, or added to credit card debt if investments are insufficient
        if simulated_investments >= cost:
            simulated_investments -= cost
            impact_description = f"Purchasing this luxury item reduces your cash/investments by ${cost:.2f}."
        else:
            remaining_cost = cost - simulated_investments
            simulated_investments = 0.0
            simulated_debts += remaining_cost
            impact_description = f"Purchasing this luxury item drains your investments and adds ${remaining_cost:.2f} to your high-interest debt."
            
    # Calculate simulated metrics
    simulated_net_savings = profile.income - simulated_expenses
    simulated_debt_ratio = simulated_debts / (profile.income * 12) if profile.income > 0 else 1
    simulated_score = int(90 - (simulated_debt_ratio * 40) + (simulated_investments / 5000))
    simulated_score = max(10, min(100, simulated_score))
    
    simulated_target_nest_egg = simulated_expenses * 12 * 25
    if simulated_net_savings <= 0:
        simulated_years = 40.0
    else:
        if simulated_investments >= simulated_target_nest_egg:
            simulated_years = 0.0
        else:
            simulated_years = max(0.0, (simulated_target_nest_egg - simulated_investments) / (simulated_net_savings * 12))
        
    score_change = simulated_score - original_score
    years_change = simulated_years - original_years
    
    return {
        "scenario": scenario,
        "impact_description": impact_description,
        "original_metrics": {
            "health_score": original_score,
            "years_to_independence": round(original_years, 1),
            "net_savings": original_net_savings
        },
        "simulated_metrics": {
            "health_score": simulated_score,
            "years_to_independence": round(simulated_years, 1),
            "net_savings": simulated_net_savings
        },
        "change": {
            "score_impact": score_change,
            "years_impact": round(years_change, 1)
        }
    }
