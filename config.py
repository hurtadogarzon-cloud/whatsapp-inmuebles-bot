# confing.py
from dotenv import load_dotenv
import os

load_dotenv()

# Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("OPENAI_API_KEY:", OPENAI_API_KEY[:5] if OPENAI_API_KEY else None)
print("TWILIO_ACCOUNT_SID:", TWILIO_ACCOUNT_SID)


