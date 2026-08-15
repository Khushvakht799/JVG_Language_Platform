import requests
import time

TG_TOKEN = "8427169783:AAFpYyOZot8ZQt06Yz4XUmQObabRcaOiZyE"
JVG_API_URL = "http://localhost:8000"

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    try:
        resp = requests.get(url, params=params, timeout=35)
        return resp.json().get("result", [])
    except Exception as e:
        print(f"Ошибка получения обновлений: {e}")
        return []

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print(f"Ошибка отправки: {e}")

print("🤖 Бот запущен (синхронный режим)...")
last_update_id = 0

while True:
    updates = get_updates(offset=last_update_id + 1 if last_update_id else None)
    for u in updates:
        last_update_id = u["update_id"]
        msg = u.get("message")
        if msg and "text" in msg:
            chat_id = msg["chat"]["id"]
            user_text = msg["text"]
            send_message(chat_id, f"⏳ Обрабатываю: {user_text}")

            try:
                resp = requests.post(
                    f"{JVG_API_URL}/step",
                    json={"doc_id": "telegram_request", "new_state": "ВЫПОЛНЕНИЕ", "action_result": user_text},
                    timeout=10
                )
                if resp.status_code == 200:
                    send_message(chat_id, f"✅ Результат: {resp.json()}")
                else:
                    send_message(chat_id, f"❌ Ошибка API: {resp.status_code}")
            except Exception as e:
                send_message(chat_id, f"❌ Ошибка: {str(e)}")

    time.sleep(2)
