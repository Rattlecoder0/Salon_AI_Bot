import json
from fastapi import FastAPI
from salon_flow import handle_message
from processed_messages import is_processed, mark_processed
from logger_config import log_event, logger
from dotenv import load_dotenv
from database.database import create_tables
from database.seed_database import seed_database
import os

app = FastAPI()
load_dotenv()

@app.on_event("startup")
async def startup_event():
    create_tables()
    seed_database()
    log_event("BOT_STARTED")


@app.get("/")
def home():
    return {"message": "Salon AI Bot is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

from fastapi import Request

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)

    return {"error": "verification failed"}


@app.post("/webhook")
async def webhook(request: Request):

    # WhatsApp se aaya hua data read karte hain
    body = await request.json()

    print("========== WEBHOOK BODY ==========")
    print(json.dumps(body, indent=2))
    print("==================================")

    user_number = "UNKNOWN"
    user_message = "UNKNOWN"

    # Agar payload me messages nahi hai to ye read/delivered/status event hai isko ignore kar do
    if "messages" not in body["entry"][0]["changes"][0]["value"]:

        return {"status": "ignored"}

    try:
        # User ka number extract karna
        user_number = body["entry"][0]["changes"][0]["value"]["messages"][0]["from"]

        # User ka message extract karna
        user_message = body["entry"][0]["changes"][0]["value"]["messages"][0]["text"][
            "body"
        ]

        # Message ID extract karo
        message_id = body["entry"][0]["changes"][0]["value"]["messages"][0]["id"]

        # Duplicate webhook ignore karo
        if is_processed(message_id):
            return {"status": "ignored"}

        mark_processed(message_id)

        # Auto reply
        handle_message(user_number, user_message)

    except Exception:
        logger.exception(
            f"UNHANDLED_EXCEPTION | "
            f"USER={user_number} | "
            f"MESSAGE={user_message} | "
        )

    return {"status": "ok"}


user_states = {}
