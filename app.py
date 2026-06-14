import os
import threading
import telebot
import sqlite3
import time
from datetime import datetime
from groq import Groq
from flask import Flask

# --- Заглушка для Render ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Зеркало работает!", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- Основной код бота ---
TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Ассаляму алейкум! Я — Зеркало. Бот работает на Render 24/7!")

@bot.message_handler(func=lambda message: True)
def answer(message):
    user_text = message.text
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Ты — Зеркало. Отвечай кратко, по делу."},
                      {"role": "user", "content": user_text}],
            temperature=0.7
        )
        bot.reply_to(message, response.choices[0].message.content[:4000])
    except Exception as e:
        bot.reply_to(message, "Ошибка. Попробуйте ещё раз.")

print("✅ Зеркало запущено!")

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    bot.infinity_polling()
