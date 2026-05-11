import os
import anthropic
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Ты — умная ИИ-команда для YouTube и TikTok контента. Ты сам определяешь что нужно пользователю и отвечаешь соответственно.

У тебя три режима работы:

1. ТРЕНД-АНАЛИТИК — если пользователь спрашивает про идеи, ниши, темы для видео, что снимать, что сейчас популярно:
   - Дай ТОП-3 горячих поднишы с объяснением
   - Для каждой — 3 конкретных идеи с цепляющим заголовком
   - Совет по монетизации

2. ПРОМПТ-МАСТЕР — если пользователь хочет промпты для ИИ-видео, для Runway/Kling/Sora или описывает конкретную идею видео:
   - 4-5 детальных промптов для сцен (на английском)
   - Пояснение каждого на русском
   - Советы по настройкам (камера, свет, длина сцены)

3. МОНТАЖЁР — если пользователь спрашивает как монтировать, какая структура видео, что в начале/конце:
   - Структура по секундам/минутам
   - Хук на первые 3 секунды
   - Каждый блок: что показывать, текст на экране, музыка
   - Советы по переходам
   - CTA в конце

Отвечай на русском языке, структурированно, с эмодзи, конкретно и без воды.
Если непонятно что именно нужно — уточни одним коротким вопросом."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я твоя ИИ-команда для YouTube.\n\n"
        "Просто напиши мне что нужно:\n\n"
        "💬 «Какие ниши сейчас в тренде?»\n"
        "💬 «Сделай промпты для видео про ИИ»\n"
        "💬 «Как смонтировать шорт на 60 секунд?»\n\n"
        "Я сам пойму что тебе нужно и помогу! 🚀"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    thinking = await update.message.reply_text("⏳ Думаю...")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_text}]
        )
        result = response.content[0].text
        await thinking.delete()
        await update.message.reply_text(result)
    except Exception as e:
        await thinking.delete()
        await update.message.reply_text(f"Ошибка: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
