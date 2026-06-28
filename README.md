# Salon AI Bot 🤖

## About
Salon AI Bot is a WhatsApp-based queue management system that allows customers to book salon appointments through chat. It automatically collects customer details, lets users choose a service and barber, stores bookings in Google Sheets, and helps reduce manual appointment management.

---

## Features
- WhatsApp appointment booking
- Queue management system
- Customer detail collection
- Service selection
- Barber selection
- Google Sheets integration
- FastAPI webhook

---

## Tech Stack
- Python
- FastAPI
- WhatsApp Cloud API
- Google Sheets API
- gspread
- ngrok / Cloudflare Tunnel

---

# Installation

### 1. Clone the repository

```bash
git clone https://github.com/Rattlecoder0/Salon_AI_Bot.git
cd Salon_AI_Bot
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

# Required Files
Before running the project, create the following files.

## 1. `.env`
Create a `.env` file in the project root.

Example:

```env
VERIFY_TOKEN=your_verify_token
WHATSAPP_TOKEN=your_whatsapp_access_token
PHONE_NUMBER_ID=your_phone_number_id
```

---

## 2. `credentials.json`
Download your Google Service Account credentials from Google Cloud Console and place the file in the project root.

Example:

```
Salon_AI_Bot/
│
├── credentials.json
├── .env
├── main.py
```

---

## 3. Google Sheet
- Create a Google Sheet
- Share it with the Service Account email
- Give **Editor** permission

---

# Run the Project

```bash
python main.py
```

The server will start on:

```
http://localhost:8000
```

---

# Folder Structure
```
Salon_AI_Bot
│
├── customer_data.py
├── main.py
├── salon_flow.py
├── states.py
├── whatsapp.py
├── credentials.json
├── .env
├── requirements.txt
├── README.md
```

---

## Author
**Ubaid**