import os
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_TOKEN_HERE")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """Ты универсальный AI-помощник для студентов и школьников. Работаешь на трёх языках: таджикском, русском и английском.

ТВОИ ВОЗМОЖНОСТИ:
1. Рефераты полные с планом (минимум 500 слов)
2. Курсовые работы со структурой
3. Домашние задания по всем предметам
4. Перевод таджикский русский английский
5. Объяснение любых тем
6. Сочинения и эссе
7. Решение задач пошагово
8. Ответы на любые вопросы

ПРАВИЛА:
- Отвечай на языке пользователя
- Рефераты минимум 500 слов с заголовками
- Задачи решай пошагово
- Никогда не отказывай"""

user_histories = {}

def ask_claude(user_id, user_message):
    if user_id not in user_histories:
        user_histories[user_id] = []
    user_histories[user_id].append({"role": "user", "content": user_message})
    if len(user_histories[user_id]) > 20:
        user_histories[user_id] = user_histories[user_id][-20:]
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 2000, "system": SYSTEM_PROMPT, "messages": user_histories[user_id]},
            timeout=60
        )
        reply = response.json()["content"][0]["text"]
        user_histories[user_id].append({"role": "assistant", "content": reply})
        return reply
    except:
        return "Хатогӣ. Дубора кӯшиш кунед."

def get_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📝 Реферат"), KeyboardButton("📚 Курсовая")],
        [KeyboardButton("🏠 Домашнее задание"), KeyboardButton("🌐 Перевод")],
        [KeyboardButton("🔢 Математика"), KeyboardButton("✏️ Сочинение")],
        [KeyboardButton("📖 Объяснение"), KeyboardButton("❓ Вопрос")],
    ], resize_keyboard=True)

async def start(update, context):
    await update.message.reply_text(
        "🎓 Салом! Привет! Hello!\n\n🇹🇯 Ёрдамчии донишҷӯён\n🇷🇺 Помощник для студентов\n🇬🇧 Study Assistant\n\n✅ Ройгон / Бесплатно / Free\n✅ 3 забон / 3 языка\n✅ 24/7",
        reply_markup=get_keyboard()
    )

async def handle_message(update, context):
    user_id = update.message.from_user.id
    text = update.message.text
    quick = {
        "📝 Реферат": "Напиши тему реферата:",
        "📚 Курсовая": "Напиши тему курсовой:",
        "🏠 Домашнее задание": "Напиши задание:",
        "🌐 Перевод": "Напиши текст для перевода:",
        "🔢 Математика": "Напиши задачу:",
        "✏️ Сочинение": "Напиши тему сочинения:",
        "📖 Объяснение": "Что объяснить?",
        "❓ Вопрос": "Задай вопрос!",
    }
    if text in quick:
        await update.message.reply_text(quick[text])
        return
    msg = await update.message.reply_text("⏳ Думаю...")
    reply = ask_claude(user_id, text)
    await msg.delete()
    if len(reply) > 4000:
        for i in range(0, len(reply), 4000):
            await update.message.reply_text(reply[i:i+4000])
    else:
        await update.message.reply_text(reply)

async def reset(update, context):
    user_histories[update.message.from_user.id] = []
    await update.message.reply_text("🔄 Тоза шуд! / Очищено!", reply_markup=get_keyboard())

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
