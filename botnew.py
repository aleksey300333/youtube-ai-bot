import os
import time
import requests
import anthropic

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

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

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_message(chat_id, text):
    requests.post(f"{BASE_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def get_updates(offset=None):
    params = {"timeout": 30, "offset": offset}
    resp = requests.get(f"{BASE_URL}/getUpdates", params=params)
    return resp.json().get("result", [])

def ask_claude(text):
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}]
    )
    return response.content[0].text

def main():
    print("Бот запущен!")
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text", "")
                if not chat_id or not text:
                    continue
                if text == "/start":
                    send_message(chat_id,
                        "👋 Привет! Я твоя ИИ-команда для YouTube.\n\n"
                        "Просто напиши мне что нужно:\n\n"
                        "💬 «Какие ниши сейчас в тренде?»\n"
                        "💬 «Сделай промпты для видео про ИИ»\n"
                        "💬 «Как смонтировать шорт на 60 секунд?»\n\n"
                        "Я сам пойму что тебе нужно и помогу! 🚀"
                    )
                else:
                    send_message(chat_id, "⏳ Думаю...")
                    reply = ask_claude(text)
                    send_message(chat_id, reply)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
