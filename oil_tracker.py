import os
import requests
import logging
from datetime import datetime

# === CONFIG ===
BOT_TOKEN = "7942291340:AAHHJ1ZuxClh7GwchbR67LMXLyuahrkP6jc"
CHAT_ID = "8169402426"
PRICE_API_URL = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F?interval=5m&range=1d"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# === FUNCTIONS ===
def get_oil_price():
    for attempt in range(3):
        try:
            response = requests.get(PRICE_API_URL, headers=HEADERS)
            print("Yahoo API response code:", response.status_code)
            if response.status_code == 429:
                print("Rate limited. Waiting and retrying...")
                time.sleep(3 * (attempt + 1))
                continue
            data = response.json()
            prices = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            timestamps = data["chart"]["result"][0]["timestamp"]
            price_data = list(zip(timestamps, prices))
            price_data = [(ts, p) for ts, p in price_data if p is not None]
            return price_data
        except Exception as e:
            logging.error(f"Error fetching oil price (attempt {attempt+1}): {e}")
            time.sleep(2)
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

    prices = get_oil_price()
    if prices:
        latest_ts, latest_price = prices[-1]
        history = [p for _, p in prices]

        momentum = calculate_momentum(history)
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        if momentum < 0.05:
            send_telegram_alert(f"⚠️ *Exit Alert* {now}\nOil price momentum weakening. Current price: ${latest_price:.2f}")
        elif momentum > 0.3:
            send_telegram_alert(f"🚨 *Buy Alert* {now}\nUpward price momentum detected. Current price: ${latest_price:.2f}")
        else:
            print(f"Checked at {now}. Momentum OK. No alert.")
    else:
        logging.error("Failed to retrieve price data after retries.")

