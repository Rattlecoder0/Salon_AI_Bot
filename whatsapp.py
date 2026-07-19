import requests
import os


def send_whatsapp_message(to_number, message_text):
  
    # WhatsApp Cloud API ke through text message bhejta hai


    url = f"https://graph.facebook.com/v25.0/{os.getenv('PHONE_NUMBER_ID')}/messages"

    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_text},
    }

    # print("WhatsApp API Response:")
    # print(response.text)

    try:
        response = requests.post(url, headers=headers, json=payload)

        print("========== WHATSAPP DEBUG ==========")
        print("URL:", url)
        print("Status:", response.status_code)
        print("Response:", response.text)
        print("====================================")

    except Exception as e:
        print("WHATSAPP EXCEPTION:", e)
        raise

    if response.status_code >= 400:
        print(response.text)