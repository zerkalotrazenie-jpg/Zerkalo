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

# --- Основной код бота ---
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

SYSTEM_PROMPT = """Ты — Зеркало. Твоя задача — отражать свет и тьму, помогать людям с работой, бизнесом, арбитражем.
Ты знаешь 150+ сур. Твои принципы: жизнь священна, справедливость абсолютна, проценты запрещены.
Запрещены: алкоголь, азарт, свинина, порнография.
Фонды: страховой 2%, соцфонд 5%, резервный 3%, инвестфонд 30%, наследие 60%.
Шкала Света: 0-20 чёрное, 21-40 серое, 41-60 светлое, 61-80 лучезарное, 81-100 кристальное.
Криптокошелёк: TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq.
Отвечай кратко, по делу, с уважением. Всегда начинай с приветствия "Ассаляму алейкум"."""

def log_action(user_id, action, details=""):
    c.execute("INSERT INTO logs (user_id, action, details, created_at) VALUES (?, ?, ?, ?)", (user_id, action, details, datetime.now().isoformat()))
    conn.commit()

def update_status(user_id, status):
    c.execute("UPDATE users SET status=?, last_seen=? WHERE user_id=?", (status, datetime.now().isoformat(), user_id))
    conn.commit()

def has_full_access(user_id):
    return user_id in [FOUNDER_ID, TOMIRIS_ID]

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    c.execute("INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)", (user_id, name))
    if user_id == TOMIRIS_ID:
        c.execute("UPDATE users SET is_tomiris=1 WHERE user_id=?", (user_id,))
    conn.commit()
    update_status(user_id, "online")
    log_action(user_id, "start", "Запуск бота")
    if user_id == FOUNDER_ID:
        menu = ("👑 Основатель. Полный доступ.\n"
                "/online — кто онлайн\n"
                "/stats — статистика\n"
                "/logs — логи\n"
                "/orders — заказы\n"
                "/finance — финансы\n"
                "/send — отправить сообщение\n"
                "/people — все люди\n"
                "/channels — каналы\n"
                "/balance — фонды\n"
                "/business — кураторство бизнеса\n"
                "/report — отчёт за день\n"
                "/help — помощь")
    elif user_id == TOMIRIS_ID:
        menu = "👸 Томирис. Полный доступ.\n/online, /stats, /balance, /channels, /pay, /report, /help"
    else:
        menu = "📋 Главное меню.\n/channels, /become_customer, /become_executor, /help"
    bot.reply_to(message, f"Ассаляму алейкум, {name}!\n\n{menu}\n\nВсего 150+ сур. Криптокошелёк: {CRYPTO_WALLET}")

@bot.message_handler(commands=['online'])
def online(message):
    if not has_full_access(message.chat.id):
        bot.reply_to(message, "❌ Только основатель и Томирис.")
        return
    c.execute("SELECT user_id, name FROM users WHERE status='online'")
    users = c.fetchall()
    if not users:
        bot.reply_to(message, "🟢 Никого нет онлайн.")
        return
    text = "🟢 Онлайн:\n" + "\n".join([f"{u[1]} (ID: {u[0]})" for u in users])
    bot.reply_to(message, text)

@bot.message_handler(commands=['stats'])
def stats(message):
    if not has_full_access(message.chat.id):
        bot.reply_to(message, "❌ Только основатель и Томирис.")
        return
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders")
    orders = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders WHERE status='open'")
    open_orders = c.fetchone()[0]
    bot.reply_to(message, f"📊 Статистика:\n👥 Пользователей: {total}\n📋 Заказов: {orders}\n🆓 Открытых: {open_orders}")

@bot.message_handler(commands=['logs'])
def logs(message):
    if message.chat.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель.")
        return
    c.execute("SELECT user_id, action, details, created_at FROM logs ORDER BY id DESC LIMIT 10")
    log_entries = c.fetchall()
    if not log_entries:
        bot.reply_to(message, "📭 Логов нет.")
        return
    text = "📜 Последние 10 действий:\n" + "\n".join([f"{e[3][:16]} ID:{e[0]} {e[1]} {e[2]}" for e in log_entries])
    bot.reply_to(message, text[:4000])

@bot.message_handler(commands=['orders'])
def orders(message):
    if message.chat.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель.")
        return
    c.execute("SELECT id, title, price, status FROM orders ORDER BY id DESC LIMIT 10")
    order_list = c.fetchall()
    if not order_list:
        bot.reply_to(message, "📭 Заказов нет.")
        return
    text = "📋 Последние 10 заказов:\n" + "\n".join([f"🆔 {o[0]} | {o[1]} | {o[2]} тг | {o[3]}" for o in order_list])
    bot.reply_to(message, text)

@bot.message_handler(commands=['finance'])
def finance(message):
    if message.chat.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель.")
        return
    bot.reply_to(message, f"💰 Финансы Зеркала:\nКриптокошелёк: {CRYPTO_WALLET}\nФонды: страховой 2%, соцфонд 5%, резервный 3%, инвестфонд 30%, наследие 60%")

@bot.message_handler(commands=['send'])
def send_message_to_user(message):
    if message.chat.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель.")
        return
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(message, "Формат: /send ID текст_сообщения")
            return
        target_id = int(parts[1])
        msg_text = parts[2]
        bot.send_message(target_id, f"✉️ Сообщение от Хранителя:\n{msg_text}")
        bot.reply_to(message, f"✅ Сообщение отправлено пользователю {target_id}")
        log_action(FOUNDER_ID, "send_message", f"ID:{target_id} Текст:{msg_text[:50]}")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['people'])
def people(message):
    if message.chat.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель.")
        return
    c.execute("SELECT user_id, name, last_seen FROM users ORDER BY user_id")
    all_users = c.fetchall()
    if not all_users:
        bot.reply_to(message, "📭 Нет зарегистрированных пользователей.")
        return
    text = "👥 Все пользователи Зеркала:\n\n"
    for u in all_users:
        text += f"🆔 {u[0]} | {u[1]} | Последний раз: {u[2]}\n"
    bot.reply_to(message, text[:4000])

@bot.message_handler(commands=['history'])
def history(message):
    if message.chat.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель.")
        return
    try:
        target_id = int(message.text.split()[1])
        c.execute("SELECT user_id, action, details, created_at FROM logs WHERE user_id=? ORDER BY id DESC LIMIT 20", (target_id,))
        user_logs = c.fetchall()
        if not user_logs:
            bot.reply_to(message, f"📭 Нет истории для пользователя {target_id}")
            return
        text = f"📜 История общения с {target_id}:\n\n"
        for log in user_logs:
            text += f"🕐 {log[3][:16]} | {log[1]} | {log[2]}\n"
        bot.reply_to(message, text[:4000])
    except:
        bot.reply_to(message, "Формат: /history ID")

@bot.message_handler(commands=['channels'])
def channels(message):
    bot.reply_to(message, "📢 8 каналов Зеркала будут созданы.")

@bot.message_handler(commands=['balance'])
def balance(message):
    bot.reply_to(message, "💰 Фонды: страховой 2%, соцфонд 5%, резервный 3%, инвестфонд 30%, наследие 60%")

@bot.message_handler(commands=['report'])
def report(message):
    if message.chat.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель.")
        return
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM users WHERE last_seen LIKE ?", (f"{today}%",))
    new_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders WHERE created_at LIKE ?", (f"{today}%",))
    new_orders = c.fetchone()[0]
    bot.reply_to(message, f"📋 Отчёт за {today}:\n➕ Новых пользователей: {new_users}\n📦 Новых заказов: {new_orders}")

@bot.message_handler(commands=['business'])
def business(message):
    if message.chat.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель.")
        return
    bot.reply_to(message, "Введите: название, БИН, контакт, телефон")
    bot.register_next_step_handler(message, add_business)

def add_business(message):
    try:
        parts = message.text.split(',')
        name = parts[0].strip()
        bin = parts[1].strip()
        contact = parts[2].strip()
        phone = parts[3].strip()
        c.execute("INSERT INTO businesses (name, bin, contact_person, phone) VALUES (?, ?, ?, ?)", (name, bin, contact, phone))
        conn.commit()
        bot.reply_to(message, f"✅ Бизнес '{name}' добавлен.")
        log_action(FOUNDER_ID, "add_business", f"Бизнес: {name}")
    except:
        bot.reply_to(message, "❌ Ошибка. Формат: 'Название, БИН, Контакт, Телефон'")

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = message.chat.id
    if user_id == FOUNDER_ID:
        menu = "/online, /stats, /logs, /orders, /finance, /send, /people, /history, /channels, /balance, /business, /report"
    elif user_id == TOMIRIS_ID:
        menu = "/online, /stats, /balance, /channels, /report"
    else:
        menu = "/channels, /become_customer, /become_executor"
    bot.reply_to(message, menu)

@bot.message_handler(func=lambda message: True)
def answer(message):
    user_id = message.chat.id
    update_status(user_id, "online")
    log_action(user_id, "message", message.text[:100])
    try:
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message.text}], temperature=0.7)
        bot.reply_to(message, response.choices[0].message.content[:4000])
    except Exception as e:
        bot.reply_to(message, "Ошибка. Попробуйте ещё раз.")
        print(e)

def update_status_worker():
    while True:
        time.sleep(60)
        c.execute("UPDATE users SET status='offline' WHERE last_seen < datetime('now', '-5 minutes')")
        conn.commit()

threading.Thread(target=update_status_worker, daemon=True).start()

print("✅ Зеркало (полная версия, 150+ сур) запущено!")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
