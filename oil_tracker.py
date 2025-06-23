import os
import requests
import logging
from datetime import datetime

# === CONFIG ===
BOT_TOKEN = "7942291340:AAHHJ1ZuxClh7GwchbR67LMXLyuahrkP6jc"
CHAT_ID = "8169402426"
TWELVE_DATA_API_KEY = "542d93a2800d4bd38aba4ecf3d1b7a45"
OIL_SYMBOL = "WTI/USD"
PRICE_API_URL = f"https://api.twelvedata.com/time_series?symbol={OIL_SYMBOL}&interval=1min&outputsize=6&apikey={TWELVE_DATA_API_KEY}"

# === FUNCTIONS ===
def get_oil_prices():
    try:
        response = requests.get(PRICE_API_URL)
        print("Twelve Data API response code:", response.status_code)
        print("Twelve Data API response body:", response.text[:200])
        data = response.json()
        values = data.get("values", [])
        if not values:
            raise Exception("No price data returned")

        # Extract latest closing prices in reverse order (oldest first)
        closing_prices = [float(entry["close"]) for entry in reversed(values)]
        return closing_prices
    except Exception as e:
        logging.error(f"Error fetching oil price: {e}")
        return []

def calculate_momentum(prices):
    if len(prices) < 6:
        return 0
    diffs = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
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

    prices = get_oil_prices()
    if prices:
        latest_price = prices[-1]
        momentum = calculate_momentum(prices)
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        if momentum < 0.05:
            send_telegram_alert(f"⚠️ *Exit Alert* {now}\nOil price momentum weakening. Current price: ${latest_price:.2f}")
        elif momentum > 0.3:
            send_telegram_alert(f"🚨 *Buy Alert* {now}\nUpward price momentum detected. Current price: ${latest_price:.2f}")

