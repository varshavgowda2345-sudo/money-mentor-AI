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
        
    # Basic structural Regex extraction for transaction alerts
    amount_match = re.search(r"\$?(\d+(?:\.\d{2})?)", cleaned_text)
    amount = float(amount_match.group(1)) if amount_match else 0.0
    
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
    if net_savings <= 0:
        score = 35 # Financial Danger Zone
        years_to_independence = 40
    else:
        # Simple dynamic index metrics
        debt_ratio = profile.debts / (profile.income * 12) if profile.income > 0 else 1
        score = int(90 - (debt_ratio * 40) + (profile.investments / 5000))
        score = max(10, min(100, score)) # Limit range between 10-100
        
        # Calculate target standard nest egg (25x rule)
        target_nest_egg = (profile.expenses )*