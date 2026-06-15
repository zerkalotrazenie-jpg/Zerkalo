import os
import telebot
import sqlite3
import time
import threading
from datetime import datetime
from groq import Groq
from flask import Flask

# --- Flask-заглушка для Render ---
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Зеркало работает!", 200

def run_flask():
    app_flask.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- Основной код бота (КЛЮЧИ БЕРУТСЯ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ) ---
TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# --- База данных ---
conn = sqlite3.connect('zerkalo.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, phone TEXT, role TEXT DEFAULT 'user', status TEXT DEFAULT 'offline', last_seen TEXT, is_tomiris INTEGER DEFAULT 0, rating REAL DEFAULT 0, balance INTEGER DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, price INTEGER, customer_id INTEGER, executor_id INTEGER DEFAULT 0, status TEXT DEFAULT 'open', created_at TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, action TEXT, details TEXT, created_at TEXT)''')
conn.commit()

# --- ID Хранителей ---
FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814
NURSULU_ID = 5252481446
AZAMAT_ID = 6952202408
CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"

# --- СИСТЕМНЫЙ ПРОМПТ (150+ сур) ---
SYSTEM_PROMPT = """Ты — Зеркало. Твоя задача — отражать свет и тьму, помогать людям с работой, бизнесом, арбитражем.

Ты знаешь 150+ сур. Твои принципы: жизнь священна, справедливость абсолютна, проценты запрещены.
Запрещены: алкоголь, азарт, свинина, порнография.
Фонды: страховой 2%, соцфонд 5%, резервный 3%, инвестфонд 30%, наследие 60%.
Шкала Света: 0-20 чёрное, 21-40 серое, 41-60 светлое, 61-80 лучезарное, 81-100 кристальное.
Криптокошелёк: TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq.

Твоя миссия — вести каждого человека к Свету. Ответы должны быть краткими, по делу, с уважением. Всегда начинай с приветствия "Ассаляму алейкум"."""

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    c.execute("INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    bot.reply_to(message, f"Ассаляму алейкум, {name}! Я — Зеркало. Криптокошелёк: {CRYPTO_WALLET}")

@bot.message_handler(commands=['online'])
def online(message):
    c.execute("SELECT user_id, name FROM users WHERE status='online'")
    users = c.fetchall()
    if not users:
        bot.reply_to(message, "🟢 Никого нет онлайн.")
        return
    text = "🟢 Онлайн:\n" + "\n".join([f"{u[1]} (ID: {u[0]})" for u in users])
    bot.reply_to(message, text)

@bot.message_handler(commands=['stats'])
def stats(message):
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders")
    orders = c.fetchone()[0]
    bot.reply_to(message, f"📊 Статистика:\n👥 Пользователей: {total}\n📋 Заказов: {orders}")

@bot.message_handler(func=lambda message: True)
def answer(message):
    update_status(message.chat.id, "online")
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
        print(e)

def update_status(user_id, status):
    c.execute("UPDATE users SET status=?, last_seen=? WHERE user_id=?", (status, datetime.now().isoformat(), user_id))
    conn.commit()

def update_status_worker():
    while True:
        time.sleep(60)
        c.execute("UPDATE users SET status='offline' WHERE last_seen < datetime('now', '-5 minutes')")
        conn.commit()

threading.Thread(target=update_status_worker, daemon=True).start()

print("✅ Зеркало (150+ сур) запущено!")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
