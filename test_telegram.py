"""
test_telegram.py — Тест Telegram Executor
"""

from jvg import ActionExecutor

TOKEN = "8674008522:AAGz3qlw2I-lAjUq5gBI5E8RV_OomQnuyLc"
CHAT_ID = "5835418456"

def main():
    print("📤 Тест отправки сообщения в Telegram")
    
    result = ActionExecutor.execute(
        "send_telegram",
        {
            "token": TOKEN,
            "chat_id": CHAT_ID,
            "message": "🔔 <b>JVG Platform</b>\n\nСообщение успешно отправлено!"
        }
    )
    
    print(f"✅ Успешно: {result.success}")
    print(f"📝 Результат: {result.stdout}")
    if result.error:
        print(f"❌ Ошибка: {result.error}")

if __name__ == "__main__":
    main()
