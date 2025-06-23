import os
import requests
import logging
from datetime import datetime

# === CONFIG ===
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PRICE_API_URL = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F?interval=5m&range=1d"

# === FUNCTIONS ===
def get_oil_price():
    try:
        response = requests.get(PRICE_API_URL)
        data = response.json()
        prices = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        timestamps = data["chart"]["result"][0]["timestamp"]
        return list(zip(timestamps, prices))
    except Exception as e:
        logging.error(f"Error fetching oil price: {e}")
        return []

def calculate_momentum(prices):
    if len(prices) < 6:
        return 0
    diffs = [prices[i+1] - prices[i] for i in range(-6, -1)]
    return sum(diffs) / len(diffs)

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    print("Telegram send status:", response.status_code)
    print("Response:", response.text)

# === MAIN LOGIC ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Optional: test message to confirm secure setup
    send_telegram_alert("✅ Secure mode: Telegram alerts are working!")

    prices = get_oil_price()
    if prices:
        latest_ts, latest_price = prices[-1]
        history = [p for _, p in prices if p is not None]

        momentum = calculate_momentum(history)
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        if momentum < 0.05:
            send_telegram_alert(f"⚠️ *Exit Alert* {now}\nOil price momentum weakening. Current price: ${latest_price:.2f}")
        elif momentum > 0.3:
            send_telegram_alert(f"🚨 *Buy Alert* {now}\nUpward price momentum detected. Current price: ${latest_price:.2f}")
