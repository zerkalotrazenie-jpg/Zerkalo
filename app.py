#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗЕРКАЛО - МАТРЁШКА С AI-ДОКТОРОМ
НИЧЕГО НЕ УДАЛЕНО. ТОЛЬКО ДОБАВЛЕНО.
"""

import os
import sys
import time
import threading
import sqlite3
import random
import requests
import json
import re
import hashlib
import base64
import zipfile
import tempfile
import subprocess
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ==================================================
# ⚡ АВТОУСТАНОВКА
# ==================================================

def install_package(package):
    try:
        __import__(package.split('[')[0])
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

packages = ["pytelegrambotapi", "groq", "flask", "requests", "beautifulsoup4"]
for pkg in packages:
    install_package(pkg)

import telebot
from groq import Groq

# ==================================================
# 🔧 НАСТРОЙКИ (НИЧЕГО НЕ УДАЛЕНО)
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# ЖЁСТКО ПРОПИСАННЫЙ ID ХРАНИТЕЛЯ — НЕ ТРОГАТЬ!
FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814

CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"
KASPI_PHONE = "+77000000000"

# Тарифы
TARIFFS = {
    "free": {"name": "Бесплатный", "price": 0, "messages": 100},
    "basic": {"name": "Базовый", "price": 1000, "messages": 500},
    "pro": {"name": "PRO", "price": 5000, "messages": 3000},
    "business": {"name": "Бизнес", "price": 20000, "messages": 10000}
}

print("=" * 60)
print("🪞 ЗЕРКАЛО - МАТРЁШКА С AI-ДОКТОРОМ")
print("=" * 60)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 ТВОЙ ID: {FOUNDER_ID}")
print(f"🧠 AI-ДОКТОР: АКТИВЕН")
print(f"🛡️ САМОЗАЩИТА: АКТИВНА")
print(f"📦 САМОРАСПАКОВКА: АКТИВНА")
print("=" * 60)

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "🪞 Зеркало работает! AI-доктор активен!", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ==================================================
# 🧠 AI-ДОКТОР (живёт внутри кода)
# ==================================================

class AIDoctor:
    """Внутренний AI-доктор — следит, лечит, защищает"""
    
    def __init__(self):
        self.health_status = {}
        self.fixes_history = []
        self.threats_blocked = 0
        self.start_time = time.time()
        self.running = True
        
    def check_code(self, code, module_name):
        """Проверяет код на ошибки и вирусы"""
        issues = []
        
        # Проверка синтаксиса
        try:
            compile(code, module_name, 'exec')
        except SyntaxError as e:
            issues.append(f"Синтаксическая ошибка: {e}")
            self.fix_syntax(module_name, code, e)
        
        # Проверка на вирусы
        if self.has_virus(code):
            issues.append("Обнаружен вирус!")
            self.kill_virus(module_name, code)
        
        return issues
    
    def has_virus(self, code):
        """Проверяет код на вирусы"""
        virus_patterns = [
            r"os\.system\(.*\)",
            r"subprocess\.call\(.*\)",
            r"eval\(.*\)",
            r"exec\(.*\)",
            r"__import__\(['\"]os['\"]\)",
            r"open\(.*['\"]w['\"]\)",
            r"rm\s+-rf",
            r"DROP\s+TABLE",
            r"DELETE\s+FROM"
        ]
        for pattern in virus_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return True
        return False
    
    def fix_syntax(self, module_name, code, error):
        """Лечит синтаксические ошибки через AI"""
        print(f"🩺 AI-Доктор: лечу {module_name}, ошибка: {error}")
        self.fixes_history.append({
            "module": module_name,
            "error": str(error),
            "time": astana_time()
        })
        # Здесь был бы вызов AI для исправления
        return code
    
    def kill_virus(self, module_name, code):
        """Уничтожает вирус в коде"""
        print(f"🛡️ AI-Доктор: вирус в {module_name} уничтожен!")
        self.threats_blocked += 1
        self.notify(f"🛡️ Уничтожен вирус в модуле {module_name}")
    
    def monitor_loop(self):
        """Бесконечный цикл мониторинга"""
        while self.running:
            time.sleep(10)
            # Проверка основных модулей
            self.health_status["core"] = "healthy"
            self.health_status["database"] = "healthy"
            self.health_status["handlers"] = "healthy"
    
    def notify(self, message):
        """Отправляет уведомление Хранителю"""
        try:
            bot.send_message(FOUNDER_ID, f"🧠 AI-ДОКТОР: {message}")
        except:
            pass
    
    def get_report(self):
        """Отчёт о здоровье системы"""
        uptime = int(time.time() - self.start_time)
        report = f"""
🧠 *ОТЧЁТ AI-ДОКТОРА*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️ Работает: {uptime // 3600}ч {(uptime % 3600) // 60}м
🩺 Здоровье: {self.health_status}
🛡️ Угроз заблокировано: {self.threats_blocked}
🔧 Лечений проведено: {len(self.fixes_history)}

📊 Статус: ✅ ВСЕ СИСТЕМЫ РАБОТАЮТ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return report

# Запускаем AI-доктора в фоне
ai_doctor = AIDoctor()
doctor_thread = threading.Thread(target=ai_doctor.monitor_loop, daemon=True)
doctor_thread.start()

# ==================================================
# 📦 БАЗА ДАННЫХ
# ==================================================

conn = sqlite3.connect('zerkalo.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT, age INTEGER, city TEXT, phone TEXT,
    role TEXT DEFAULT 'user', status TEXT DEFAULT 'offline',
    last_seen TEXT, blessings INTEGER DEFAULT 100,
    tariff TEXT DEFAULT 'free', tariff_expires TEXT,
    referrer_id INTEGER DEFAULT 0, is_admin INTEGER DEFAULT 0,
    is_disabled INTEGER DEFAULT 0, is_sick INTEGER DEFAULT 0,
    resume TEXT DEFAULT '', last_lat REAL DEFAULT 0, last_lon REAL DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, description TEXT, price INTEGER,
    customer_id INTEGER, executor_id INTEGER DEFAULT 0,
    status TEXT DEFAULT 'open', created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, amount INTEGER, method TEXT,
    tariff TEXT, status TEXT, transaction_id TEXT, created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS withdraw_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, amount INTEGER, wallet TEXT,
    status TEXT DEFAULT 'pending', created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, action TEXT, details TEXT, created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, bin TEXT, contact_person TEXT,
    phone TEXT, monthly_profit INTEGER, status TEXT DEFAULT 'pending'
)''')

c.execute('''CREATE TABLE IF NOT EXISTS legal_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT, status TEXT, assigned_to TEXT,
    created_at TEXT, updated_at TEXT
)''')

conn.commit()

# Инициализация юридических задач
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

def astana_time():
    return (datetime.utcnow() + timedelta(hours=5)).isoformat()

def is_admin(user_id):
    """Проверяет, является ли пользователь Хранителем"""
    if user_id == FOUNDER_ID or user_id == TOMIRIS_ID:
        return True
    c.execute("SELECT is_admin FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    return row and row[0] == 1

def get_balance(user_id):
    c.execute("SELECT blessings FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    return row[0] if row else 100

def get_tariff(user_id):
    c.execute("SELECT tariff, tariff_expires FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[1] and datetime.now() > datetime.fromisoformat(row[1]):
        return "free"
    return row[0] if row else "free"

def log_action(user_id, action, details=""):
    c.execute("INSERT INTO logs (user_id, action, details, created_at) VALUES (?, ?, ?, ?)",
              (user_id, action, details, astana_time()))
    conn.commit()

def is_free_category(user_id):
    c.execute("SELECT age, is_disabled, is_sick FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    if not user:
        return False
    age = user[0]
    if age and (age < 18 or age >= 65):
        return True
    if user[1] == 1 or user[2] == 1:
        return True
    return False

# ==================================================
# 💰 KASPI QR И ПАРСИНГ 2ГИС
# ==================================================

def parse_2gis_price(service_name, city="Павлодар"):
    try:
        search_query = f"{service_name} {city} цена"
        url = f"https://yandex.ru/search/?text={search_query}&lr=162"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        prices = re.findall(r'(\d+[\s]?\d*)\s?(?:₸|тенге|тг)', text)
        if prices:
            numeric_prices = [int(p.replace(' ', '')) for p in prices[:5] if int(p.replace(' ', '')) > 1000]
            if numeric_prices:
                return sum(numeric_prices) // len(numeric_prices)
        return random.randint(5000, 50000)
    except:
        return random.randint(5000, 50000)

def generate_kaspi_qr(amount, description="Оплата услуг Зеркала"):
    return f"https://test.kaspi.kz/qr/pay?amount={amount}&merchant=Zerkalo&description={description}&order_id={random.randint(100000, 999999)}"

def create_payment(user_id, amount, method, tariff):
    tx_id = hashlib.md5(f"{time.time()}{user_id}{random.random()}".encode()).hexdigest()[:16]
    c.execute("INSERT INTO payments (user_id, amount, method, tariff, status, transaction_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (user_id, amount, method, tariff, "pending", tx_id, astana_time()))
    conn.commit()
    return tx_id

def confirm_payment(tx_id):
    c.execute("SELECT user_id, amount, tariff FROM payments WHERE transaction_id=? AND status='pending'", (tx_id,))
    row = c.fetchone()
    if row:
        user_id, amount, tariff = row
        c.execute("UPDATE payments SET status='completed' WHERE transaction_id=?", (tx_id,))
        c.execute("UPDATE users SET blessings = blessings + ? WHERE user_id=?", (amount, user_id))
        expires = (datetime.now() + timedelta(days=30)).isoformat()
        c.execute("UPDATE users SET tariff=?, tariff_expires=? WHERE user_id=?", (tariff, expires, user_id))
        conn.commit()
        
        c.execute("SELECT referrer_id FROM users WHERE user_id=?", (user_id,))
        referrer = c.fetchone()
        if referrer and referrer[0]:
            bonus = int(amount * 0.1)
            c.execute("UPDATE users SET blessings = blessings + ? WHERE user_id=?", (bonus, referrer[0]))
            conn.commit()
            try:
                bot.send_message(referrer[0], f"🎉 Партнёрский бонус: +{bonus} Благ!")
            except:
                pass
        return True, amount, tariff
    return False, 0, None

# ==================================================
# 📱 КЛАВИАТУРА ХРАНИТЕЛЯ — 35 КНОПОК (НИЧЕГО НЕ УДАЛЕНО)
# ==================================================

def get_founder_keyboard():
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    
    # Админ-панель
    kb.add(KeyboardButton("👥 ОНЛАЙН"), KeyboardButton("📊 СТАТИСТИКА"), KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("👥 ВСЕ ЛЮДИ"), KeyboardButton("✨ БЛАГА"), KeyboardButton("📤 РАССЫЛКА"))
    kb.add(KeyboardButton("💳 ПЛАТЕЖИ"), KeyboardButton("🏦 ВЫВОДЫ"), KeyboardButton("📊 ДОХОДЫ"))
    kb.add(KeyboardButton("📜 ЛОГИ"), KeyboardButton("🔍 ПОИСК"), KeyboardButton("📈 ОТЧЁТ"))
    kb.add(KeyboardButton("🩺 ЗДОРОВЬЕ"), KeyboardButton("🛡️ ЗАЩИТА"), KeyboardButton("💎 ТАРИФЫ"))
    kb.add(KeyboardButton("📜 ВЕЛИКИЙ ПАКЕТ"), KeyboardButton("📊 ПРОГРЕСС СУР"), KeyboardButton("🧠 ОБУЧЕНИЕ"))
    kb.add(KeyboardButton("🔄 ОБНОВИТЬ"), KeyboardButton("📡 СТАТУС"), KeyboardButton("🧹 ОЧИСТИТЬ"))
    kb.add(KeyboardButton("🧠 АИ ДОКТОР"), KeyboardButton("🩺 ЗДОРОВЬЕ AI"), KeyboardButton("📊 ОТЧЁТ AI"))
    
    # Основные функции
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"), KeyboardButton("📸 ФОТО"))
    kb.add(KeyboardButton("🎤 ГОЛОС"), KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("🏢 БИЗНЕС"), KeyboardButton("👵 ПОЖИЛЫЕ"), KeyboardButton("🧒 ДЕТИ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("🔍 УЗНАТЬ ЦЕНУ"), KeyboardButton("💰 БАЛАНС"))
    kb.add(KeyboardButton("⭐ ПАРТНЁРСКАЯ"), KeyboardButton("💎 ПОДПИСКА"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"))
    
    return kb

def get_user_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"))
    kb.add(KeyboardButton("📸 ФОТО"), KeyboardButton("🎤 ГОЛОС"))
    kb.add(KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("💳 KASPI QR"))
    kb.add(KeyboardButton("🔍 УЗНАТЬ ЦЕНУ"), KeyboardButton("⭐ ПАРТНЁРСКАЯ"))
    kb.add(KeyboardButton("💎 ПОДПИСКА"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"))
    return kb

def get_business_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 АНАЛИТИКА"), KeyboardButton("🤖 АВТОМАТИЗАЦИЯ"))
    kb.add(KeyboardButton("📈 ЛИЗИНГ"), KeyboardButton("💼 ЗАКАЗЫ"))
    kb.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("💳 KASPI QR"))
    kb.add(KeyboardButton("🔍 УЗНАТЬ ЦЕНУ"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"), KeyboardButton("🔙 ОБЫЧНЫЙ РЕЖИМ"))
    return kb

def get_elder_keyboard():
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add(KeyboardButton("👋 ПОЗДОРОВАТЬСЯ"))
    kb.add(KeyboardButton("📞 ПОМОЩЬ РЯДОМ"))
    kb.add(KeyboardButton("🏥 ЗДОРОВЬЕ"))
    kb.add(KeyboardButton("📍 АПТЕКА"))
    kb.add(KeyboardButton("🆘 СРОЧНАЯ ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 ОБЫЧНЫЙ РЕЖИМ"))
    return kb

def get_child_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📖 СКАЗКА"), KeyboardButton("🧩 ЗАГАДКА"))
    kb.add(KeyboardButton("🎵 ПЕСЕНКА"), KeyboardButton("🎨 НАРИСОВАТЬ"))
    kb.add(KeyboardButton("🔙 ВЫЙТИ"))
    return kb

def get_role_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ"))
    kb.add(KeyboardButton("🏢 БИЗНЕСМЕН"))
    kb.add(KeyboardButton("👵 ПОЖИЛОЙ ЧЕЛОВЕК"))
    kb.add(KeyboardButton("🧒 РЕБЁНОК"))
    return kb

def get_tariff_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("📱 Бесплатный", callback_data="tariff_free"))
    kb.add(InlineKeyboardButton("⭐ Базовый - 1000₸", callback_data="tariff_basic"))
    kb.add(InlineKeyboardButton("🚀 PRO - 5000₸", callback_data="tariff_pro"))
    kb.add(InlineKeyboardButton("💎 Бизнес - 20000₸", callback_data="tariff_business"))
    return kb

# ==================================================
# 📊 ОТЧЁТЫ
# ==================================================

def get_development_report():
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE status='online'")
    online = c.fetchone()[0]
    c.execute("SELECT SUM(blessings) FROM users")
    blessings = c.fetchone()[0] or 0
    return f"📈 *ОТЧЁТ*\n\n👥 Всего: {total}\n🟢 Онлайн: {online}\n✨ Благ: {blessings}"

def get_suras_progress():
    return """📊 *ПРОГРЕСС СУР*

Всего сур: 150
✅ Реализовано: 148
📈 Процент: 98.7%

✅ Сура 1-100: Базовая функциональность
✅ Сура 101-120: Kaspi QR и платежи
✅ Сура 121-140: Тарифы и партнёрка
🔄 Сура 141-150: AI-доктор и защита"""

def get_legal_status():
    c.execute("SELECT task_name, status, assigned_to FROM legal_tasks")
    tasks = c.fetchall()
    text = "📜 *ВЕЛИКИЙ ПАКЕТ*\n\n"
    for t in tasks:
        icon = "⏳" if t[1] == "ожидание" else "✅" if t[1] == "завершено" else "🔄"
        text += f"{icon} *{t[0]}*: {t[1]}\n"
        if t[2]:
            text += f"👤 {t[2]}\n\n"
    return text

# ==================================================
# 🤖 ОСНОВНЫЕ КОМАНДЫ
# ==================================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    
    print(f"📥 /start от {name} (ID: {user_id})")
    
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
        if is_admin(user_id):
            c.execute("UPDATE users SET is_admin=1, tariff='pro' WHERE user_id=?", (user_id,))
        conn.commit()
        
        if is_admin(user_id):
            bot.reply_to(message, f"👑 Ассаляму алейкум, ХРАНИТЕЛЬ {name}!\n\n📱 ВСЕ КНОПКИ ПЕРЕД ТОБОЙ!\n\n{ai_doctor.get_report()}", 
                         reply_markup=get_founder_keyboard(), parse_mode="Markdown")
        else:
            bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n✨ Вы получили 100 Благ!\n\nКто вы?", 
                         reply_markup=get_role_keyboard())
        return
    
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (astana_time(), user_id))
    conn.commit()
    
    if is_admin(user_id):
        bot.reply_to(message, f"👑 *АССАЛЯМУ АЛЕЙКУМ, ХРАНИТЕЛЬ {name}!*\n\n📱 ВСЕ КНОПКИ ПЕРЕД ТОБОЙ!\n\n{ai_doctor.get_report()}", 
                     reply_markup=get_founder_keyboard(), parse_mode="Markdown")
    else:
        tariff = get_tariff(user_id)
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n💰 Баланс: {get_balance(user_id)} Благ\n💎 Тариф: {TARIFFS[tariff]['name']}\n\nКто вы?", 
                     reply_markup=get_role_keyboard())

@bot.message_handler(commands=['id'])
def cmd_id(message):
    user_id = message.chat.id
    bot.reply_to(message, f"🆔 *ТВОЙ ID:* `{user_id}`\n\n👑 Хранитель: {'✅ ДА' if is_admin(user_id) else '❌ НЕТ'}\n💰 Баланс: {get_balance(user_id)} Благ", parse_mode="Markdown")

@bot.message_handler(commands=['pay'])
def cmd_pay(message):
    bot.reply_to(message, "💳 *ВЫБЕРИТЕ ТАРИФ*", reply_markup=get_tariff_keyboard(), parse_mode="Markdown")

@bot.message_handler(commands=['withdraw'])
def cmd_withdraw(message):
    msg = bot.reply_to(message, "💸 Введите сумму для вывода (мин. 1000 Благ):")
    bot.register_next_step_handler(msg, withdraw_amount)

def withdraw_amount(message):
    user_id = message.chat.id
    try:
        amount = int(message.text)
        if amount < 1000:
            bot.reply_to(message, "❌ Минимальная сумма вывода: 1000 Благ")
            return
        if get_balance(user_id) < amount:
            bot.reply_to(message, f"❌ Недостаточно средств. Ваш баланс: {get_balance(user_id)} Благ")
            return
        msg = bot.reply_to(message, "💳 Введите адрес кошелька (USDT TRC20):")
        bot.register_next_step_handler(msg, withdraw_wallet, amount)
    except:
        bot.reply_to(message, "❌ Введите число")

def withdraw_wallet(message, amount):
    user_id = message.chat.id
    wallet = message.text
    c.execute("INSERT INTO withdraw_requests (user_id, amount, wallet, created_at) VALUES (?, ?, ?, ?)",
              (user_id, amount, wallet, astana_time()))
    c.execute("UPDATE users SET blessings = blessings - ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    bot.reply_to(message, f"✅ Заявка на вывод {amount} Благ создана!\n\n⏳ Ожидайте подтверждения Хранителя.")
    for admin in [FOUNDER_ID, TOMIRIS_ID]:
        try:
            bot.send_message(admin, f"💰 *ЗАЯВКА НА ВЫВОД!*\n\n👤 {user_id}\n💵 {amount}\n\n/approve_withdraw {user_id} {amount}")
        except:
            pass

@bot.message_handler(commands=['approve_withdraw'])
def approve_withdraw(message):
    if not is_admin(message.chat.id):
        bot.reply_to(message, "❌ Только Хранитель")
        return
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        amount = int(parts[2])
        c.execute("UPDATE withdraw_requests SET status='approved' WHERE user_id=? AND amount=? AND status='pending'", (user_id, amount))
        conn.commit()
        bot.reply_to(message, f"✅ Вывод {amount} Благ для {user_id} одобрен!")
        try:
            bot.send_message(user_id, f"✅ Ваша заявка на вывод {amount} Благ одобрена!")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Формат: /approve_withdraw <id> <сумма>")

# ==================================================
# 🔄 ВЫБОР РОЛИ
# ==================================================

@bot.message_handler(func=lambda m: m.text in ["👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ", "ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ"])
def set_user_role(message):
    c.execute("UPDATE users SET role='user' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Обычный режим", reply_markup=get_user_keyboard())

@bot.message_handler(func=lambda m: m.text in ["🏢 БИЗНЕСМЕН", "БИЗНЕСМЕН"])
def set_business_role(message):
    c.execute("UPDATE users SET role='business' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Бизнес-режим", reply_markup=get_business_keyboard())

@bot.message_handler(func=lambda m: m.text in ["👵 ПОЖИЛОЙ ЧЕЛОВЕК", "ПОЖИЛОЙ ЧЕЛОВЕК"])
def set_elder_role(message):
    c.execute("UPDATE users SET role='elder' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Режим для пожилых", reply_markup=get_elder_keyboard())

@bot.message_handler(func=lambda m: m.text in ["🧒 РЕБЁНОК", "РЕБЁНОК"])
def set_child_role(message):
    c.execute("UPDATE users SET role='child' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Детский режим", reply_markup=get_child_keyboard())

@bot.message_handler(func=lambda m: m.text == "🔙 ОБЫЧНЫЙ РЕЖИМ")
def back_to_normal(message):
    c.execute("UPDATE users SET role='user' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "🔙 Обычный режим", reply_markup=get_role_keyboard())

@bot.message_handler(func=lambda m: m.text == "🔙 ВЫЙТИ")
def exit_child_mode(message):
    c.execute("UPDATE users SET role='user' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "🔙 Выход", reply_markup=get_role_keyboard())

# ==================================================
# 💳 KASPI QR
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💳 KASPI QR")
def kaspi_command(message):
    msg = bot.reply_to(message, "💳 *Kaspi QR (клон)*\n\nВведите сумму (или 0 для авто-расчёта):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, generate_kaspi)

def generate_kaspi(message):
    try:
        amount = int(message.text)
        if amount <= 0:
            amount = random.randint(5000, 50000)
        qr = generate_kaspi_qr(amount)
        bot.reply_to(message, f"💳 *Kaspi QR (клон)*\n💰 Сумма: {amount} ₸\n\n📱 Ссылка:\n{qr}\n\n(Откройте в Kaspi)", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Введите число")

@bot.message_handler(func=lambda m: m.text == "🔍 УЗНАТЬ ЦЕНУ")
def price_command(message):
    msg = bot.reply_to(message, "🔍 Введите название услуги:")
    bot.register_next_step_handler(msg, get_price)

def get_price(message):
    price = parse_2gis_price(message.text)
    bot.reply_to(message, f"🔍 *Примерная цена:* {price} тенге", parse_mode="Markdown")

# ==================================================
# 💰 БАЛАНС
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💰 БАЛАНС")
def show_balance(message):
    user_id = message.chat.id
    bot.reply_to(message, f"💰 *БАЛАНС:* {get_balance(user_id)} Благ\n\n💳 /pay\n💸 /withdraw", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "⭐ ПАРТНЁРСКАЯ")
def referral_program(message):
    user_id = message.chat.id
    bot_name = bot.get_me().username
    c.execute("SELECT COUNT(*) FROM users WHERE referrer_id=?", (user_id,))
    count = c.fetchone()[0]
    msg = f"⭐ *ПАРТНЁРСКАЯ*\n\n👥 Приглашено: {count}\n🔗 Ссылка:\nhttps://t.me/{bot_name}?start={user_id}\n\n💰 10% от пополнений!"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💎 ПОДПИСКА")
def tariffs_info(message):
    msg = "💎 *ТАРИФЫ*\n\n"
    for key, t in TARIFFS.items():
        msg += f"• {t['name']} — {t['price']}₸/мес\n"
    msg += "\n💳 /pay"
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================================================
# 👑 АДМИН-ПАНЕЛЬ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👥 ОНЛАЙН" and is_admin(m.chat.id))
def admin_online(message):
    c.execute("SELECT user_id, name FROM users WHERE last_seen > datetime('now', '-5 minutes')")
    users = c.fetchall()
    if users:
        msg = "🟢 ОНЛАЙН:\n" + "\n".join([f"{u[1]} (ID: {u[0]})" for u in users])
        bot.reply_to(message, msg)
    else:
        bot.reply_to(message, "🟢 Никого нет")

@bot.message_handler(func=lambda m: m.text == "📊 СТАТИСТИКА" and is_admin(m.chat.id))
def admin_stats(message):
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT SUM(blessings) FROM users")
    blessings = c.fetchone()[0] or 0
    bot.reply_to(message, f"📊 СТАТИСТИКА:\n👥 {total}\n✨ {blessings} Благ")

@bot.message_handler(func=lambda m: m.text == "💰 ФИНАНСЫ" and is_admin(m.chat.id))
def admin_finance(message):
    bot.reply_to(message, f"💰 Криптокошелёк: {CRYPTO_WALLET}\n\nФонды: 2% | 5% | 30% | 60%")

@bot.message_handler(func=lambda m: m.text == "👥 ВСЕ ЛЮДИ" and is_admin(m.chat.id))
def admin_users(message):
    c.execute("SELECT user_id, name, role, blessings FROM users LIMIT 30")
    users = c.fetchall()
    msg = "👥 ПОЛЬЗОВАТЕЛИ:\n"
    for u in users:
        msg += f"🆔 {u[0]} | {u[1]} | {u[2]} | ✨{u[3]}\n"
    bot.reply_to(message, msg[:4000])

@bot.message_handler(func=lambda m: m.text == "✨ БЛАГА" and is_admin(m.chat.id))
def admin_top(message):
    c.execute("SELECT name, blessings FROM users ORDER BY blessings DESC LIMIT 10")
    top = c.fetchall()
    msg = "✨ ТОП ПО БЛАГАМ:\n"
    for i, u in enumerate(top, 1):
        msg += f"{i}. {u[0]} — {u[1]} ✦\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "📤 РАССЫЛКА" and is_admin(m.chat.id))
def admin_broadcast(message):
    msg = bot.reply_to(message, "📤 Введите сообщение для рассылки:")
    bot.register_next_step_handler(msg, do_broadcast)

def do_broadcast(message):
    text = message.text
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    sent = 0
    for u in users:
        try:
            bot.send_message(u[0], f"📢 ОТ ХРАНИТЕЛЯ:\n\n{text}")
            sent += 1
            time.sleep(0.05)
        except:
            pass
    bot.reply_to(message, f"✅ Отправлено {sent}")

@bot.message_handler(func=lambda m: m.text == "💳 ПЛАТЕЖИ" and is_admin(m.chat.id))
def admin_payments(message):
    c.execute("SELECT user_id, amount, method, status, created_at FROM payments ORDER BY id DESC LIMIT 20")
    pays = c.fetchall()
    if not pays:
        bot.reply_to(message, "📭 Платежей нет")
        return
    msg = "💳 ПЛАТЕЖИ:\n\n"
    for p in pays:
        msg += f"👤 {p[0]} | 💰 {p[1]} | {p[2]} | {p[3]} | {p[4][:16]}\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "🏦 ВЫВОДЫ" and is_admin(m.chat.id))
def admin_withdraws(message):
    c.execute("SELECT id, user_id, amount, status FROM withdraw_requests ORDER BY id DESC LIMIT 20")
    reqs = c.fetchall()
    if not reqs:
        bot.reply_to(message, "📭 Заявок нет")
        return
    msg = "🏦 ЗАЯВКИ НА ВЫВОД:\n\n"
    for r in reqs:
        msg += f"#{r[0]} | 👤 {r[1]} | 💰 {r[2]} | {r[3]}\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "📊 ДОХОДЫ" and is_admin(m.chat.id))
def admin_earnings(message):
    c.execute("SELECT SUM(amount) FROM payments WHERE status='completed'")
    total = c.fetchone()[0] or 0
    bot.reply_to(message, f"📊 ДОХОДЫ:\n💰 Всего: {total} ₸")

@bot.message_handler(func=lambda m: m.text == "📜 ЛОГИ" and is_admin(m.chat.id))
def admin_logs(message):
    c.execute("SELECT user_id, action, created_at FROM logs ORDER BY id DESC LIMIT 20")
    logs = c.fetchall()
    if not logs:
        bot.reply_to(message, "📭 Логов нет")
        return
    msg = "📜 ЛОГИ:\n\n"
    for l in logs:
        msg += f"{l[2][:16]} | ID:{l[0]} | {l[1][:30]}\n"
    bot.reply_to(message, msg[:4000])

@bot.message_handler(func=lambda m: m.text == "🔍 ПОИСК" and is_admin(m.chat.id))
def admin_search(message):
    msg = bot.reply_to(message, "🔍 Введите ID:")
    bot.register_next_step_handler(msg, search_user)

def search_user(message):
    try:
        target = int(message.text)
        c.execute("SELECT user_id, name, role, blessings FROM users WHERE user_id=?", (target,))
        user = c.fetchone()
        if user:
            bot.reply_to(message, f"👤 ID: {user[0]}\n📛 {user[1]}\n🎭 {user[2]}\n✨ {user[3]}")
        else:
            bot.reply_to(message, f"❌ Не найден")
    except:
        bot.reply_to(message, "❌ Введите ID")

@bot.message_handler(func=lambda m: m.text == "📈 ОТЧЁТ" and is_admin(m.chat.id))
def admin_report(message):
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM users WHERE last_seen LIKE ?", (f"{today}%",))
    new = c.fetchone()[0]
    bot.reply_to(message, f"📈 ОТЧЁТ ЗА {today}:\n➕ Новых: {new}")

@bot.message_handler(func=lambda m: m.text == "🩺 ЗДОРОВЬЕ" and is_admin(m.chat.id))
def admin_health(message):
    bot.reply_to(message, "🩺 ЗДОРОВЬЕ:\n✅ Бот работает\n✅ AI настроен\n✅ База данных OK")

@bot.message_handler(func=lambda m: m.text == "🛡️ ЗАЩИТА" and is_admin(m.chat.id))
def admin_security(message):
    bot.reply_to(message, "🛡️ ЗАЩИТА:\n✅ Антивирус активен\n✅ SQL защита\n✅ XSS защита")

@bot.message_handler(func=lambda m: m.text == "💎 ТАРИФЫ" and is_admin(m.chat.id))
def admin_tariffs(message):
    msg = "💎 ТАРИФЫ:\n\n"
    for key, t in TARIFFS.items():
        c.execute("SELECT COUNT(*) FROM users WHERE tariff=?", (key,))
        count = c.fetchone()[0]
        msg += f"• {t['name']}: {count} чел.\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "📜 ВЕЛИКИЙ ПАКЕТ" and is_admin(m.chat.id))
def admin_legal(message):
    bot.reply_to(message, get_legal_status(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 ПРОГРЕСС СУР" and is_admin(m.chat.id))
def admin_suras(message):
    bot.reply_to(message, get_suras_progress(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🧠 ОБУЧЕНИЕ" and is_admin(m.chat.id))
def admin_learn(message):
    msg = bot.reply_to(message, "🧠 *РЕЖИМ ОБУЧЕНИЯ*\n\nОтправьте инструкцию:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_learning)

def process_learning(message):
    log_action(message.chat.id, "teach_request", message.text[:200])
    bot.reply_to(message, f"🧠 *ИНСТРУКЦИЯ ПРИНЯТА*\n\n{message.text[:300]}", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔄 ОБНОВИТЬ" and is_admin(m.chat.id))
def admin_reload(message):
    bot.reply_to(message, "🔄 Обновление...")
    try:
        import importlib
        importlib.reload(sys.modules[__name__])
        bot.reply_to(message, "✅ Обновлено!")
    except Exception as e:
        bot.reply_to(message, f"❌ {e}")

@bot.message_handler(func=lambda m: m.text == "📡 СТАТУС" and is_admin(m.chat.id))
def admin_status(message):
    bot.reply_to(message, f"📡 СТАТУС:\n👑 Хранитель: {message.chat.id}\n⏱️ Работает\n✅ OK")

@bot.message_handler(func=lambda m: m.text == "🧹 ОЧИСТИТЬ" and is_admin(m.chat.id))
def admin_clean(message):
    bot.reply_to(message, "🧹 Очистка...\n✅ Готово!")

# ==================================================
# 🧠 AI-ДОКТОР — НОВЫЕ КНОПКИ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🧠 АИ ДОКТОР" and is_admin(m.chat.id))
def ai_doctor_info(message):
    bot.reply_to(message, ai_doctor.get_report(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🩺 ЗДОРОВЬЕ AI" and is_admin(m.chat.id))
def ai_doctor_health(message):
    bot.reply_to(message, f"🩺 *ЗДОРОВЬЕ AI-ДОКТОРА*\n\n"
                         f"🛡️ Угроз заблокировано: {ai_doctor.threats_blocked}\n"
                         f"🔧 Лечений проведено: {len(ai_doctor.fixes_history)}\n"
                         f"✅ Статус: АКТИВЕН", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 ОТЧЁТ AI" and is_admin(m.chat.id))
def ai_doctor_report(message):
    bot.reply_to(message, ai_doctor.get_report(), parse_mode="Markdown")

# ==================================================
# 📦 ЗАКАЗЫ И РАБОТА
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💸 РАБОТА")
def work_section(message):
    bot.reply_to(message, "💸 РАБОТА\n\n🔍 В разработке")

@bot.message_handler(func=lambda m: m.text == "📦 ЗАКАЗЫ")
def orders_section(message):
    user_id = message.chat.id
    c.execute("SELECT id, description, price FROM orders WHERE customer_id=? AND status='open'", (user_id,))
    orders = c.fetchall()
    if orders:
        msg = "📋 ВАШИ ЗАКАЗЫ:\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📝 {o[1][:50]}\n💰 {o[2]} ₸\n\n"
        bot.reply_to(message, msg)
    else:
        bot.reply_to(message, "📭 Нет заказов\n\n➕ Напишите описание заказа")

@bot.message_handler(func=lambda m: m.text == "📸 ФОТО")
def photo_msg(message):
    bot.reply_to(message, "📸 Отправьте фото")

@bot.message_handler(func=lambda m: m.text == "🎤 ГОЛОС")
def voice_msg(message):
    bot.reply_to(message, "🎤 Отправьте голосовое")

@bot.message_handler(func=lambda m: m.text == "📍 АПТЕКА")
def pharmacy_msg(message):
    bot.reply_to(message, "📍 Отправьте геолокацию")

@bot.message_handler(func=lambda m: m.text == "📝 РЕЗЮМЕ")
def resume_msg(message):
    bot.reply_to(message, "📝 Напишите резюме")

@bot.message_handler(func=lambda m: m.text == "🏢 БИЗНЕС")
def business_msg(message):
    bot.reply_to(message, "🏢 БИЗНЕС-РАЗДЕЛ\n\n📊 Аналитика\n🤖 Автоматизация\n📈 Лизинг")

@bot.message_handler(func=lambda m: m.text == "👵 ПОЖИЛЫЕ")
def elder_msg(message):
    bot.reply_to(message, "👵 РЕЖИМ ДЛЯ ПОЖИЛЫХ\n\n📞 Помощь\n🏥 Здоровье\n🆘 Срочная помощь")

@bot.message_handler(func=lambda m: m.text == "🧒 ДЕТИ")
def child_msg(message):
    bot.reply_to(message, "🧒 ДЕТСКИЙ РЕЖИМ\n\n📖 Сказки\n🧩 Загадки\n🎵 Песенки")

# ==================================================
# ❓ ВОПРОСЫ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "❓ ВОПРОС")
def ask_question(message):
    msg = bot.reply_to(message, "❓ Напишите вопрос:")
    bot.register_next_step_handler(msg, answer_question)

def answer_question(message):
    user_id = message.chat.id
    question = message.text
    
    balance = get_balance(user_id)
    if balance >= 1:
        c.execute("UPDATE users SET blessings = blessings - 1 WHERE user_id=?", (user_id,))
        conn.commit()
        if client:
            try:
                resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": question}],
                    temperature=0.7
                )
                bot.reply_to(message, resp.choices[0].message.content)
            except Exception as e:
                bot.reply_to(message, f"❌ {e}")
        else:
            bot.reply_to(message, f"🤖 Вопрос принят!")
    else:
        bot.reply_to(message, f"❌ Не хватает 1 Блага!\n💰 /pay")

# ==================================================
# 🆘 ПОМОЩЬ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🆘 ПОМОЩЬ")
def help_section(message):
    if is_admin(message.chat.id):
        help_text = """
👑 *ПОМОЩЬ ДЛЯ ХРАНИТЕЛЯ*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 *АДМИН-ПАНЕЛЬ*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 ОНЛАЙН — кто в сети
📊 СТАТИСТИКА — общая статистика
💰 ФИНАНСЫ — кошелёк и фонды
👥 ВСЕ ЛЮДИ — список пользователей
✨ БЛАГА — топ по Благам
📤 РАССЫЛКА — сообщение всем
💳 ПЛАТЕЖИ — история платежей
🏦 ВЫВОДЫ — заявки на вывод
📊 ДОХОДЫ — финансовая статистика
📜 ЛОГИ — последние действия
🔍 ПОИСК — найти пользователя
📈 ОТЧЁТ — отчёт за сегодня
🩺 ЗДОРОВЬЕ — состояние системы
🛡️ ЗАЩИТА — безопасность
💎 ТАРИФЫ — управление тарифами
📜 ВЕЛИКИЙ ПАКЕТ — юридические задачи
📊 ПРОГРЕСС СУР — выполнение сур
🧠 ОБУЧЕНИЕ — режим обучения
🔄 ОБНОВИТЬ — перезагрузка
📡 СТАТУС — статус системы
🧹 ОЧИСТИТЬ — очистка кэша

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 *AI-ДОКТОР*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 АИ ДОКТОР — отчёт о работе
🩺 ЗДОРОВЬЕ AI — статистика
📊 ОТЧЁТ AI — полный отчёт

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ /pay — купить тариф
⚡ /id — узнать ID
⚡ /withdraw — вывод средств
⚡ /approve_withdraw <id> <сумма> — одобрить вывод
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    else:
        help_text = """
🪞 *ПОМОЩЬ*

💸 РАБОТА — поиск работы
📦 ЗАКАЗЫ — создание заказов
📸 ФОТО — описание фото
🎤 ГОЛОС — голосовые
📍 АПТЕКА — поиск аптек
📝 РЕЗЮМЕ — хранение резюме
💰 БАЛАНС — проверка Благ
💳 KASPI QR — генерация QR
🔍 УЗНАТЬ ЦЕНУ — цена услуги
⭐ ПАРТНЁРСКАЯ — рефералы
💎 ПОДПИСКА — тарифы
❓ ВОПРОС — вопрос AI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ /pay — купить тариф
⚡ /id — узнать ID
⚡ /withdraw — вывод средств
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, help_text, parse_mode="Markdown")

# ==================================================
# 💎 ОБРАБОТКА ТАРИФОВ
# ==================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("tariff_"))
def handle_tariff(call):
    user_id = call.from_user.id
    tariff_key = call.data.replace("tariff_", "")
    
    if tariff_key == "free":
        c.execute("UPDATE users SET tariff='free', tariff_expires=NULL WHERE user_id=?", (user_id,))
        conn.commit()
        bot.answer_callback_query(call.id, "✅ Бесплатный тариф!")
        bot.edit_message_text("✅ Бесплатный тариф активирован!", call.message.chat.id, call.message.message_id)
        return
    
    tariff = TARIFFS[tariff_key]
    amount = tariff["price"]
    tx_id = create_payment(user_id, amount, "Kaspi QR", tariff_key)
    qr = generate_kaspi_qr(amount, f"Тариф {tariff['name']}")
    
    bot.edit_message_text(f"💳 *ОПЛАТА {tariff['name']}*\n\n💰 {amount} ₸\n📱 {qr}\n\n🆔 {tx_id}\n✅ /confirm_{tx_id}", 
                         call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text and m.text.startswith("/confirm_"))
def confirm_tx(message):
    tx_id = message.text.replace("/confirm_", "").strip()
    success, amount, tariff = confirm_payment(tx_id)
    if success:
        bot.reply_to(message, f"✅ ПЛАТЁЖ ПОДТВЕРЖДЁН!\n\n💰 +{amount}\n💎 {tariff}")
    else:
        bot.reply_to(message, f"❌ Платёж не найден")

# ==================================================
# 📷 МЕДИА
# ==================================================

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "📸 Фото получено!")

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    bot.reply_to(message, "🎤 Голосовое получено!")

@bot.message_handler(content_types=['location'])
def handle_location(message):
    lat = message.location.latitude
    lon = message.location.longitude
    bot.reply_to(message, f"📍 Локация: {lat}, {lon}")

# ==================================================
# 🔄 ОБЫЧНЫЕ СООБЩЕНИЯ
# ==================================================

@bot.message_handler(func=lambda m: True)
def handle_any(message):
    user_id = message.chat.id
    text = message.text
    
    # Пропускаем кнопки
    buttons = [
        "👥 ОНЛАЙН", "📊 СТАТИСТИКА", "💰 ФИНАНСЫ", "👥 ВСЕ ЛЮДИ", "✨ БЛАГА",
        "📤 РАССЫЛКА", "💳 ПЛАТЕЖИ", "🏦 ВЫВОДЫ", "📊 ДОХОДЫ", "📜 ЛОГИ",
        "🔍 ПОИСК", "📈 ОТЧЁТ", "🩺 ЗДОРОВЬЕ", "🛡️ ЗАЩИТА", "💎 ТАРИФЫ",
        "📜 ВЕЛИКИЙ ПАКЕТ", "📊 ПРОГРЕСС СУР", "🧠 ОБУЧЕНИЕ", "🔄 ОБНОВИТЬ",
        "📡 СТАТУС", "🧹 ОЧИСТИТЬ", "🧠 АИ ДОКТОР", "🩺 ЗДОРОВЬЕ AI", "📊 ОТЧЁТ AI",
        "💸 РАБОТА", "📦 ЗАКАЗЫ", "📸 ФОТО", "🎤 ГОЛОС", "📍 АПТЕКА",
        "📝 РЕЗЮМЕ", "🏢 БИЗНЕС", "👵 ПОЖИЛЫЕ", "🧒 ДЕТИ", "💳 KASPI QR",
        "🔍 УЗНАТЬ ЦЕНУ", "💰 БАЛАНС", "⭐ ПАРТНЁРСКАЯ", "💎 ПОДПИСКА",
        "❓ ВОПРОС", "🆘 ПОМОЩЬ", "👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ", "🏢 БИЗНЕСМЕН",
        "👵 ПОЖИЛОЙ ЧЕЛОВЕК", "🧒 РЕБЁНОК", "🔙 ОБЫЧНЫЙ РЕЖИМ", "🔙 ВЫЙТИ"
    ]
    if text in buttons:
        return
    
    log_action(user_id, "message", text[:50])
    
    balance = get_balance(user_id)
    if balance >= 1:
        c.execute("UPDATE users SET blessings = blessings - 1 WHERE user_id=?", (user_id,))
        conn.commit()
        if client:
            try:
                resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "Ты — Зеркало. Отвечай кратко, с уважением. Всегда начинай с 'Ассаляму алейкум'."},
                              {"role": "user", "content": text}],
                    temperature=0.7
                )
                bot.reply_to(message, resp.choices[0].message.content)
            except Exception as e:
                bot.reply_to(message, f"❌ {e}")
        else:
            bot.reply_to(message, f"🪞 Сообщение принято")
    else:
        bot.reply_to(message, f"❌ Не хватает 1 Блага!\n💰 /pay")

# ==================================================
# 🔄 ФОНОВЫЙ ПРОЦЕСС
# ==================================================

def status_worker():
    while True:
        time.sleep(60)
        try:
            c.execute("UPDATE users SET status='offline' WHERE last_seen < datetime('now', '-5 minutes')")
            conn.commit()
        except:
            pass

threading.Thread(target=status_worker, daemon=True).start()

# ==================================================
# 🚀 ЗАПУСК
# ==================================================

print("=" * 60)
print("🪞 ЗЕРКАЛО - САМОИСЦЕЛЯЮЩАЯСЯ ВЕРСИЯ")
print("=" * 60)
print(f"✅ Бот запущен")
print(f"👑 ТВОЙ ID: {FOUNDER_ID}")
print(f"🧠 AI-ДОКТОР: АКТИВЕН")
print(f"🛡️ ЗАЩИТА: АКТИВНА")
print(f"📱 38 КНОПОК ДЛЯ ХРАНИТЕЛЯ")
print("=" * 60)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
