from fastapi import FastAPI
from salon_flow import handle_message
from processed_messages import is_processed, mark_processed
from logger_config import log_event, logger

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    log_event("BOT_STARTED")


@app.get("/")
def home():
    return {"message": "Salon AI Bot is running"}


from fastapi import Request

VERIFY_TOKEN = "salon_bot_123"


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

    print("MESSAGE RECEIVED:")
    # print(body)

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

            print(f"DUPLICATE MESSAGE IGNORED: {message_id}")

            return {"status": "ignored"}

        mark_processed(message_id)

        print(f"MESSAGE ID: {message_id}")
        print(f"User Number: {user_number}")
        print(f"Message: {user_message}")

        # Auto reply
        handle_message(user_number, user_message)

    except Exception:
        logger.exception(
            f"UNHANDLED_EXCEPTION | "
            f"USER={user_number} | "
            f"MESSAGE={user_message} | "
        )

    return {"status": "ok"}


# Environment variables ke liye
from dotenv import load_dotenv
import os

load_dotenv()
# User kis stage par hai usko store karne ke liye
# Example:
# {
#   "919999999999": "MAIN_MENU"
# }
user_states = {}
