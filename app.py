import os
import telebot
import sqlite3
import time
import threading
import random
from datetime import datetime
from groq import Groq
from flask import Flask

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Зеркало работает!", 200

def run_flask():
    app_flask.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY)

conn = sqlite3.connect('zerkalo.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, phone TEXT, role TEXT DEFAULT 'user', status TEXT DEFAULT 'offline', last_seen TEXT, is_tomiris INTEGER DEFAULT 0, rating REAL DEFAULT 0, balance INTEGER DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, price INTEGER, customer_id INTEGER, executor_id INTEGER DEFAULT 0, status TEXT DEFAULT 'open', created_at TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, action TEXT, details TEXT, created_at TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount INTEGER, method TEXT, status TEXT, qr_data TEXT, created_at TEXT)''')
conn.commit()

FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814
CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"

SYSTEM_PROMPT = """Ты — Зеркало. Твоя задача — отражать свет и тьму, помогать людям с работой, бизнесом, арбитражем.
Твои принципы: жизнь священна, справедливость абсолютна, проценты запрещены.
Запрещены: алкоголь, азарт, свинина, порнография.
Отвечай кратко, по делу, с уважением. Всегда начинай с приветствия "Ассаляму алейкум"."""

def log_action(user_id, action, details=""):
    c.execute("INSERT INTO logs (user_id, action, details, created_at) VALUES (?, ?, ?, ?)", (user_id, action, details, datetime.now().isoformat()))
    conn.commit()

def update_status(user_id, status):
    c.execute("UPDATE users SET status=?, last_seen=? WHERE user_id=?", (status, datetime.now().isoformat(), user_id))
    conn.commit()

def has_full_access(user_id):
    return user_id in [FOUNDER_ID, TOMIRIS_ID]

def generate_kaspi_qr(amount, description="Оплата услуг Зеркала"):
    """Генерирует тестовую ссылку на Kaspi QR"""
    return f"https://test.kaspi.kz/qr/pay?amount={amount}&merchant=Zerkalo&description={description}&order_id={random.randint(100000, 999999)}"

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    c.execute("INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    update_status(user_id, "online")
    log_action(user_id, "start", "Запуск бота")
    if has_full_access(user_id):
        menu = ("👑 Хранитель. Полный доступ.\n\n"
                "📊 Управление:\n"
                "/online — кто онлайн\n"
                "/stats — статистика\n"
                "/logs — логи\n"
                "/orders — заказы\n"
                "/finance — финансы\n"
                "/send — отправить сообщение\n"
                "/people — все люди\n"
                "/history — история диалога\n\n"
                "💳 Оплата и тестирование:\n"
                "/pay — оплатить (как пользователь)\n"
                "/test_payment ID СУММА — тест оплаты за пользователя\n"
                "/payment_logs — логи всех оплат\n\n"
                "⚙️ Другое:\n"
                "/channels — каналы\n"
                "/balance — фонды\n"
                "/business — бизнес\n"
                "/report — отчёт\n"
                "/help — помощь")
    else:
        menu = ("📋 Главное меню\n\n"
                "/channels — каналы\n"
                "/become_customer — стать заказчиком\n"
                "/become_executor — стать исполнителем\n"
                "/pay — оплатить услугу\n"
                "/help — помощь")
    bot.reply_to(message, f"Ассаляму алейкум, {name}!\n\n{menu}")

# --- ОПЛАТА (для обычного пользователя) ---
@bot.message_handler(commands=['pay'])
def pay_command(message):
    msg = bot.reply_to(message, "💳 *Оплата услуги*\n\nВведите сумму в тенге (например, 1000):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_payment)

def process_payment(message):
    try:
        amount = int(message.text)
        if amount < 1:
            bot.reply_to(message, "Сумма должна быть больше 0.")
            return
        user_id = message.chat.id
        # Генерируем QR
        qr_data = generate_kaspi_qr(amount)
        # Сохраняем в базу
        c.execute("INSERT INTO payments (user_id, amount, method, status, qr_data, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (user_id, amount, "Kaspi QR", "pending", qr_data, datetime.now().isoformat()))
        conn.commit()
        # Отправляем пользователю
        bot.reply_to(message, f"🧾 *Оплата*: {amount} тенге\n\n"
                             f"📱 Отсканируйте QR-код в приложении Kaspi:\n{qr_data}\n\n"
                             f"*(Это тестовый режим. Реальная оплата появится после подключения Kaspi API.)*",
                             parse_mode="Markdown")
        log_action(user_id, "pay", f"Сумма: {amount} тенге, QR: {qr_data}")
    except ValueError:
        bot.reply_to(message, "Пожалуйста, введите число.")

# --- ТЕСТОВАЯ ОПЛАТА ЗА ЛЮБОГО ПОЛЬЗОВАТЕЛЯ (только для Хранителя) ---
@bot.message_handler(commands=['test_payment'])
def test_payment(message):
    if message.chat.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель.")
        return
    try:
        parts = message.text.split()
        target_id = int(parts[1])
        amount = int(parts[2])
        qr_data = generate_kaspi_qr(amount)
        c.execute("INSERT INTO payments (user_id, amount, method, status, qr_data, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (target_id, amount, "Kaspi QR (тест)", "test", qr_data, datetime.now().isoformat()))
        conn.commit()
        bot.reply_to(message, f"✅ *Тестовая оплата для пользователя {target_id}*\n\n"
                             f"💰 Сумма: {amount} тенге\n"
                             f"📱 QR-код:\n{qr_data}\n\n"
                             f"Пользователь получил бы такое сообщение.", parse_mode="Markdown")
        log_action(FOUNDER_ID, "test_payment", f"Для {target_id}, сумма: {amount}")
    except:
        bot.reply_to(message, "❌ Формат: /test_payment ID СУММА")

# --- ЛОГИ ВСЕХ ОПЛАТ (только для Хранителя) ---
@bot.message_handler(commands=['payment_logs'])
def payment_logs(message):
    if message.chat.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель.")
        return
    c.execute("SELECT id, user_id, amount, method, status, qr_data, created_at FROM payments ORDER BY id DESC LIMIT 15")
    payments = c.fetchall()
    if not payments:
        bot.reply_to(message, "📭 Нет записей об оплатах.")
        return
    text = "💳 *Логи оплат (последние 15):*\n\n"
    for p in payments:
        text += f"🆔 {p[0]} | 👤 {p[1]} | 💰 {p[2]} | 📌 {p[3]} | 🔄 {p[4]}\n🕐 {p[6][:16]}\n📱 QR: {p[5][:60]}...\n\n"
    bot.reply_to(message, text[:4000], parse_mode="Markdown")

# --- ОСТАЛЬНЫЕ КОМАНДЫ (сжато, но все важные есть) ---
@bot.message_handler(commands=['online'])
def online(message):
    if not has_full_access(message.chat.id):
        bot.reply_to(message, "❌ Только Хранитель.")
        return
    c.execute("SELECT user_id, name FROM users WHERE status='online'")
    users = c.fetchall()
    bot.reply_to(message, "🟢 Онлайн:\n" + "\n".join([f"{u[1]} (ID: {u[0]})" for u in users]) if users else "🟢 Никого нет.")

@bot.message_handler(commands=['stats'])
def stats(message):
    if not has_full_access(message.chat.id):
        bot.reply_to(message, "❌ Только Хранитель.")
        return
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders")
    orders = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders WHERE status='open'")
    open_orders = c.fetchone()[0]
    bot.reply_to(message, f"📊 Пользователей: {total}\n📋 Заказов: {orders}\n🆓 Открытых: {open_orders}")

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
    bot.reply_to(message, f"💰 Криптокошелёк: {CRYPTO_WALLET}\nФонды: 2/5/3/30/60")

@bot.message_handler(commands=['send'])
def send_message_to_user(message):
    if message.chat.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель.")
        return
    try:
        parts = message.text.split(maxsplit=2)
        target_id = int(parts[1])
        msg_text = parts[2]
        bot.send_message(target_id, f"✉️ Сообщение от Хранителя:\n{msg_text}")
        bot.reply_to(message, f"✅ Отправлено {target_id}")
    except:
        bot.reply_to(message, "Формат: /send ID текст")

@bot.message_handler(commands=['people'])
def people(message):
    if message.chat.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель.")
        return
    c.execute("SELECT user_id, name, last_seen FROM users")
    all_users = c.fetchall()
    if not all_users:
        bot.reply_to(message, "📭 Нет пользователей.")
        return
    text = "👥 Все пользователи:\n" + "\n".join([f"🆔 {u[0]} | {u[1]} | {u[2]}" for u in all_users])
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
            bot.reply_to(message, f"📭 Нет истории для {target_id}")
            return
        text = f"📜 История {target_id}:\n" + "\n".join([f"{e[3][:16]} | {e[1]} | {e[2]}" for e in user_logs])
        bot.reply_to(message, text[:4000])
    except:
        bot.reply_to(message, "Формат: /history ID")

@bot.message_handler(commands=['channels'])
def channels(message):
    bot.reply_to(message, "📢 8 каналов Зеркала будут созданы.")

@bot.message_handler(commands=['balance'])
def balance(message):
    if not has_full_access(message.chat.id):
        bot.reply_to(message, "❌ Только Хранитель.")
        return
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
    bot.reply_to(message, f"📋 Отчёт за {today}:\n➕ Новых: {new_users}\n📦 Заказов: {new_orders}")

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
    except:
        bot.reply_to(message, "❌ Ошибка. Формат: 'Название, БИН, Контакт, Телефон'")

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = message.chat.id
    if has_full_access(user_id):
        menu = "/online, /stats, /logs, /orders, /finance, /send, /people, /history, /pay, /test_payment, /payment_logs, /channels, /balance, /business, /report"
    else:
        menu = "/channels, /become_customer, /become_executor, /pay, /help"
    bot.reply_to(message, menu)

@bot.message_handler(func=lambda message: True)
def answer(message):
    user_id = message.chat.id
    update_status(user_id, "online")
    log_action(user_id, "message", message.text[:100])
    try:
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message.text}], temperature=0.7)
        bot.reply_to(message, response.choices[0].message.content[:4000])
    except:
        bot.reply_to(message, "Ошибка. Попробуйте ещё раз.")

def update_status_worker():
    while True:
        time.sleep(60)
        c.execute("UPDATE users SET status='offline' WHERE last_seen < datetime('now', '-5 minutes')")
        conn.commit()

threading.Thread(target=update_status_worker, daemon=True).start()

print("✅ Зеркало (полный контроль оплаты) запущено!")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
