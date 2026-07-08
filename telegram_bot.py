"""
telegram_bot.py — Telegram-бот для JVG Platform
"""

import os
import sys
import json
import logging
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Добавляем пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from jvg import JVGCompiler, JVGValidatorPipeline, JVGStore, JVGVectorizer, JVGRankingEngine

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация компонентов
compiler = JVGCompiler()
validator = JVGValidatorPipeline()
store = JVGStore()
vectorizer = JVGVectorizer()
ranking = JVGRankingEngine()

# Токен бота (замени на свой)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    await update.message.reply_text(
        "🤖 *JVG Telegram Bot*\n\n"
        "Я помогаю работать с JVG (JSON Vectorograph).\n\n"
        "📌 *Доступные команды:*\n"
        "/start — показать это сообщение\n"
        "/help — помощь\n"
        "/compile — скомпилировать текст в JVG\n"
        "/search — поиск по хранилищу\n"
        "/store — показать сохранённые документы\n"
        "/explain — объяснить документ\n\n"
        "📝 *Использование:*\n"
        "Просто отправьте текст в формате JVG, и я его обработаю.",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    await update.message.reply_text(
        "📖 *Помощь по JVG Bot*\n\n"
        "1. Отправьте текст в формате JVG (YAML-подобный)\n"
        "2. Используйте команды для работы\n"
        "3. /compile <текст> — компиляция\n"
        "4. /search <запрос> — поиск\n"
        "5. /store — список документов\n"
        "6. /explain <doc_id> — объяснение",
        parse_mode="Markdown"
    )

async def compile_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Компилирует текст в JVG."""
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("❌ Укажите текст для компиляции. Пример: /compile entity: name: Тест")
        return
    
    try:
        result = compiler.compile(text)
        if result["status"] == "success":
            jvg = result["jvg"]
            # Сохраняем в хранилище
            doc_id = store.save(jvg)
            # Векторизуем
            vectorizer.vectorize(jvg, doc_id)
            # Ранжируем
            ranking.index_jvg(jvg, doc_id)
            
            await update.message.reply_text(
                f"✅ *Компиляция успешна!*\n"
                f"📄 Документ сохранён с ID: `{doc_id}`\n\n"
                f"Содержимое:\n```json\n{json.dumps(jvg, indent=2, ensure_ascii=False)[:1000]}...\n```",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(f"❌ Ошибка компиляции: {result.get('errors', 'неизвестная ошибка')}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Поиск по хранилищу."""
    query = " ".join(context.args) if context.args else ""
    if not query:
        await update.message.reply_text("❌ Укажите запрос для поиска. Пример: /search система")
        return
    
    try:
        results = ranking.search(query, top_k=5)
        if not results:
            await update.message.reply_text("🔍 Ничего не найдено.")
            return
        
        message = f"🔍 *Результаты поиска:* '{query}'\n\n"
        for i, r in enumerate(results, 1):
            message += f"{i}. `{r.get('id', 'unknown')}` — {r.get('title', 'Без названия')} ({r.get('type', 'unknown')})\n"
            message += f"   Скор: {r.get('score', 0):.4f}\n"
        
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка поиска: {str(e)}")

async def store_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список сохранённых документов."""
    try:
        items = store.list()
        if not items:
            await update.message.reply_text("📭 Хранилище пусто.")
            return
        
        message = f"📁 *Сохранённые документы:* ({len(items)})\n\n"
        for item in items[:10]:
            message += f"• `{item.get('id', '')[:30]}` — {item.get('title', 'Без названия')} ({item.get('type', 'unknown')})\n"
        
        if len(items) > 10:
            message += f"\n... и ещё {len(items) - 10} документов."
        
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def explain_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Объясняет документ по ID."""
    doc_id = " ".join(context.args) if context.args else ""
    if not doc_id:
        await update.message.reply_text("❌ Укажите ID документа. Пример: /explain doc_123")
        return
    
    try:
        jvg = store.get(doc_id)
        if not jvg:
            await update.message.reply_text(f"❌ Документ с ID `{doc_id}` не найден.", parse_mode="Markdown")
            return
        
        data = jvg.get("vectorograph", {})
        entity = data.get("entity", {})
        state = data.get("state", {})
        evolution = data.get("evolution", {})
        
        message = (
            f"📄 *Объяснение документа:* `{doc_id}`\n\n"
            f"📌 *Название:* {entity.get('name', 'неизвестно')}\n"
            f"📂 *Тип:* {entity.get('type', 'неизвестно')}\n"
            f"🎯 *Цель:* {entity.get('purpose', 'не указана')}\n"
            f"📊 *Состояние:* {state.get('current', 'неизвестно')}\n"
            f"⚠️ *Проблемы:* {', '.join(state.get('problems', ['нет']))}\n"
            f"📖 *История:* {evolution.get('history', 'нет')[:100]}...\n"
        )
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений."""
    text = update.message.text
    
    # Пытаемся скомпилировать текст как JVG
    try:
        result = compiler.compile(text)
        if result["status"] == "success":
            jvg = result["jvg"]
            doc_id = store.save(jvg)
            vectorizer.vectorize(jvg, doc_id)
            ranking.index_jvg(jvg, doc_id)
            
            await update.message.reply_text(
                f"✅ *Компиляция успешна!*\n"
                f"📄 ID: `{doc_id}`\n"
                f"📌 {jvg['vectorograph']['entity']['name']} ({jvg['vectorograph']['entity']['type']})",
                parse_mode="Markdown"
            )
            return
    except Exception:
        pass
    
    # Если не удалось — просто отвечаем
    await update.message.reply_text(
        "ℹ️ Отправьте текст в формате JVG, чтобы я скомпилировал его.\n"
        "Или используйте команды: /help"
    )

def main():
    """Запуск бота."""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Укажите TELEGRAM_BOT_TOKEN в переменной окружения или в коде")
        return
    
    print("🤖 Запуск Telegram-бота...")
    print(f"   Токен: {BOT_TOKEN[:10]}...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("compile", compile_text))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("store", store_command))
    application.add_handler(CommandHandler("explain", explain_command))
    
    # Обработка сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск
    print("✅ Бот запущен. Нажмите Ctrl+C для остановки.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
