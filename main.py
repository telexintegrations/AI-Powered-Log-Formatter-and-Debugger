import httpx
import json
from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4
from dateutil import parser
from sqlalchemy.orm import Session
from openai import OpenAI  # If using OpenAI for AI analysis
# from database import get_db  # Your DB session handler
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

app = FastAPI()

# Config
DATABASE_URL = os.getenv("DATABASE_URL")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEYS")
TELEX_WEBHOOK_URL = os.getenv("TELEX_WEBHOOK_URL")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



class LogEntryDB(Base):
    __tablename__ = "logs"
    id = Column(String, primary_key=True, index=True)
    source = Column(String, index=True)
    level = Column(String)
    message = Column(String)
    timestamp = Column(DateTime)
    processed_at = Column(DateTime, default=datetime.utcnow)



Base.metadata.create_all(bind=engine)


# Log Entry Model from Telex
class TelexLog(BaseModel):
    message: str
    settings: list


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Define error and warning keywords
ERROR_KEYWORDS = ["failed", "error", "exception", "crash"]
WARNING_KEYWORDS = ["deprecated", "slow", "unstable"]



# AI Error Analysis Function
async def analyze_with_ai(log_message: str) -> str:
    """Use OpenAI to analyze error logs and suggest fixes."""
    if not OPENAI_API_KEY:
        return "AI analysis is disabled."

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.completions.create(
        model="gpt-3.5-turbo",
        prompt=f"Analyze this error log and suggest a fix: {log_message}",
        max_tokens=100
    )
    return response["choices"][0]["text"].strip()


# Send log to Slack
async def send_to_slack(log_data: dict):
    """Send log details to Slack."""
    if not SLACK_WEBHOOK_URL:
        print("SLACK_WEBHOOK_URL is not set.")
        return

    message = (
        f"🔴 *{log_data['level']}* - {log_data['source']}\n"
        f"📅 *Time:* {log_data['timestamp']}\n"
        f"📝 *Message:* {log_data['message']}"
    )
    payload = {"text": message}

    async with httpx.AsyncClient() as client:
        response = await client.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            print("✅ Log sent to Slack successfully.")
        else:
            print(f"⚠️ Failed to send log: {response.status_code} - {response.text}")



async def send_to_telex(log_data: dict):
    """Send log details to Slack."""
    if not TELEX_WEBHOOK_URL:
        print("TELEX_WEBHOOK_URL is not set.")
        return

    message = f"🔴 *{log_data['level']}* - {log_data['source']}\n📅 *Time:* {log_data['timestamp']}\n📝 *Message:* {log_data['message']}"
    # payload = {"text": message}
    payload = {
    "event_name": "Applicaion Log",
    "message": message,
    "status": "error",
    "username": "Breeze"
}

    async with httpx.AsyncClient() as client:
        response = await client.post(TELEX_WEBHOOK_URL, json=payload, headers={
        "Accept": "application/json",
        "Content-Type": "application/json"
    })
        if response.status_code == 200:
            print("✅ Log sent to Slack successfully.")
        else:
            print(f"⚠️ Failed to send log: {response.status_code} - {response.text}")


# Process Log from Telex
@app.post("/telex/logs")
async def process_telex_log(log: TelexLog, db: Session = Depends(get_db)):
    """Process logs received from Telex, analyze, and send alerts."""
    
    # Extract settings
    settings_dict = {s["label"]: s["value"] for s in log.settings}
    enable_ai = settings_dict.get("Enable AI Analysis", "No") == "Yes"
    send_slack = settings_dict.get("Send Alerts to Slack", "No") == "Yes"
    send_telex = settings_dict.get("Send Alerts to Telex", "No") == "Yes"

    # Categorize log
    category = "INFO"
    message_lower = log.message.lower()
    
    if any(word in message_lower for word in ERROR_KEYWORDS):
        category = "ERROR"
    elif any(word in message_lower for word in WARNING_KEYWORDS):
        category = "WARNING"

    # AI analysis (if enabled)
    ai_suggestion = None
    if enable_ai and category == "ERROR":
        ai_suggestion = await analyze_with_ai(log.message)

    # Save log to DB
    db_log = LogEntryDB(
        id=str(uuid4()),
        source="Telex",
        level=category,
        message=log.message,
        timestamp=datetime.utcnow(),
        processed_at=datetime.utcnow()
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    # Send to Slack if enabled
    if send_slack:
        await send_to_slack({
            "level": category,
            "source": "Telex",
            "timestamp": db_log.timestamp.isoformat(),
            "message": log.message
        })

    # Send to Telex if enabled
    if send_telex:
        await send_to_telex({
            "level": category,
            "source": "Telex",
            "timestamp": db_log.timestamp.isoformat(),
            "message": log.message
        })

    # Return processed log
    return {
        "original_message": log.message,
        "category": category,
        "ai_suggestion": ai_suggestion or "No AI analysis performed.",
        "processed_at": db_log.processed_at.isoformat()
    }
