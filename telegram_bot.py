import os
import json
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Конфигурация
TG_TOKEN = "8427169783:AAFpYyOZot8ZQt06Yz4XUmQObabRcaOiZyE"
JVG_API_URL = "http://localhost:8000"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я SLCCollectorBot. Отправь мне запрос, и я передам его в JVG API.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"⏳ Обрабатываю запрос: {user_text}")

    try:
        # Отправляем запрос в JVG API
        response = requests.post(
            f"{JVG_API_URL}/step",
            json={"doc_id": "telegram_request", "new_state": "ВЫПОЛНЕНИЕ", "action_result": user_text},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            await update.message.reply_text(f"✅ Результат: {result}")
        else:
            await update.message.reply_text(f"❌ Ошибка API: {response.status_code}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

def main():
    app = ApplicationBuilder().token(TG_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
