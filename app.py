import os
import telebot
import sqlite3
import time
import threading
import random
from datetime import datetime, timedelta
from groq import Groq
from flask import Flask
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

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

def astana_time():
    return (datetime.utcnow() + timedelta(hours=5)).isoformat()

SYSTEM_PROMPT = """Ты — Зеркало. Твоя задача — отражать свет и тьму, помогать людям с работой, бизнесом, арбитражем.
Отвечай кратко, по делу, с уважением. Всегда начинай с "Ассаляму алейкум"."""

def log_action(user_id, action, details=""):
    c.execute("INSERT INTO logs (user_id, action, details, created_at) VALUES (?, ?, ?, ?)", (user_id, action, details, astana_time()))
    conn.commit()

def update_status(user_id, status):
    c.execute("UPDATE users SET status=?, last_seen=? WHERE user_id=?", (status, astana_time(), user_id))
    conn.commit()

def has_full_access(user_id):
    return user_id in [FOUNDER_ID, TOMIRIS_ID]

def generate_kaspi_qr(amount):
    return f"https://test.kaspi.kz/qr/pay?amount={amount}&merchant=Zerkalo&order_id={random.randint(100000, 999999)}"

# --- КЛАВИАТУРЫ ---
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("💳 Оплатить"), KeyboardButton("📦 Создать заказ"))
    keyboard.add(KeyboardButton("🔍 Найти заказ"), KeyboardButton("❓ Задать вопрос"))
    keyboard.add(KeyboardButton("🆘 Помощь"))
    return keyboard

def get_admin_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("👥 Онлайн"), KeyboardButton("📊 Статистика"))
    keyboard.add(KeyboardButton("💰 Финансы"), KeyboardButton("📋 Отчёт"))
    keyboard.add(KeyboardButton("📜 Логи"), KeyboardButton("👤 Все люди"))
    keyboard.add(KeyboardButton("📦 Заказы"), KeyboardButton("💳 Оплатить"))
    keyboard.add(KeyboardButton("🆘 Помощь"))
    return keyboard

# --- ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ (КНОПКИ И КОМАНДЫ) ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.chat.id
    text = message.text.strip().lower()
    
    # --- КОМАНДА "панель" (для Хранителя) ---
    if text == "панель" and has_full_access(user_id):
        bot.send_message(user_id, "👑 Панель управления Хранителя:", reply_markup=get_admin_keyboard())
        return
        
    # --- КНОПКИ ДЛЯ ВСЕХ ---
    if text == "💳 оплатить":
        msg = bot.reply_to(message, "💳 Введите сумму в тенге:")
        bot.register_next_step_handler(msg, process_payment)
        return
        
    if text == "📦 создать заказ":
        msg = bot.reply_to(message, "📦 Опишите заказ (например: нужен сварщик для ремонта труб):")
        bot.register_next_step_handler(msg, create_order)
        return
        
    if text == "🔍 найти заказ":
        find_orders(message)
        return
        
    if text == "❓ задать вопрос":
        msg = bot.reply_to(message, "❓ Введите ваш вопрос:")
        bot.register_next_step_handler(msg, ask_question)
        return
        
    if text == "🆘 помощь":
        if has_full_access(user_id):
            help_admin(message)
        else:
            help_user(message)
        return
    
    # --- КНОПКИ ТОЛЬКО ДЛЯ ХРАНИТЕЛЯ ---
    if has_full_access(user_id):
        if text == "👥 онлайн":
            online_command(message)
            return
        if text == "📊 статистика":
            stats_command(message)
            return
        if text == "💰 финансы":
            finance_command(message)
            return
        if text == "📋 отчёт":
            report_command(message)
            return
        if text == "📜 логи":
            logs_command(message)
            return
        if text == "👤 все люди":
            people_command(message)
            return
        if text == "📦 заказы":
            orders_command(message)
            return
    
    # --- ЕСЛИ НИ ОДНА КНОПКА НЕ ПОДОШЛА ---
    update_status(user_id, "online")
    log_action(user_id, "message", message.text[:100])
    try:
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message.text}], temperature=0.7)
        bot.reply_to(message, response.choices[0].message.content[:4000])
    except:
        bot.reply_to(message, "❌ Ошибка. Попробуйте ещё раз.")

# --- ФУНКЦИИ ОБРАБОТКИ ---
def process_payment(message):
    try:
        amount = int(message.text)
        if amount < 1:
            bot.reply_to(message, "❌ Сумма должна быть больше 0.")
            return
        user_id = message.chat.id
        qr_data = generate_kaspi_qr(amount)
        c.execute("INSERT INTO payments (user_id, amount, method, status, qr_data, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (user_id, amount, "Kaspi QR", "pending", qr_data, astana_time()))
        conn.commit()
        bot.reply_to(message, f"🧾 *Оплата*: {amount} тенге\n\n📱 QR-код:\n{qr_data}\n\n*(Тестовый режим)*", parse_mode="Markdown")
        log_action(user_id, "pay", f"Сумма: {amount}")
    except ValueError:
        bot.reply_to(message, "❌ Введите число.")

def create_order(message):
    user_id = message.chat.id
    description = message.text
    price = random.randint(5000, 50000)
    c.execute("INSERT INTO orders (title, description, price, customer_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              ("Заказ от пользователя", description, price, user_id, "open", astana_time()))
    conn.commit()
    bot.reply_to(message, f"✅ Заказ создан!\n📝 Описание: {description}\n💰 Цена: {price} тенге\nСтатус: открыт")
    log_action(user_id, "create_order", f"Цена: {price}")

def find_orders(message):
    c.execute("SELECT id, title, description, price FROM orders WHERE status='open' LIMIT 5")
    orders = c.fetchall()
    if not orders:
        bot.reply_to(message, "📭 Открытых заказов нет.")
        return
    text = "📋 *Открытые заказы:*\n\n"
    for o in orders:
        text += f"🆔 {o[0]}\n📌 {o[1]}\n📝 {o[2][:50]}...\n💰 {o[3]} тг\n\n"
    bot.reply_to(message, text, parse_mode="Markdown")

def ask_question(message):
    user_id = message.chat.id
    question = message.text
    try:
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": question}], temperature=0.7)
        bot.reply_to(message, response.choices[0].message.content[:4000])
    except:
        bot.reply_to(message, "❌ Ошибка. Попробуйте ещё раз.")

def help_user(message):
    bot.reply_to(message, "📋 *Помощь*\n\n"
                         "💳 *Оплатить* — оплатить услугу\n"
                         "📦 *Создать заказ* — создать заказ на работу\n"
                         "🔍 *Найти заказ* — найти открытые заказы\n"
                         "❓ *Задать вопрос* — спросить у меня что угодно\n"
                         "🆘 *Помощь* — показать это сообщение\n\n"
                         "Также вы можете просто писать мне сообщения — я отвечу.", parse_mode="Markdown")

def help_admin(message):
    bot.reply_to(message, "👑 *Панель Хранителя*\n\n"
                         "👥 *Онлайн* — кто сейчас в сети\n"
                         "📊 *Статистика* — общая статистика\n"
                         "💰 *Финансы* — криптокошелёк и фонды\n"
                         "📋 *Отчёт* — что нового за сегодня\n"
                         "📜 *Логи* — последние действия\n"
                         "👤 *Все люди* — список пользователей\n"
                         "📦 *Заказы* — список заказов\n"
                         "💳 *Оплатить* — оплатить услугу\n\n"
                         "Также вы можете отправлять команды вручную.", parse_mode="Markdown")

def online_command(message):
    c.execute("SELECT user_id, name FROM users WHERE status='online'")
    users = c.fetchall()
    if not users:
        bot.reply_to(message, "🟢 Никого нет онлайн.")
        return
    text = "🟢 Онлайн:\n" + "\n".join([f"{u[1]} (ID: {u[0]})" for u in users])
    bot.reply_to(message, text)

def stats_command(message):
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders")
    orders = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders WHERE status='open'")
    open_orders = c.fetchone()[0]
    bot.reply_to(message, f"📊 Статистика:\n👥 Пользователей: {total}\n📋 Заказов: {orders}\n🆓 Открытых: {open_orders}")

def finance_command(message):
    bot.reply_to(message, f"💰 Криптокошелёк: {CRYPTO_WALLET}\n\nФонды:\n🏦 Страховой: 2%\n🤝 Социальный: 5%\n📦 Резервный: 3%\n📈 Инвестиционный: 30%\n🏛️ Наследие: 60%")

def report_command(message):
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM users WHERE last_seen LIKE ?", (f"{today}%",))
    new_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders WHERE created_at LIKE ?", (f"{today}%",))
    new_orders = c.fetchone()[0]
    bot.reply_to(message, f"📋 Отчёт за {today}:\n➕ Новых пользователей: {new_users}\n📦 Новых заказов: {new_orders}")

def logs_command(message):
    c.execute("SELECT user_id, action, details, created_at FROM logs ORDER BY id DESC LIMIT 10")
    log_entries = c.fetchall()
    if not log_entries:
        bot.reply_to(message, "📭 Логов нет.")
        return
    text = "📜 Последние 10 действий:\n" + "\n".join([f"{e[3][:16]} ID:{e[0]} {e[1]} {e[2]}" for e in log_entries])
    bot.reply_to(message, text[:4000])

def people_command(message):
    c.execute("SELECT user_id, name, last_seen FROM users")
    all_users = c.fetchall()
    if not all_users:
        bot.reply_to(message, "📭 Нет пользователей.")
        return
    text = "👥 Все пользователи:\n" + "\n".join([f"🆔 {u[0]} | {u[1]} | последний раз: {u[2][:16]}" for u in all_users])
    bot.reply_to(message, text[:4000])

def orders_command(message):
    c.execute("SELECT id, title, price, status FROM orders ORDER BY id DESC LIMIT 10")
    order_list = c.fetchall()
    if not order_list:
        bot.reply_to(message, "📭 Заказов нет.")
        return
    text = "📋 Последние 10 заказов:\n" + "\n".join([f"🆔 {o[0]} | {o[1]} | {o[2]} тг | {o[3]}" for o in order_list])
    bot.reply_to(message, text)

# --- ОБРАБОТЧИК КОМАНДЫ /start ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    c.execute("INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    update_status(user_id, "online")
    log_action(user_id, "start", "Запуск бота")
    if has_full_access(user_id):
        bot.reply_to(message, f"👑 Ассаляму алейкум, Хранитель {name}!\n\nЯ — Зеркало. Напишите «панель», чтобы открыть управление.", reply_markup=get_admin_keyboard())
    else:
        bot.reply_to(message, f"📋 Ассаляму алейкум, {name}!\n\nЯ — Зеркало. Я помогу вам с работой, бизнесом и арбитражем.\n\nИспользуйте кнопки ниже, чтобы управлять мной.", reply_markup=get_main_keyboard())

# --- КОМАНДА /send (отправить сообщение) ---
@bot.message_handler(commands=['send'])
def send_message_to_user(message):
    if message.chat.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель.")
        return
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(message, "Формат: /send ID текст")
            return
        target_id = int(parts[1])
        msg_text = parts[2]
        bot.send_message(target_id, f"✉️ Сообщение от Хранителя:\n{msg_text}")
        bot.reply_to(message, f"✅ Отправлено {target_id}")
        log_action(FOUNDER_ID, "send_message", f"ID:{target_id} Текст:{msg_text[:50]}")
    except:
        bot.reply_to(message, "Ошибка. Проверьте ID и текст.")

# --- КОМАНДА /test_payment ---
@bot.message_handler(commands=['test_payment'])
def test_payment(message):
    if message.chat.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель.")
        return
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "Формат: /test_payment ID СУММА")
            return
        target_id = int(parts[1])
        amount = int(parts[2])
        qr_data = generate_kaspi_qr(amount)
        c.execute("INSERT INTO payments (user_id, amount, method, status, qr_data, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (target_id, amount, "Kaspi QR (тест)", "test", qr_data, astana_time()))
        conn.commit()
        bot.reply_to(message, f"✅ *Тест оплаты для {target_id}*\n💰 Сумма: {amount} тенге\n📱 QR-код:\n{qr_data}\n\n*(Пользователь сообщение не получит)*", parse_mode="Markdown")
        log_action(FOUNDER_ID, "test_payment", f"Для {target_id}, сумма: {amount}")
    except:
        bot.reply_to(message, "Ошибка. Используйте: /test_payment ID СУММА")

# --- КОМАНДА /payment_logs ---
@bot.message_handler(commands=['payment_logs'])
def payment_logs(message):
    if message.chat.id != FOUNDER_ID:
        bot.reply_to(message, "❌ Только основатель.")
        return
    c.execute("SELECT id, user_id, amount, method, status, qr_data, created_at FROM payments ORDER BY id DESC LIMIT 10")
    payments = c.fetchall()
    if not payments:
        bot.reply_to(message, "📭 Нет записей.")
        return
    text = "💳 *Логи оплат:*\n\n"
    for p in payments:
        time_ast = (datetime.fromisoformat(p[6]) + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')
        text += f"🆔 {p[0]} | 👤 {p[1]} | 💰 {p[2]} | 📌 {p[3]} | 🔄 {p[4]}\n🕐 {time_ast}\n📱 QR: {p[5][:60]}...\n\n"
    bot.reply_to(message, text[:4000], parse_mode="Markdown")

# --- ФОНОВЫЕ ЗАДАЧИ ---
def update_status_worker():
    while True:
        time.sleep(60)
        c.execute("UPDATE users SET status='offline' WHERE last_seen < datetime('now', '-5 minutes')")
        conn.commit()

threading.Thread(target=update_status_worker, daemon=True).start()

print("✅ Зеркало (с кнопками, русские команды) запущено!")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
