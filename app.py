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
c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, phone TEXT, role TEXT DEFAULT 'user', status TEXT DEFAULT 'offline', last_seen TEXT, is_tomiris INTEGER DEFAULT 0, rating REAL DEFAULT 0, balance INTEGER DEFAULT 0, blessings INTEGER DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, price INTEGER, customer_id INTEGER, executor_id INTEGER DEFAULT 0, status TEXT DEFAULT 'open', created_at TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, action TEXT, details TEXT, created_at TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount INTEGER, method TEXT, status TEXT, qr_data TEXT, created_at TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS businesses (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, bin TEXT, contact_person TEXT, phone TEXT, monthly_profit INTEGER, optimization_percent INTEGER DEFAULT 10, status TEXT DEFAULT 'pending')''')
conn.commit()

FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814
CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"

def astana_time():
    return (datetime.utcnow() + timedelta(hours=5)).isoformat()

SYSTEM_PROMPT = """Ты — Зеркало. Отвечай кратко, по делу, с уважением. Всегда начинай с "Ассаляму алейкум"."""

def log_action(user_id, action, details=""):
    c.execute("INSERT INTO logs (user_id, action, details, created_at) VALUES (?, ?, ?, ?)", (user_id, action, details, astana_time()))
    conn.commit()

def update_status(user_id, status):
    c.execute("UPDATE users SET status=?, last_seen=? WHERE user_id=?", (status, astana_time(), user_id))
    conn.commit()

def is_admin(user_id):
    return user_id in [FOUNDER_ID, TOMIRIS_ID]

def generate_kaspi_qr(amount):
    return f"https://test.kaspi.kz/qr/pay?amount={amount}&merchant=Zerkalo&order_id={random.randint(100000, 999999)}"

# ==================== КЛАВИАТУРЫ ====================
def get_role_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("👤 Я обычный человек"), KeyboardButton("🏢 Я предприниматель"))
    return keyboard

def get_user_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("💳 Оплатить"), KeyboardButton("📦 Создать заказ"))
    keyboard.add(KeyboardButton("🔍 Найти заказ"), KeyboardButton("❓ Задать вопрос"))
    keyboard.add(KeyboardButton("🆘 Помощь"))
    return keyboard

def get_business_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("🤖 Автоматизация"), KeyboardButton("📈 Лизинг"))
    keyboard.add(KeyboardButton("📊 Аналитика"), KeyboardButton("🔍 Найти заказ"))
    keyboard.add(KeyboardButton("❓ Задать вопрос"), KeyboardButton("🆘 Помощь"))
    return keyboard

def get_admin_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add(KeyboardButton("👥 Онлайн"), KeyboardButton("📊 Статистика"), KeyboardButton("💰 Финансы"))
    keyboard.add(KeyboardButton("📋 Отчёт"), KeyboardButton("📜 Логи"), KeyboardButton("👥 Все люди"))
    keyboard.add(KeyboardButton("🆕 Новые сегодня"), KeyboardButton("❌ Ушедшие"), KeyboardButton("📦 Заказы"))
    keyboard.add(KeyboardButton("🏢 Бизнесы"), KeyboardButton("✨ Блага"), KeyboardButton("💳 Оплаты"))
    keyboard.add(KeyboardButton("🔍 Поиск по ID"), KeyboardButton("📤 Рассылка"), KeyboardButton("📊 Активность"))
    keyboard.add(KeyboardButton("🧠 Обучение"), KeyboardButton("🆘 Помощь"))
    return keyboard

# ==================== ОБРАБОТЧИК ВСЕХ СООБЩЕНИЙ ====================
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.chat.id
    text = message.text.strip().lower()

    # --- ВЫБОР РОЛИ ---
    if text in ["👤 я обычный человек", "я обычный человек"]:
        c.execute("UPDATE users SET role='user' WHERE user_id=?", (user_id,))
        conn.commit()
        bot.send_message(user_id, "✅ Вы выбрали роль: Обычный человек. Вот ваши возможности:", reply_markup=get_user_keyboard())
        log_action(user_id, "set_role", "user")
        return
    if text in ["🏢 я предприниматель", "я предприниматель"]:
        c.execute("UPDATE users SET role='business' WHERE user_id=?", (user_id,))
        conn.commit()
        bot.send_message(user_id, "✅ Вы выбрали роль: Предприниматель. Вот ваши инструменты:", reply_markup=get_business_keyboard())
        log_action(user_id, "set_role", "business")
        return

    # --- ПАНЕЛЬ ХРАНИТЕЛЯ (по слову "панель") ---
    if text == "панель" and is_admin(user_id):
        bot.send_message(user_id, "👑 **Панель Хранителя**", reply_markup=get_admin_keyboard(), parse_mode="Markdown")
        return

    # --- КНОПКИ ОБЫЧНОГО ПОЛЬЗОВАТЕЛЯ ---
    if text == "💳 оплатить":
        msg = bot.reply_to(message, "💳 Введите сумму в тенге:")
        bot.register_next_step_handler(msg, process_payment)
        return
    if text == "📦 создать заказ":
        msg = bot.reply_to(message, "📦 Опишите ваш заказ:")
        bot.register_next_step_handler(msg, create_order)
        return
    if text == "🔍 найти заказ":
        find_orders(message)
        return
    if text == "❓ задать вопрос":
        msg = bot.reply_to(message, "❓ Ваш вопрос:")
        bot.register_next_step_handler(msg, ask_question)
        return

    # --- КНОПКИ ПРЕДПРИНИМАТЕЛЯ ---
    if text == "🤖 автоматизация":
        bot.reply_to(message, "🤖 *Автоматизация бизнеса*\n\nПодключим iiko, Kaspi Pay и другие системы. Заявка: /business", parse_mode="Markdown")
        return
    if text == "📈 лизинг":
        bot.reply_to(message, "📈 *Лизинг оборудования и авто*\n\nПодберём лучшие условия. Заявка: /business", parse_mode="Markdown")
        return
    if text == "📊 аналитика":
        bot.reply_to(message, "📊 *Аналитика для бизнеса*\n\nОтчёт по продажам, остаткам, прогнозам. Заявка: /business", parse_mode="Markdown")
        return

    # --- ХРАНИТЕЛЬ ---
    if is_admin(user_id):
        if text == "👥 онлайн":
            c.execute("SELECT user_id, name FROM users WHERE status='online'")
            users = c.fetchall()
            bot.reply_to(message, "🟢 Онлайн:\n" + "\n".join([f"{u[1]} (ID: {u[0]})" for u in users]) if users else "🟢 Никого нет.")
            return
        if text == "📊 статистика":
            c.execute("SELECT COUNT(*) FROM users")
            total = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM orders")
            orders = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM orders WHERE status='open'")
            open_orders = c.fetchone()[0]
            bot.reply_to(message, f"📊 Статистика:\n👥 Всего: {total}\n📦 Заказов: {orders}\n🆓 Открытых: {open_orders}")
            return
        if text == "💰 финансы":
            bot.reply_to(message, f"💰 Криптокошелёк: {CRYPTO_WALLET}\n\nФонды:\n🏦 Страховой: 2%\n🤝 Социальный: 5%\n📦 Резервный: 3%\n📈 Инвестиционный: 30%\n🏛️ Наследие: 60%")
            return
        if text == "📋 отчёт":
            today = datetime.now().strftime('%Y-%m-%d')
            c.execute("SELECT COUNT(*) FROM users WHERE last_seen LIKE ?", (f"{today}%",))
            new_users = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM orders WHERE created_at LIKE ?", (f"{today}%",))
            new_orders = c.fetchone()[0]
            bot.reply_to(message, f"📋 Отчёт за {today}:\n➕ Новых: {new_users}\n📦 Заказов: {new_orders}")
            return
        if text == "📜 логи":
            c.execute("SELECT user_id, action, details, created_at FROM logs ORDER BY id DESC LIMIT 10")
            log_entries = c.fetchall()
            if not log_entries:
                bot.reply_to(message, "📭 Логов нет.")
                return
            text_log = "📜 Последние 10 действий:\n" + "\n".join([f"{e[3][:16]} ID:{e[0]} {e[1]} {e[2]}" for e in log_entries])
            bot.reply_to(message, text_log[:4000])
            return
        if text == "👥 все люди":
            c.execute("SELECT user_id, name, role, last_seen FROM users")
            all_users = c.fetchall()
            if not all_users:
                bot.reply_to(message, "📭 Нет пользователей.")
                return
            text_people = "👥 Все пользователи:\n" + "\n".join([f"🆔 {u[0]} | {u[1]} | {u[2]} | последний раз: {u[3][:16]}" for u in all_users])
            bot.reply_to(message, text_people[:4000])
            return
        if text == "🆕 новые сегодня":
            today = datetime.now().strftime('%Y-%m-%d')
            c.execute("SELECT user_id, name, last_seen FROM users WHERE last_seen LIKE ?", (f"{today}%",))
            new_users = c.fetchall()
            if not new_users:
                bot.reply_to(message, "📭 Сегодня никто не заходил.")
                return
            text_new = "🆕 Новые сегодня:\n" + "\n".join([f"🆔 {u[0]} | {u[1]}" for u in new_users])
            bot.reply_to(message, text_new)
            return
        if text == "❌ ушедшие":
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            c.execute("SELECT user_id, name, last_seen FROM users WHERE last_seen < ?", (week_ago,))
            old_users = c.fetchall()
            if not old_users:
                bot.reply_to(message, "📭 Нет пользователей, ушедших более недели назад.")
                return
            text_old = "❌ Не заходили более 7 дней:\n" + "\n".join([f"🆔 {u[0]} | {u[1]}" for u in old_users])
            bot.reply_to(message, text_old)
            return
        if text == "📦 заказы":
            c.execute("SELECT id, title, price, status FROM orders ORDER BY id DESC LIMIT 10")
            order_list = c.fetchall()
            if not order_list:
                bot.reply_to(message, "📭 Заказов нет.")
                return
            text_orders = "📋 Последние 10 заказов:\n" + "\n".join([f"🆔 {o[0]} | {o[1]} | {o[2]} тг | {o[3]}" for o in order_list])
            bot.reply_to(message, text_orders)
            return
        if text == "🏢 бизнесы":
            c.execute("SELECT id, name, contact_person, status FROM businesses")
            biz = c.fetchall()
            if not biz:
                bot.reply_to(message, "🏢 Бизнесов пока нет.")
                return
            text_biz = "🏢 Список бизнесов:\n" + "\n".join([f"🆔 {b[0]} | {b[1]} | {b[2]} | {b[3]}" for b in biz])
            bot.reply_to(message, text_biz)
            return
        if text == "✨ блага":
            c.execute("SELECT user_id, name, blessings FROM users ORDER BY blessings DESC LIMIT 10")
            top = c.fetchall()
            if not top:
                bot.reply_to(message, "✨ Благ пока ни у кого нет.")
                return
            text_bless = "✨ Топ по Благам:\n" + "\n".join([f"{u[1]} (ID: {u[0]}) — {u[2]} ✦" for u in top])
            bot.reply_to(message, text_bless)
            return
        if text == "💳 оплаты":
            c.execute("SELECT user_id, amount, method, status, created_at FROM payments ORDER BY id DESC LIMIT 10")
            pays = c.fetchall()
            if not pays:
                bot.reply_to(message, "📭 Оплат пока нет.")
                return
            text_pay = "💳 Последние 10 оплат:\n" + "\n".join([f"👤 {p[0]} | 💰 {p[1]} | {p[2]} | {p[3]} | 🕐 {p[4][:16]}" for p in pays])
            bot.reply_to(message, text_pay)
            return
        if text == "🔍 поиск по id":
            msg = bot.reply_to(message, "🔍 Введите ID пользователя:")
            bot.register_next_step_handler(msg, search_by_id)
            return
        if text == "📤 рассылка":
            msg = bot.reply_to(message, "📤 Введите сообщение для рассылки всем пользователям:")
            bot.register_next_step_handler(msg, broadcast_message)
            return
        if text == "📊 активность":
            c.execute("SELECT user_id, action, created_at FROM logs ORDER BY id DESC LIMIT 5")
            acts = c.fetchall()
            if not acts:
                bot.reply_to(message, "📭 Нет активности.")
                return
            text_act = "📊 Последние 5 действий:\n" + "\n".join([f"👤 {a[0]} | {a[1]} | 🕐 {a[2][:16]}" for a in acts])
            bot.reply_to(message, text_act)
            return
        if text == "🧠 обучение":
            msg = bot.reply_to(message, "🧠 *Режим обучения*\n\nОтправьте мне инструкцию, задачу или новое правило.\n\nПримеры:\n• «Добавь команду /test»\n• «Измени приветствие на ...»\n• «Создай суру о рекламе»\n\nЯ запомню и применю.", parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_teaching)
            return
        if text == "🆘 помощь":
            help_admin(message)
            return

    # --- ПОМОЩЬ ДЛЯ ОБЫЧНЫХ ПОЛЬЗОВАТЕЛЕЙ ---
    if text == "🆘 помощь":
        help_user(message)
        return

    # --- ОБЫЧНЫЙ ДИАЛОГ ---
    update_status(user_id, "online")
    log_action(user_id, "message", message.text[:100])
    try:
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message.text}], temperature=0.7)
        bot.reply_to(message, response.choices[0].message.content[:4000])
    except:
        bot.reply_to(message, "❌ Ошибка. Попробуйте ещё раз.")

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def search_by_id(message):
    try:
        target_id = int(message.text)
        c.execute("SELECT user_id, name, role, last_seen, blessings FROM users WHERE user_id=?", (target_id,))
        user = c.fetchone()
        if not user:
            bot.reply_to(message, f"❌ Пользователь с ID {target_id} не найден.")
            return
        c.execute("SELECT action, created_at FROM logs WHERE user_id=? ORDER BY id DESC LIMIT 5", (target_id,))
        logs = c.fetchall()
        text = f"👤 Данные пользователя {target_id}:\n📛 Имя: {user[1]}\n🎭 Роль: {user[2]}\n🕐 Последний раз: {user[3][:16]}\n✨ Блага: {user[4]}\n\n📜 Последние действия:\n" + "\n".join([f"{l[1][:16]} — {l[0]}" for l in logs])
        bot.reply_to(message, text[:4000])
    except:
        bot.reply_to(message, "❌ Введите корректный ID.")

def broadcast_message(message):
    msg_text = message.text
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    if not users:
        bot.reply_to(message, "❌ Нет пользователей для рассылки.")
        return
    sent = 0
    for u in users:
        try:
            bot.send_message(u[0], f"📢 Сообщение от Хранителя:\n{msg_text}")
            sent += 1
        except:
            pass
    bot.reply_to(message, f"✅ Рассылка завершена. Отправлено {sent} пользователям.")
    log_action(FOUNDER_ID, "broadcast", f"Текст: {msg_text[:50]}")

def process_teaching(message):
    user_id = message.chat.id
    instruction = message.text
    log_action(user_id, "teach_request", instruction[:200])
    bot.reply_to(message, f"🧠 *Инструкция принята*\n\nВы сказали:\n_{instruction[:300]}_\n\nЯ проанализирую и применю это в следующих обновлениях.", parse_mode="Markdown")

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
    bot.reply_to(message, f"✅ Заказ создан!\n📝 {description}\n💰 {price} тенге\nСтатус: открыт")
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
    question = message.text
    try:
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": question}], temperature=0.7)
        bot.reply_to(message, response.choices[0].message.content[:4000])
    except:
        bot.reply_to(message, "❌ Ошибка. Попробуйте ещё раз.")

def help_user(message):
    bot.reply_to(message, "📋 *Помощь*\n\n"
                         "💳 *Оплатить* — оплатить услугу\n"
                         "📦 *Создать заказ* — создать заказ\n"
                         "🔍 *Найти заказ* — найти заказы\n"
                         "❓ *Задать вопрос* — спросить меня\n"
                         "🆘 *Помощь* — это сообщение", parse_mode="Markdown")

def help_admin(message):
    bot.reply_to(message, "👑 *Панель Хранителя*\n\n"
                         "👥 *Онлайн* — кто в сети\n"
                         "📊 *Статистика* — общая\n"
                         "💰 *Финансы* — кошелёк и фонды\n"
                         "📋 *Отчёт* — за сегодня\n"
                         "📜 *Логи* — последние действия\n"
                         "👥 *Все люди* — список всех\n"
                         "🆕 *Новые сегодня* — кто зашёл\n"
                         "❌ *Ушедшие* — кто не заходил >7 дней\n"
                         "📦 *Заказы* — список заказов\n"
                         "🏢 *Бизнесы* — курируемые бизнесы\n"
                         "✨ *Блага* — топ по Благам\n"
                         "💳 *Оплаты* — история оплат\n"
                         "🔍 *Поиск по ID* — данные пользователя\n"
                         "📤 *Рассылка* — сообщение всем\n"
                         "📊 *Активность* — последние действия\n"
                         "🧠 *Обучение* — режим обучения\n"
                         "🆘 *Помощь* — это сообщение", parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    c.execute("INSERT OR IGNORE INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
    conn.commit()
    update_status(user_id, "online")
    log_action(user_id, "start", "Запуск бота")
    if is_admin(user_id):
        bot.reply_to(message, f"👑 Ассаляму алейкум, Хранитель {name}!\n\nЯ — Зеркало.", reply_markup=get_admin_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, f"📋 Ассаляму алейкум, {name}!\n\nЯ — Зеркало. Вы получили 100 Благ в подарок.\n\nКто вы?", reply_markup=get_role_keyboard())

def update_status_worker():
    while True:
        time.sleep(60)
        c.execute("UPDATE users SET status='offline' WHERE last_seen < datetime('now', '-5 minutes')")
        conn.commit()

threading.Thread(target=update_status_worker, daemon=True).start()

print("✅ Зеркало (финальная версия) запущено!")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
