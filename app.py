import os
import telebot
import time
import threading
from datetime import datetime
from groq import Groq
from flask import Flask

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Zerkalo is running!", 200

def run_flask():
    app_flask.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Ты — Зеркало. Отвечай кратко, по делу, с уважением. Всегда начинай с приветствия "Ассаляму алейкум"."""

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Ассаляму алейкум! Я — Зеркало. Бот работает на Render 24/7!")

@bot.message_handler(func=lambda message: True)
def answer(message):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": message.text}],
            temperature=0.7
        )
        bot.reply_to(message, response.choices[0].message.content[:4000])
    except Exception as e:
        bot.reply_to(message, "Ошибка. Попробуйте ещё раз.")

print("✅ Зеркало (финальная версия) запущено!")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
