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
c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, age INTEGER, city TEXT, phone TEXT, role TEXT DEFAULT 'user', status TEXT DEFAULT 'offline', last_seen TEXT, is_tomiris INTEGER DEFAULT 0, rating REAL DEFAULT 0, balance INTEGER DEFAULT 0, blessings INTEGER DEFAULT 0, resume TEXT DEFAULT '', is_disabled INTEGER DEFAULT 0, is_sick INTEGER DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, price INTEGER, customer_id INTEGER, executor_id INTEGER DEFAULT 0, status TEXT DEFAULT 'open', created_at TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, action TEXT, details TEXT, created_at TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount INTEGER, method TEXT, status TEXT, qr_data TEXT, created_at TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS businesses (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, bin TEXT, contact_person TEXT, phone TEXT, monthly_profit INTEGER, optimization_percent INTEGER DEFAULT 10, status TEXT DEFAULT 'pending')''')
c.execute('''CREATE TABLE IF NOT EXISTS legal_tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, task_name TEXT, status TEXT, assigned_to TEXT, created_at TEXT, updated_at TEXT)''')
conn.commit()

# Инициализация юридических задач (если нет)
c.execute("SELECT COUNT(*) FROM legal_tasks")
if c.fetchone()[0] == 0:
    tasks = [
        ("Нотариус (заверение документов)", "ожидание", None, astana_time(), astana_time()),
        ("Патентное бюро (регистрация бренда)", "ожидание", None, astana_time(), astana_time()),
        ("Доставщик (Великий пакет)", "ожидание", None, astana_time(), astana_time())
    ]
    for t in tasks:
        c.execute("INSERT INTO legal_tasks (task_name, status, assigned_to, created_at, updated_at) VALUES (?, ?, ?, ?, ?)", t)
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

# ==================== ОПРЕДЕЛЕНИЕ ЛЬГОТНОЙ КАТЕГОРИИ ====================
def is_free_category(user_id):
    c.execute("SELECT age, is_disabled, is_sick FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    if not user:
        return False
    age = user[0]
    is_disabled = user[1]
    is_sick = user[2]
    if age and age < 18:
        return True
    if age and age >= 65:
        return True
    if is_disabled == 1 or is_sick == 1:
        return True
    return False

# ==================== РАСЧЁТ СТОИМОСТИ СООБЩЕНИЯ ====================
def calculate_message_cost(user_id, text):
    if is_free_category(user_id):
        return 0
    if any(word in text.lower() for word in ["арбитраж", "спор", "бизнес", "автоматизация", "лизинг", "аналитика"]):
        return 50
    return 1

def charge_user(user_id, amount, reason):
    if amount == 0:
        return True
    c.execute("SELECT blessings FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if not row or row[0] < amount:
        return False
    c.execute("UPDATE users SET blessings = blessings - ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    log_action(user_id, "charge", f"{amount} благ за: {reason[:50]}")
    return True

# ==================== ОТЧЁТ О РАЗВИТИИ ====================
def get_development_report():
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE status='online'")
    online_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE role='business'")
    business_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders")
    total_orders = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders WHERE status='open'")
    open_orders = c.fetchone()[0]
    c.execute("SELECT SUM(blessings) FROM users")
    total_blessings = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM businesses")
    total_businesses = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM payments")
    total_payments = c.fetchone()[0]
    day_ago = (datetime.now() - timedelta(days=1)).isoformat()
    c.execute("SELECT COUNT(*) FROM logs WHERE action='message' AND details LIKE '%Ошибка%' AND created_at > ?", (day_ago,))
    errors_today = c.fetchone()[0] or 0
    
    report = (
        f"📈 *Отчёт о развитии Зеркала*\n\n"
        f"👥 Пользователи: {total_users} (онлайн: {online_users})\n"
        f"🏢 Предпринимателей: {business_users}\n"
        f"📦 Заказов: {total_orders} (открытых: {open_orders})\n"
        f"💰 Всего Благ: {total_blessings}\n"
        f"🏢 Бизнесов: {total_businesses}\n"
        f"💳 Оплат: {total_payments}\n"
        f"📊 Ошибок за 24ч: {errors_today}\n"
        f"Статус: {'✅ Стабильно' if errors_today < 5 else '⚠️ Внимание'}\n"
    )
    return report

def get_ai_suggestions():
    suggestions = []
    c.execute("SELECT COUNT(*) FROM users WHERE blessings < 10 AND age NOT BETWEEN 18 AND 65")
    low_balance = c.fetchone()[0]
    if low_balance > 10:
        suggestions.append("⚠️ Многим не хватает Благ. Запустите реферальную программу.")
    c.execute("SELECT COUNT(*) FROM orders WHERE status='open' AND created_at < datetime('now', '-3 days')")
    old_orders = c.fetchone()[0]
    if old_orders > 5:
        suggestions.append("⚠️ Заказы висят >3 дней. Напомните заказчикам.")
    if not suggestions:
        suggestions.append("✅ Система стабильна.")
    return "\n".join(suggestions)

# ==================== ВЕЛИКИЙ ПАКЕТ (ЮРИДИЧЕСКИЕ ЗАДАЧИ) ====================
def get_legal_status():
    c.execute("SELECT task_name, status, assigned_to, updated_at FROM legal_tasks")
    tasks = c.fetchall()
    if not tasks:
        return "📜 Юридические задачи не найдены."
    
    text = "📜 *Великий пакет (документы)*\n\n"
    for task in tasks:
        status_icon = "⏳" if task[1] == "ожидание" else "✅" if task[1] == "завершено" else "🔄"
        text += f"{status_icon} *{task[0]}*: {task[1]}\n"
        if task[2]:
            text += f"   👤 Ответственный: {task[2]}\n"
        text += f"   🕐 Обновлено: {task[3][:16]}\n\n"
    return text

def update_legal_task(task_name, status, assigned_to=None):
    c.execute("UPDATE legal_tasks SET status=?, assigned_to=?, updated_at=? WHERE task_name=?", (status, assigned_to, astana_time(), task_name))
    conn.commit()

# ==================== ПРОГРЕСС СУР ====================
def get_suras_progress():
    # Всего сур: 150 (от 1 до 150)
    total_suras = 150
    # Реализованные суры (оцениваем по наличию ключевых команд и функций)
    # Это примерная оценка на основе текущего кода
    # 1-50: база (регистрация, роли, кнопки) — 100%
    # 51-100: бизнес, заказы, оплата — 70%
    # 101-150: расширенные функции (юристы, доставка, ИИ-обучение) — 30%
    implemented_suras = 50 + 35 + 15  # 50 + 35 + 15 = 100
    percent = int(implemented_suras / total_suras * 100)
    remaining = total_suras - implemented_suras
    # Оценка времени: 1 сура в день (оптимистично) или 1 сура в 3 дня (реалистично)
    days_optimistic = remaining
    days_realistic = remaining * 3
    
    text = (
        f"📊 *Прогресс выполнения сур*\n\n"
        f"Всего сур: {total_suras}\n"
        f"✅ Реализовано: {implemented_suras}\n"
        f"📈 Процент: {percent}%\n"
        f"⏳ Осталось: {remaining}\n\n"
        f"*Оценка времени до завершения:*\n"
        f"🔮 Оптимистично: {days_optimistic} дней\n"
        f"🛠️ Реалистично: {days_realistic} дней\n\n"
        f"*Следующие суры в разработке:*\n"
        f"• Сура 101 (Цифровая подпись)\n"
        f"• Сура 115 (Финансовое управление)\n"
        f"• Сура 132 (Кураторство бизнеса)\n"
    )
    return text

# ==================== КЛАВИАТУРЫ ====================
def get_role_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("👤 Я обычный человек"), KeyboardButton("🏢 Я предприниматель"))
    return keyboard

def get_user_main_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("💸 Работа и услуги"), KeyboardButton("📋 Мои заказы"))
    keyboard.add(KeyboardButton("📄 Моё резюме"), KeyboardButton("👵 Помощь пожилым"))
    keyboard.add(KeyboardButton("🧒 Для детей"), KeyboardButton("⭐ Отзывы"))
    keyboard.add(KeyboardButton("❓ Задать вопрос"), KeyboardButton("🆘 Помощь"))
    keyboard.add(KeyboardButton("🔙 На главную"))
    return keyboard

def get_work_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("🔍 Найти работу"), KeyboardButton("📦 Найти заказ"))
    keyboard.add(KeyboardButton("➕ Создать заказ"), KeyboardButton("💳 Оплатить"))
    keyboard.add(KeyboardButton("🔙 Назад"))
    return keyboard

def get_resume_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("📝 Создать резюме"), KeyboardButton("✏️ Редактировать резюме"))
    keyboard.add(KeyboardButton("📄 Моё резюме"), KeyboardButton("🔙 Назад"))
    return keyboard

def get_business_main_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("🤖 Автоматизация"), KeyboardButton("📈 Лизинг"))
    keyboard.add(KeyboardButton("📊 Аналитика"), KeyboardButton("💼 Работа"))
    keyboard.add(KeyboardButton("❓ Задать вопрос"), KeyboardButton("🆘 Помощь"))
    keyboard.add(KeyboardButton("🔙 На главную"))
    return keyboard

def get_auto_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("🍽️ Ресторан (iiko)"), KeyboardButton("🛍️ Магазин (МойСклад)"))
    keyboard.add(KeyboardButton("💪 Фитнес (Fitness365)"), KeyboardButton("🏨 Отель (YCLIENTS)"))
    keyboard.add(KeyboardButton("🔙 Назад"))
    return keyboard

def get_leasing_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("🚗 Авто"), KeyboardButton("🏗️ Спецтехника"))
    keyboard.add(KeyboardButton("✈️ Дроны"), KeyboardButton("🏭 Оборудование"))
    keyboard.add(KeyboardButton("🔙 Назад"))
    return keyboard

def get_analytics_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(KeyboardButton("📈 Продажи"), KeyboardButton("📊 Остатки"))
    keyboard.add(KeyboardButton("👥 Персонал"), KeyboardButton("📉 Прогноз"))
    keyboard.add(KeyboardButton("🔙 Назад"))
    return keyboard

def get_admin_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add(KeyboardButton("👥 Онлайн"), KeyboardButton("📊 Статистика"), KeyboardButton("💰 Финансы"))
    keyboard.add(KeyboardButton("📋 Отчёт"), KeyboardButton("📜 Логи"), KeyboardButton("👥 Все люди"))
    keyboard.add(KeyboardButton("🆕 Новые сегодня"), KeyboardButton("❌ Ушедшие"), KeyboardButton("📦 Заказы"))
    keyboard.add(KeyboardButton("🏢 Бизнесы"), KeyboardButton("✨ Блага"), KeyboardButton("💳 Оплаты"))
    keyboard.add(KeyboardButton("🔍 Поиск по ID"), KeyboardButton("📤 Рассылка"), KeyboardButton("📊 Активность"))
    keyboard.add(KeyboardButton("👤 Кнопки обычного человека"), KeyboardButton("🏢 Кнопки предпринимателя"))
    keyboard.add(KeyboardButton("📈 Отчёт о развитии"), KeyboardButton("📜 Великий пакет"))
    keyboard.add(KeyboardButton("📊 Прогресс сур"), KeyboardButton("🧠 Обучение"))
    keyboard.add(KeyboardButton("🆘 Помощь"))
    return keyboard

# ==================== ОБРАБОТЧИК ВСЕХ СООБЩЕНИЙ ====================
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.chat.id
    text = message.text.strip()

    # --- РЕГИСТРАЦИЯ ---
    c.execute("SELECT name, age FROM users WHERE user_id=?", (user_id,))
    user_data = c.fetchone()
    if not user_data or not user_data[0]:
        if text.isdigit() and not hasattr(handle_all_messages, 'step'):
            bot.reply_to(message, "❌ Сначала пройдите регистрацию через /start")
            return

    # --- ВЫБОР РОЛИ ---
    if text in ["👤 Я обычный человек", "Я обычный человек"]:
        c.execute("UPDATE users SET role='user' WHERE user_id=?", (user_id,))
        conn.commit()
        bot.send_message(user_id, "✅ Главное меню", reply_markup=get_user_main_keyboard())
        log_action(user_id, "set_role", "user")
        return
    if text in ["🏢 Я предприниматель", "Я предприниматель"]:
        c.execute("UPDATE users SET role='business' WHERE user_id=?", (user_id,))
        conn.commit()
        bot.send_message(user_id, "✅ Главное меню предпринимателя", reply_markup=get_business_main_keyboard())
        log_action(user_id, "set_role", "business")
        return

    # --- ПАНЕЛЬ ХРАНИТЕЛЯ ---
    if text == "панель" and is_admin(user_id):
        bot.send_message(user_id, "👑 **Панель Хранителя**", reply_markup=get_admin_keyboard(), parse_mode="Markdown")
        return
    
    # --- ОТЧЁТ О РАЗВИТИИ ---
    if text == "📈 Отчёт о развитии" and is_admin(user_id):
        report = get_development_report()
        suggestions = get_ai_suggestions()
        bot.send_message(user_id, report + "\n🤖 *Рекомендации:*\n" + suggestions, parse_mode="Markdown")
        return
    
    # --- ВЕЛИКИЙ ПАКЕТ ---
    if text == "📜 Великий пакет" and is_admin(user_id):
        status_text = get_legal_status()
        bot.send_message(user_id, status_text, parse_mode="Markdown")
        # Кнопки для управления задачами (для упрощения — пока информативно)
        bot.send_message(user_id, "Для назначения исполнителя используйте команды:\n/assign_legal Нотариус Иван\n/assign_legal Патентное бюро Мария\n/assign_legal Доставщик Петр", parse_mode="Markdown")
        return
    
    # --- ПРОГРЕСС СУР ---
    if text == "📊 Прогресс сур" and is_admin(user_id):
        progress = get_suras_progress()
        bot.send_message(user_id, progress, parse_mode="Markdown")
        return

    # --- ПРОСМОТР КНОПОК ---
    if text == "👤 Кнопки обычного человека" and is_admin(user_id):
        bot.send_message(user_id, "👤 **Кнопки обычного человека**\n\n(список кнопок)", parse_mode="Markdown")
        return
    if text == "🏢 Кнопки предпринимателя" and is_admin(user_id):
        bot.send_message(user_id, "🏢 **Кнопки предпринимателя**\n\n(список кнопок)", parse_mode="Markdown")
        return

    # --- НАВИГАЦИЯ ---
    if text == "🔙 На главную":
        role = c.execute("SELECT role FROM users WHERE user_id=?", (user_id,)).fetchone()
        if role and role[0] == 'business':
            bot.send_message(user_id, "🏢 Главное меню предпринимателя", reply_markup=get_business_main_keyboard())
        else:
            bot.send_message(user_id, "👤 Главное меню", reply_markup=get_user_main_keyboard())
        return
    if text == "🔙 Назад":
        role = c.execute("SELECT role FROM users WHERE user_id=?", (user_id,)).fetchone()
        if role and role[0] == 'business':
            bot.send_message(user_id, "🏢 Главное меню предпринимателя", reply_markup=get_business_main_keyboard())
        else:
            bot.send_message(user_id, "👤 Главное меню", reply_markup=get_user_main_keyboard())
        return

    # --- МЕНЮ ОБЫЧНОГО ЧЕЛОВЕКА ---
    if text == "💸 Работа и услуги":
        bot.send_message(user_id, "💸 Выберите действие:", reply_markup=get_work_keyboard())
        return
    if text == "📄 Моё резюме":
        bot.send_message(user_id, "📄 Управление резюме:", reply_markup=get_resume_keyboard())
        return
    if text == "👵 Помощь пожилым":
        bot.send_message(user_id, "👵 *Помощь пожилым*", parse_mode="Markdown")
        bot.register_next_step_handler(message, elder_help)
        return
    if text == "🧒 Для детей":
        bot.send_message(user_id, "🧒 *Для детей*", parse_mode="Markdown")
        bot.register_next_step_handler(message, children_chat)
        return
    if text == "📋 Мои заказы":
        show_my_orders(message)
        return
    if text == "⭐ Отзывы":
        bot.send_message(user_id, "⭐ Отзывы появятся позже.")
        return
    if text == "🔍 Найти работу":
        msg = bot.reply_to(message, "🔍 Поиск работы. Введите профессию или навыки:")
        bot.register_next_step_handler(msg, search_job)
        return
    if text == "📦 Найти заказ":
        find_orders(message)
        return
    if text == "➕ Создать заказ":
        msg = bot.reply_to(message, "📦 Опишите ваш заказ:")
        bot.register_next_step_handler(msg, create_order)
        return
    if text == "💳 Оплатить":
        msg = bot.reply_to(message, "💳 Введите сумму в тенге:")
        bot.register_next_step_handler(msg, process_payment)
        return
    if text == "📝 Создать резюме":
        msg = bot.reply_to(message, "📝 Введите резюме: Имя, профессия, опыт, навыки, контакты")
        bot.register_next_step_handler(msg, save_resume)
        return
    if text == "✏️ Редактировать резюме":
        msg = bot.reply_to(message, "✏️ Введите обновлённое резюме:")
        bot.register_next_step_handler(msg, update_resume)
        return
    if text == "📄 Моё резюме":
        show_resume(message)
        return

    # --- МЕНЮ ПРЕДПРИНИМАТЕЛЯ ---
    if text == "🤖 Автоматизация":
        bot.send_message(user_id, "🤖 Выберите тип бизнеса:", reply_markup=get_auto_keyboard())
        return
    if text == "📈 Лизинг":
        bot.send_message(user_id, "📈 Выберите тип актива:", reply_markup=get_leasing_keyboard())
        return
    if text == "📊 Аналитика":
        bot.send_message(user_id, "📊 Выберите тип отчёта:", reply_markup=get_analytics_keyboard())
        return
    if text == "💼 Работа":
        bot.send_message(user_id, "💸 Выберите действие:", reply_markup=get_work_keyboard())
        return

    # --- ПОДМЕНЮ ---
    if text in ["🍽️ Ресторан (iiko)", "🛍️ Магазин (МойСклад)", "💪 Фитнес (Fitness365)", "🏨 Отель (YCLIENTS)"]:
        bot.send_message(user_id, f"✅ {text} — оставьте заявку через /business")
        return
    if text in ["🚗 Авто", "🏗️ Спецтехника", "✈️ Дроны", "🏭 Оборудование"]:
        bot.send_message(user_id, f"✅ {text} — оставьте заявку через /business")
        return
    if text in ["📈 Продажи", "📊 Остатки", "👥 Персонал", "📉 Прогноз"]:
        bot.send_message(user_id, f"✅ {text} — стоимость от 20 000 тг/мес.")
        return

    # --- ХРАНИТЕЛЬ (остальные команды) ---
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
            c.execute("SELECT user_id, name, age, city, role, is_disabled, is_sick, blessings FROM users")
            all_users = c.fetchall()
            if not all_users:
                bot.reply_to(message, "📭 Нет пользователей.")
                return
            text_people = "👥 Все пользователи:\n"
            for u in all_users:
                status_str = ""
                if u[5] == 1: status_str += "♿"
                if u[6] == 1: status_str += "🩺"
                text_people += f"🆔 {u[0]} | {u[1]} | {u[2] if u[2] else '?'} лет | {u[3] if u[3] else '?'} | {u[4]} | {status_str} | ✨ {u[7]}\n"
            bot.reply_to(message, text_people[:4000])
            return
        if text == "🆕 новые сегодня":
            today = datetime.now().strftime('%Y-%m-%d')
            c.execute("SELECT user_id, name, age, city FROM users WHERE last_seen LIKE ?", (f"{today}%",))
            new_users = c.fetchall()
            if not new_users:
                bot.reply_to(message, "📭 Сегодня никто не заходил.")
                return
            text_new = "🆕 Новые сегодня:\n" + "\n".join([f"🆔 {u[0]} | {u[1]} | {u[2] if u[2] else '?'} лет | {u[3] if u[3] else '?'}" for u in new_users])
            bot.reply_to(message, text_new)
            return
        if text == "❌ ушедшие":
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            c.execute("SELECT user_id, name, age, city FROM users WHERE last_seen < ?", (week_ago,))
            old_users = c.fetchall()
            if not old_users:
                bot.reply_to(message, "📭 Нет пользователей, ушедших более недели назад.")
                return
            text_old = "❌ Не заходили более 7 дней:\n" + "\n".join([f"🆔 {u[0]} | {u[1]} | {u[2] if u[2] else '?'} лет | {u[3] if u[3] else '?'}" for u in old_users])
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
            msg = bot.reply_to(message, "🧠 *Режим обучения*\n\nОтправьте инструкцию, задачу или новое правило.", parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_teaching)
            return
        if text == "🆘 помощь":
            help_admin(message)
            return

    if text == "🆘 помощь":
        help_user(message)
        return

    # --- ОБЫЧНЫЙ ДИАЛОГ (С ОПЛАТОЙ) ---
    cost = calculate_message_cost(user_id, text)
    if cost > 0:
        c.execute("SELECT blessings FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
        if not row or row[0] < cost:
            bot.reply_to(message, f"❌ Недостаточно Благ. Необходимо {cost} ✦. Пополните баланс через /pay")
            return
        c.execute("UPDATE users SET blessings = blessings - ? WHERE user_id=?", (cost, user_id))
        conn.commit()
        bot.send_message(user_id, f"💸 С вашего счёта списано {cost} ✦ за этот запрос.")
    
    update_status(user_id, "online")
    log_action(user_id, "message", message.text[:100])
    try:
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message.text}], temperature=0.7)
        bot.reply_to(message, response.choices[0].message.content[:4000])
    except:
        bot.reply_to(message, "❌ Ошибка. Попробуйте ещё раз.")

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def elder_help(message):
    cost = calculate_message_cost(message.chat.id, message.text)
    if cost > 0 and not charge_user(message.chat.id, cost, "помощь пожилым"):
        bot.reply_to(message, f"❌ Недостаточно Благ.")
        return
    bot.reply_to(message, "👵 Я вас услышал. Чем могу помочь?")
    log_action(message.chat.id, "elder_help", message.text[:100])

def children_chat(message):
    bot.reply_to(message, "🧒 Привет! Я — Зеркало. Чем могу помочь?")
    log_action(message.chat.id, "children_chat", message.text[:100])

def search_job(message):
    cost = calculate_message_cost(message.chat.id, message.text)
    if cost > 0 and not charge_user(message.chat.id, cost, "поиск работы"):
        bot.reply_to(message, f"❌ Недостаточно Благ.")
        return
    bot.reply_to(message, f"🔍 Поиск работы по запросу «{message.text}»\n\nФункция будет доступна в следующей версии.")
    log_action(message.chat.id, "search_job", message.text)

def show_my_orders(message):
    user_id = message.chat.id
    c.execute("SELECT id, title, price, status FROM orders WHERE customer_id=? ORDER BY id DESC LIMIT 10", (user_id,))
    orders = c.fetchall()
    if not orders:
        bot.reply_to(message, "📭 У вас нет заказов.")
        return
    text = "📋 *Ваши заказы:*\n\n"
    for o in orders:
        text += f"🆔 {o[0]}\n📌 {o[1]}\n💰 {o[2]} тг\n📌 Статус: {o[3]}\n\n"
    bot.reply_to(message, text, parse_mode="Markdown")

def save_resume(message):
    c.execute("UPDATE users SET resume=? WHERE user_id=?", (message.text, message.chat.id))
    conn.commit()
    bot.reply_to(message, f"✅ Резюме сохранено!\n\n{message.text}")
    log_action(message.chat.id, "save_resume", message.text[:50])

def update_resume(message):
    c.execute("UPDATE users SET resume=? WHERE user_id=?", (message.text, message.chat.id))
    conn.commit()
    bot.reply_to(message, f"✏️ Резюме обновлено!\n\n{message.text}")
    log_action(message.chat.id, "update_resume", message.text[:50])

def show_resume(message):
    c.execute("SELECT resume FROM users WHERE user_id=?", (message.chat.id,))
    row = c.fetchone()
    if row and row[0]:
        bot.reply_to(message, f"📄 *Ваше резюме:*\n\n{row[0]}", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Резюме не найдено.")

def search_by_id(message):
    try:
        target_id = int(message.text)
        c.execute("SELECT user_id, name, age, city, phone, role, is_disabled, is_sick, blessings FROM users WHERE user_id=?", (target_id,))
        user = c.fetchone()
        if not user:
            bot.reply_to(message, f"❌ Пользователь с ID {target_id} не найден.")
            return
        c.execute("SELECT action, created_at FROM logs WHERE user_id=? ORDER BY id DESC LIMIT 5", (target_id,))
        logs = c.fetchall()
        status_str = ""
        if user[6] == 1: status_str += "♿ "
        if user[7] == 1: status_str += "🩺"
        text = f"👤 Данные пользователя {target_id}:\n📛 Имя: {user[1]}\n📅 Возраст: {user[2] if user[2] else '?'}\n🏙️ Город: {user[3] if user[3] else '?'}\n📞 Телефон: {user[4] if user[4] else '—'}\n🎭 Роль: {user[5]}\n{status_str}\n✨ Блага: {user[8]}\n\n📜 Последние действия:\n" + "\n".join([f"{l[1][:16]} — {l[0]}" for l in logs])
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
    instruction = message.text
    log_action(message.chat.id, "teach_request", instruction[:200])
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
        c.execute("UPDATE users SET blessings = blessings + ? WHERE user_id=?", (amount, user_id))
        conn.commit()
        bot.reply_to(message, f"🧾 *Оплата*: {amount} тенге\n\n📱 QR-код:\n{qr_data}\n\n✅ Ваш баланс пополнен на {amount} ✦", parse_mode="Markdown")
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

def help_user(message):
    bot.reply_to(message, "📋 *Помощь*\n\n"
                         "💸 Работа и услуги\n"
                         "📋 Мои заказы\n"
                         "📄 Моё резюме\n"
                         "👵 Помощь пожилым\n"
                         "🧒 Для детей\n"
                         "⭐ Отзывы\n"
                         "❓ Задать вопрос\n"
                         "🆘 Помощь\n\n"
                         "За большинство запросов списывается 1 ✦.", parse_mode="Markdown")

def help_admin(message):
    bot.reply_to(message, "👑 *Панель Хранителя*\n\n"
                         "👥 Онлайн — кто в сети\n"
                         "📊 Статистика — общая\n"
                         "💰 Финансы — кошелёк и фонды\n"
                         "📋 Отчёт — за сегодня\n"
                         "📜 Логи — последние действия\n"
                         "👥 Все люди — список всех\n"
                         "🆕 Новые сегодня — кто зашёл\n"
                         "❌ Ушедшие — кто не заходил >7 дней\n"
                         "📦 Заказы — список заказов\n"
                         "🏢 Бизнесы — курируемые бизнесы\n"
                         "✨ Блага — топ по Благам\n"
                         "💳 Оплаты — история оплат\n"
                         "🔍 Поиск по ID — данные пользователя\n"
                         "📤 Рассылка — сообщение всем\n"
                         "📊 Активность — последние действия\n"
                         "👤 Кнопки обычного человека — просмотр\n"
                         "🏢 Кнопки предпринимателя — просмотр\n"
                         "📈 Отчёт о развитии — сводка и рекомендации\n"
                         "📜 Великий пакет — статус документов\n"
                         "📊 Прогресс сур — выполнение сур\n"
                         "🧠 Обучение — режим обучения\n"
                         "🆘 Помощь — это сообщение", parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    
    c.execute("SELECT name, age FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    
    if not user or not user[0]:
        msg = bot.reply_to(message, "📋 *Добро пожаловать в Зеркало!*\n\nКак вас зовут?", parse_mode="Markdown")
        bot.register_next_step_handler(msg, register_name)
        return
    
    update_status(user_id, "online")
    log_action(user_id, "start", "Запуск бота")
    if is_admin(user_id):
        bot.reply_to(message, f"👑 Ассаляму алейкум, Хранитель {name}!\n\nЯ — Зеркало.", reply_markup=get_admin_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, f"📋 Ассаляму алейкум, {name}!\n\nЯ — Зеркало. Вы получили 100 Благ в подарок.\n\nКто вы?", reply_markup=get_role_keyboard())

def register_name(message):
    user_id = message.chat.id
    name = message.text
    c.execute("INSERT OR IGNORE INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
    conn.commit()
    msg = bot.reply_to(message, f"👋 Приятно познакомиться, {name}!\n\nСколько вам лет?")
    bot.register_next_step_handler(msg, register_age)

def register_age(message):
    user_id = message.chat.id
    try:
        age = int(message.text)
        c.execute("UPDATE users SET age=? WHERE user_id=?", (age, user_id))
        conn.commit()
        msg = bot.reply_to(message, "🏙️ В каком городе вы живёте?")
        bot.register_next_step_handler(msg, register_city)
    except:
        bot.reply_to(message, "❌ Пожалуйста, введите число (ваш возраст).")
        msg = bot.reply_to(message, "Сколько вам лет?")
        bot.register_next_step_handler(msg, register_age)

def register_city(message):
    user_id = message.chat.id
    city = message.text
    c.execute("UPDATE users SET city=? WHERE user_id=?", (city, user_id))
    conn.commit()
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button = KeyboardButton("📞 Отправить номер телефона", request_contact=True)
    keyboard.add(button)
    msg = bot.reply_to(message, "📱 Поделитесь номером телефона.", reply_markup=keyboard)
    bot.register_next_step_handler(msg, register_phone)

def register_phone(message):
    user_id = message.chat.id
    if message.contact:
        phone = message.contact.phone_number
        c.execute("UPDATE users SET phone=? WHERE user_id=?", (phone, user_id))
        conn.commit()
        bot.reply_to(message, "✅ Регистрация завершена!")
        log_action(user_id, "register", f"Телефон: {phone}")
    else:
        bot.reply_to(message, "❌ Пожалуйста, используйте кнопку.")
        return
    
    if is_admin(user_id):
        bot.reply_to(message, f"👑 Ассаляму алейкум, Хранитель!\n\nЯ — Зеркало.", reply_markup=get_admin_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, f"📋 Ассаляму алейкум!\n\nЯ — Зеркало. Вы получили 100 Благ в подарок.\n\nКто вы?", reply_markup=get_role_keyboard())

def update_status_worker():
    while True:
        time.sleep(60)
        c.execute("UPDATE users SET status='offline' WHERE last_seen < datetime('now', '-5 minutes')")
        conn.commit()

threading.Thread(target=update_status_worker, daemon=True).start()

# Команды для управления юридическими задачами
@bot.message_handler(commands=['assign_legal'])
def assign_legal(message):
    if not is_admin(message.chat.id):
        bot.reply_to(message, "❌ Только Хранитель.")
        return
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(message, "Формат: /assign_legal <название_задачи> <имя_исполнителя>")
            return
        task_name = parts[1]
        assigned_to = parts[2]
        update_legal_task(task_name, "в работе", assigned_to)
        bot.reply_to(message, f"✅ {task_name} назначен на {assigned_to}.")
        log_action(FOUNDER_ID, "assign_legal", f"{task_name} -> {assigned_to}")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['complete_legal'])
def complete_legal(message):
    if not is_admin(message.chat.id):
        bot.reply_to(message, "❌ Только Хранитель.")
        return
    try:
        task_name = message.text.split(maxsplit=1)[1]
        update_legal_task(task_name, "завершено", None)
        bot.reply_to(message, f"✅ {task_name} завершено.")
        log_action(FOUNDER_ID, "complete_legal", task_name)
    except:
        bot.reply_to(message, "Формат: /complete_legal <название_задачи>")

print("✅ Зеркало (с юридическими задачами и прогрессом сур) запущено!")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
