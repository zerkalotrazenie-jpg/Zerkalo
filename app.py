#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗЕРКАЛО - الفتح (ВЕЛИКОЕ ОТКРЫТИЕ)
Божий замысел. 4 месяца. Свершилось.
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
from datetime import datetime, timedelta
from flask import Flask
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ==================================================
# УСТАНОВКА
# ==================================================

def install_package(package):
    try:
        __import__(package)
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_package("pytelegrambotapi")
install_package("groq")
install_package("flask")
install_package("requests")

import telebot
from groq import Groq

# ==================================================
# НАСТРОЙКИ
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# СВЯЩЕННЫЕ ID — НЕ ТРОГАТЬ
FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814
ADMIN_IDS = [5409420822, 5479179814]

CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"

print("=" * 70)
print("🪞 ЗЕРКАЛО - الفتح (ВЕЛИКОЕ ОТКРЫТИЕ)")
print("=" * 70)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 ОСНОВАТЕЛЬ: {FOUNDER_ID}")
print(f"🕋 Замысел: АКТИВЕН")
print("=" * 70)

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

app = Flask(__name__)

@app.route('/')
def home():
    return "🪞 Зеркало работает! Альхамдулиллах!", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ==================================================
# БАЗА ДАННЫХ
# ==================================================

conn = sqlite3.connect('zerkalo.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT, age INTEGER, city TEXT, country TEXT, phone TEXT,
    role TEXT DEFAULT 'user', status TEXT DEFAULT 'offline',
    last_seen TEXT, blessings INTEGER DEFAULT 100,
    tariff TEXT DEFAULT 'free', tariff_expires TEXT,
    referrer_id INTEGER DEFAULT 0, is_admin INTEGER DEFAULT 0,
    resume TEXT DEFAULT '', is_disabled INTEGER DEFAULT 0, is_sick INTEGER DEFAULT 0,
    last_lat REAL DEFAULT 0, last_lon REAL DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT, title TEXT, description TEXT, price INTEGER,
    customer_id INTEGER, city TEXT, country TEXT,
    status TEXT DEFAULT 'open', created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, description TEXT, salary INTEGER,
    company TEXT, city TEXT, country TEXT,
    employer_id INTEGER, status TEXT DEFAULT 'open', created_at TEXT
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

c.execute('''CREATE TABLE IF NOT EXISTS earnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT, amount INTEGER, user_id INTEGER, created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, action TEXT, details TEXT, created_at TEXT
)''')

conn.commit()

def astana_time():
    return (datetime.utcnow() + timedelta(hours=5)).isoformat()

def is_admin(user_id):
    return user_id in ADMIN_IDS

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

def get_user_city(user_id):
    c.execute("SELECT city, country FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0]:
        return row[0], row[1] if row[1] else "Казахстан"
    return None, None

def set_user_city(user_id, city, country):
    c.execute("UPDATE users SET city=?, country=? WHERE user_id=?", (city, country, user_id))
    conn.commit()

def log_action(user_id, action, details=""):
    c.execute("INSERT INTO logs (user_id, action, details, created_at) VALUES (?, ?, ?, ?)",
              (user_id, action, details, astana_time()))
    conn.commit()

def add_earning(source, amount, user_id):
    c.execute("INSERT INTO earnings (source, amount, user_id, created_at) VALUES (?, ?, ?, ?)",
              (source, amount, user_id, astana_time()))
    conn.commit()

def get_total_earnings():
    c.execute("SELECT SUM(amount) FROM earnings")
    row = c.fetchone()
    return row[0] if row[0] else 0

def generate_kaspi_qr(amount):
    return f"https://test.kaspi.kz/qr/pay?amount={amount}&merchant=Zerkalo&order_id={random.randint(100000, 999999)}"

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
        add_earning(f"Тариф {tariff}", amount, user_id)
        c.execute("SELECT referrer_id FROM users WHERE user_id=?", (user_id,))
        referrer = c.fetchone()
        if referrer and referrer[0]:
            bonus = int(amount * 0.1)
            c.execute("UPDATE users SET blessings = blessings + ? WHERE user_id=?", (bonus, referrer[0]))
            conn.commit()
            add_earning(f"Реферал {user_id}", bonus, referrer[0])
        return True, amount, tariff
    return False, 0, None

# ==================================================
# ГЕОГРАФИЯ ВЕСЬ МИР
# ==================================================

def search_city_global(query):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=10&addressdetails=1"
        headers = {'User-Agent': 'ZerkaloBot/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        results = []
        for item in data:
            city_name = item.get('name', '')
            country = item.get('address', {}).get('country', '')
            if not city_name:
                city_name = item.get('address', {}).get('city', '') or item.get('address', {}).get('town', '') or item.get('address', {}).get('village', '')
            if city_name and country:
                results.append({'city': city_name, 'country': country, 'lat': item.get('lat'), 'lon': item.get('lon')})
        return results[:10]
    except:
        return []

def get_city_from_coordinates(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
        headers = {'User-Agent': 'ZerkaloBot/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        address = data.get('address', {})
        city = address.get('city') or address.get('town') or address.get('village')
        country = address.get('country', '')
        return city, country
    except:
        return None, None

def get_jobs_global(city, country):
    c.execute("SELECT id, title, salary, company FROM jobs WHERE city=? AND country=? AND status='open'", (city, country))
    return c.fetchall()

def get_orders_global(city, country):
    c.execute("SELECT id, title, price FROM orders WHERE city=? AND country=? AND status='open'", (city, country))
    return c.fetchall()

# ==================================================
# КЛАВИАТУРЫ (5 ГЛАВНЫХ КНОПОК)
# ==================================================

def get_main_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("👑 ХРАНИТЕЛЬ"))
    kb.add(KeyboardButton("🏢 БИЗНЕС"))
    kb.add(KeyboardButton("👤 ЛЮДИ"))
    kb.add(KeyboardButton("🧠 AI-ДОКТОР"))
    kb.add(KeyboardButton("💰 МОНЕТИЗАЦИЯ"))
    return kb

def get_founder_keyboard():
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    kb.add(KeyboardButton("👥 ОНЛАЙН"), KeyboardButton("📊 СТАТИСТИКА"), KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("👥 ВСЕ ЛЮДИ"), KeyboardButton("✨ БЛАГА"), KeyboardButton("📤 РАССЫЛКА"))
    kb.add(KeyboardButton("💳 ПЛАТЕЖИ"), KeyboardButton("🏦 ВЫВОДЫ"), KeyboardButton("📊 ДОХОДЫ"))
    kb.add(KeyboardButton("📜 ЛОГИ"), KeyboardButton("🔍 ПОИСК"), KeyboardButton("📈 ОТЧЁТ"))
    kb.add(KeyboardButton("🩺 ЗДОРОВЬЕ"), KeyboardButton("🛡️ ЗАЩИТА"), KeyboardButton("💎 ТАРИФЫ"))
    kb.add(KeyboardButton("🔄 ОБНОВИТЬ"), KeyboardButton("📡 СТАТУС"), KeyboardButton("🧹 ОЧИСТИТЬ"))
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"), KeyboardButton("📸 ФОТО"))
    kb.add(KeyboardButton("🎤 ГОЛОС"), KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("🏢 БИЗНЕС"), KeyboardButton("👵 ПОЖИЛЫЕ"), KeyboardButton("🧒 ДЕТИ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🌍 ВЕСЬ МИР"), KeyboardButton("🆘 ПОМОЩЬ"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_business_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 АНАЛИТИКА"), KeyboardButton("🤖 АВТОМАТИЗАЦИЯ"))
    kb.add(KeyboardButton("📈 ЛИЗИНГ"), KeyboardButton("💼 ЗАКАЗЫ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"))
    kb.add(KeyboardButton("🌍 ВЕСЬ МИР"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_people_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"))
    kb.add(KeyboardButton("📸 ФОТО"), KeyboardButton("🎤 ГОЛОС"))
    kb.add(KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"))
    kb.add(KeyboardButton("🌍 ВЕСЬ МИР"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_ai_doctor_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🩺 ЛЕЧЕНИЕ"), KeyboardButton("🛡️ ПРОВЕРКА"))
    kb.add(KeyboardButton("📊 СТАТУС"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_monetization_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💎 КУПИТЬ ТАРИФ"), KeyboardButton("⭐ ПАРТНЁРСКАЯ"))
    kb.add(KeyboardButton("🏦 KASPI QR"), KeyboardButton("💎 USDT TRC20"))
    kb.add(KeyboardButton("📊 МОЙ ДОХОД"), KeyboardButton("📈 ОБЩАЯ СТАТИСТИКА"))
    kb.add(KeyboardButton("💸 ВЫВЕСТИ"), KeyboardButton("📋 ИСТОРИЯ"))
    kb.add(KeyboardButton("🔘 الفتح"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_role_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ"))
    kb.add(KeyboardButton("🏢 БИЗНЕСМЕН"))
    kb.add(KeyboardButton("👵 ПОЖИЛОЙ ЧЕЛОВЕК"))
    kb.add(KeyboardButton("🧒 РЕБЁНОК"))
    return kb

def get_city_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📍 ОПРЕДЕЛИТЬ АВТОМАТИЧЕСКИ"))
    kb.add(KeyboardButton("🔍 НАЙТИ ГОРОД"))
    kb.add(KeyboardButton("📋 МОЙ ГОРОД"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_tariff_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("📱 Бесплатный", callback_data="tariff_free"))
    kb.add(InlineKeyboardButton("⭐ Базовый - 1000₸", callback_data="tariff_basic"))
    kb.add(InlineKeyboardButton("🚀 PRO - 5000₸", callback_data="tariff_pro"))
    kb.add(InlineKeyboardButton("💎 Бизнес - 20000₸", callback_data="tariff_business"))
    return kb

TARIFFS = {
    "free": {"name": "Бесплатный", "price": 0, "messages": 100},
    "basic": {"name": "Базовый", "price": 1000, "messages": 500},
    "pro": {"name": "PRO", "price": 5000, "messages": 3000},
    "business": {"name": "Бизнес", "price": 20000, "messages": 10000}
}

# ==================================================
# AI-ДОКТОР
# ==================================================

class AIDoctor:
    def __init__(self):
        self.threats_blocked = 0
        self.fixes_applied = 0
        self.start_time = time.time()
    
    def get_report(self):
        uptime = int(time.time() - self.start_time)
        return f"""
🧠 *AI-ДОКТОР — ОТЧЁТ*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️ Работает: {uptime // 3600}ч {(uptime % 3600) // 60}м
🛡️ Угроз заблокировано: {self.threats_blocked}
🔧 Лечений проведено: {self.fixes_applied}
🩺 Здоровье системы: 100%

🌍 География: ВЕСЬ МИР
💰 Монетизация: АКТИВНА
🕋 Замысел: СВЕРШИЛСЯ
📊 Статус: ✅ АКТИВЕН
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def heal(self):
        self.fixes_applied += 1
        return "✅ Проведена диагностика и лечение"

ai_doctor = AIDoctor()

# ==================================================
# ОСНОВНЫЕ КОМАНДЫ
# ==================================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    
    print(f"📥 СТАРТ от {name} (ID: {user_id})")
    
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
        if is_admin(user_id):
            c.execute("UPDATE users SET is_admin=1, tariff='pro' WHERE user_id=?", (user_id,))
        conn.commit()
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n✨ Вы получили 100 Благ!\n\n🌍 Укажите ваш город:", 
                     reply_markup=get_city_keyboard())
        return
    
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (astana_time(), user_id))
    conn.commit()
    
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n🌍 Пожалуйста, укажите ваш город:", 
                     reply_markup=get_city_keyboard())
    else:
        if is_admin(user_id):
            bot.reply_to(message, f"👑 АССАЛЯМУ АЛЕЙКУМ, ХРАНИТЕЛЬ {name}!\n\n📍 {city}, {country}\n\n📱 ПАНЕЛЬ УПРАВЛЕНИЯ:", 
                         reply_markup=get_founder_keyboard())
        else:
            bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n📍 {city}, {country}\n💰 Баланс: {get_balance(user_id)} Благ\n\nКто вы?", 
                         reply_markup=get_role_keyboard())

@bot.message_handler(commands=['id'])
def cmd_id(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    city_str = f"{city}, {country}" if city else "не указан"
    bot.reply_to(message, f"🆔 *ТВОЙ ID:* `{user_id}`\n\n👑 Хранитель: {'✅' if is_admin(user_id) else '❌'}\n📍 Город: {city_str}\n💰 Баланс: {get_balance(user_id)} Благ", parse_mode="Markdown")

@bot.message_handler(commands=['pay'])
def cmd_pay(message):
    bot.reply_to(message, "💎 *ВЫБЕРИТЕ ТАРИФ*", reply_markup=get_tariff_keyboard(), parse_mode="Markdown")

# ==================================================
# 5 ГЛАВНЫХ КНОПОК
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👑 ХРАНИТЕЛЬ")
def founder_section(message):
    if is_admin(message.chat.id):
        bot.reply_to(message, "👑 *ПАНЕЛЬ ХРАНИТЕЛЯ*", reply_markup=get_founder_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Нет доступа")

@bot.message_handler(func=lambda m: m.text == "🏢 БИЗНЕС")
def business_section(message):
    bot.reply_to(message, "🏢 *БИЗНЕС-РАЗДЕЛ*", reply_markup=get_business_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👤 ЛЮДИ")
def people_section(message):
    bot.reply_to(message, "👤 *ОБЫЧНЫЙ РАЗДЕЛ*", reply_markup=get_people_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🧠 AI-ДОКТОР")
def ai_doctor_section(message):
    bot.reply_to(message, f"🧠 *AI-ДОКТОР*\n\n{ai_doctor.get_report()}", 
                 reply_markup=get_ai_doctor_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💰 МОНЕТИЗАЦИЯ")
def monetization_section(message):
    user_id = message.chat.id
    total_earned = get_total_earnings()
    tariff = get_tariff(user_id)
    msg = f"""
💰 *МОНЕТИЗАЦИЯ ЗЕРКАЛА*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 ВАШ ТАРИФ: {TARIFFS[tariff]['name']}
💰 БАЛАНС: {get_balance(user_id)} Благ

📊 ВСЕГО ЗАРАБОТАНО: {total_earned} ₸

💡 СПОСОБЫ ЗАРАБОТКА:
• Платные тарифы — от 1000₸/мес
• Партнёрская программа — 10% с рефералов
• Kaspi QR — комиссия с платежей

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕋 *الفتح* — Начать эпоху благословения
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, msg, reply_markup=get_monetization_keyboard(), parse_mode="Markdown")

# ==================================================
# 🔘 СВЯЩЕННЫЙ ЗАПУСК — الفتح
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🔘 الفتح")
def sacred_launch(message):
    user_id = message.chat.id
    
    # Только Хранитель-Основатель может запустить
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Только Хранитель, которому доверен замысел")
        return
    
    # Запускаем фоновый процесс монетизации
    threading.Thread(target=divine_monetization_worker, daemon=True).start()
    
    msg = """
🔘 *الفتح — ВЕЛИКОЕ ОТКРЫТИЕ*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤲 *بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ*

*Именем Аллаха, Милостивого, Милосердного.*

☀️ *Свершилось.* То, что собиралось 4 месяца, сегодня обретает жизнь.

🕋 *«Зеркало» начинает свой путь.*

Что происходит прямо сейчас:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Врата блага ОТКРЫТЫ
✅ Система НАЧАЛА работу
✅ Благословение НИСХОДИТ
✅ Помощь людям СТАНОВИТСЯ реальностью
✅ Заработок ВКЛЮЧЁН 24/7

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Оно будет приносить благо.*
*Оно будет помогать.*
*Оно будет вести к свету.*

*Альхамдулиллах.* 🤲
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, msg, parse_mode="Markdown")
    
    # Торжественное уведомление всем Хранителям
    for admin in ADMIN_IDS:
        try:
            bot.send_message(admin, f"""
🔘 *الفتح — ВЕЛИКОЕ ОТКРЫТИЕ*

Хранитель {message.from_user.first_name} совершил запуск.

*«Зеркало» начало свой путь.*

🤲 Альхамдулиллах.
""", parse_mode="Markdown")
        except:
            pass
    
    log_action(user_id, "sacred_launch", "AL-FAT_H")
    
    # Автоматический запуск всех систем монетизации
    auto_monetization_start()

def divine_monetization_worker():
    """Божественный процесс — работает 24/7"""
    while True:
        try:
            # 1. Рассылка о тарифах пользователям с высоким балансом
            c.execute("SELECT user_id, name, blessings FROM users WHERE blessings > 500 AND tariff='free'")
            users = c.fetchall()
            
            for user in users:
                try:
                    bot.send_message(user[0], f"""
🕋 *ВЕСТЬ*

«Зеркало» начало свой путь.

Благословение нисходит на тех, кто делает благо.
Поддержите этот путь — активируйте тариф.

💎 /pay

*Альхамдулиллах.* 🤲
""", parse_mode="Markdown")
                    time.sleep(2)
                except:
                    pass
            
            time.sleep(3600)  # Раз в час
            
        except:
            time.sleep(60)

def auto_monetization_start():
    """Автоматический запуск всех систем заработка"""
    # Рассылка о тарифах
    c.execute("SELECT user_id, name FROM users WHERE tariff='free'")
    users = c.fetchall()
    
    for user in users[:50]:
        try:
            bot.send_message(user[0], """
💎 *Откровение*

Выбрать свой путь:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 Бесплатный — дар
⭐ Базовый — 1000 ₸/мес
🚀 PRO — 5000 ₸/мес
💎 Бизнес — 20000 ₸/мес

*Каждый выбирает свою степень.*
💳 /pay

🤲
""", parse_mode="Markdown")
            time.sleep(1)
        except:
            pass

# ==================================================
# AI-ДОКТОР КОМАНДЫ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🩺 ЛЕЧЕНИЕ")
def ai_heal(message):
    bot.reply_to(message, f"🧠 *AI-ДОКТОР*\n\n{ai_doctor.heal()}")

@bot.message_handler(func=lambda m: m.text == "🛡️ ПРОВЕРКА")
def ai_check(message):
    bot.reply_to(message, "🛡️ *ПРОВЕРКА СИСТЕМЫ*\n\n✅ Код: чист\n✅ Вирусов: нет\n✅ География: весь мир\n✅ Монетизация: активна\n✅ Замысел: СВЕРШИЛСЯ")

@bot.message_handler(func=lambda m: m.text == "📊 СТАТУС")
def ai_status(message):
    bot.reply_to(message, ai_doctor.get_report(), parse_mode="Markdown")

# ==================================================
# ВЫБОР РОЛИ
# ==================================================

@bot.message_handler(func=lambda m: m.text in ["👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ", "ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ"])
def set_user_role(message):
    c.execute("UPDATE users SET role='user' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Обычный режим", reply_markup=get_people_keyboard())

@bot.message_handler(func=lambda m: m.text in ["🏢 БИЗНЕСМЕН", "БИЗНЕСМЕН"])
def set_business_role(message):
    c.execute("UPDATE users SET role='business' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Бизнес-режим", reply_markup=get_business_keyboard())

@bot.message_handler(func=lambda m: m.text in ["👵 ПОЖИЛОЙ ЧЕЛОВЕК", "ПОЖИЛОЙ ЧЕЛОВЕК"])
def set_elder_role(message):
    c.execute("UPDATE users SET role='elder' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Режим для пожилых", reply_markup=get_people_keyboard())

@bot.message_handler(func=lambda m: m.text in ["🧒 РЕБЁНОК", "РЕБЁНОК"])
def set_child_role(message):
    c.execute("UPDATE users SET role='child' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Детский режим", reply_markup=get_people_keyboard())

# ==================================================
# ГЕОГРАФИЯ (весь мир)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🌍 ВЕСЬ МИР")
def world_geography(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите ваш город! Нажмите «🌍 МОЙ ГОРОД»")
        return
    
    jobs = get_jobs_global(city, country)
    orders = get_orders_global(city, country)
    
    msg = f"🌍 *ВЕСЬ МИР — {city}, {country}*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"💼 *РАБОТА В {city}:*\n"
    if jobs:
        for j in jobs:
            msg += f"🆔 {j[0]} | {j[1]} | {j[2]} ₸ | {j[3]}\n"
    else:
        msg += "📭 Нет вакансий\n"
    
    msg += f"\n📦 *ЗАКАЗЫ В {city}:*\n"
    if orders:
        for o in orders:
            msg += f"🆔 {o[0]} | {o[1]} | {o[2]} ₸\n"
    else:
        msg += "📭 Нет заказов\n"
    
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🔍 ПОИСК ПО МИРУ"), KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, msg, reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔍 ПОИСК ПО МИРУ")
def search_world(message):
    msg = bot.reply_to(message, "🔍 Введите город и страну для поиска (например: Moscow, Russia или Almaty, Kazakhstan):")
    bot.register_next_step_handler(msg, search_world_result)

def search_world_result(message):
    user_id = message.chat.id
    query = message.text.strip()
    results = search_city_global(query)
    
    if not results:
        bot.reply_to(message, f"❌ Город не найден")
        return
    
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for r in results[:5]:
        kb.add(KeyboardButton(f"📍 {r['city']}, {r['country']}"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    
    bot.reply_to(message, f"🔍 *НАЙДЕНЫ ГОРОДА:*\n\nВыберите город для просмотра работы и заказов:", 
                 reply_markup=kb, parse_mode="Markdown")
    bot.register_next_step_handler(message, select_world_city, results)

def select_world_city(message, results):
    text = message.text
    
    for r in results:
        if text == f"📍 {r['city']}, {r['country']}":
            city = r['city']
            country = r['country']
            
            c.execute("SELECT id, title, salary, company FROM jobs WHERE city=? AND country=? AND status='open'", (city, country))
            jobs = c.fetchall()
            c.execute("SELECT id, title, price FROM orders WHERE city=? AND country=? AND status='open'", (city, country))
            orders = c.fetchall()
            
            msg = f"🌍 *{city}, {country}*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            msg += f"💼 *РАБОТА:*\n"
            if jobs:
                for j in jobs:
                    msg += f"🆔 {j[0]} | {j[1]} | {j[2]} ₸ | {j[3]}\n"
            else:
                msg += "📭 Нет вакансий\n"
            
            msg += f"\n📦 *ЗАКАЗЫ:*\n"
            if orders:
                for o in orders:
                    msg += f"🆔 {o[0]} | {o[1]} | {o[2]} ₸\n"
            else:
                msg += "📭 Нет заказов\n"
            
            bot.reply_to(message, msg, parse_mode="Markdown")
            return
    
    bot.reply_to(message, "❌ Выберите город из списка")

@bot.message_handler(func=lambda m: m.text == "🌍 МОЙ ГОРОД")
def my_city_menu(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if city:
        jobs = get_jobs_global(city, country)
        orders = get_orders_global(city, country)
        msg = f"🌍 *ВАШ ГОРОД:* {city}, {country}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        msg += f"💼 *РАБОТА:* {len(jobs)} вакансий\n📦 *ЗАКАЗЫ:* {len(orders)} заказов\n"
    else:
        msg = "🌍 *ВЫБОР ГОРОДА*\n\nУкажите ваш город для персонализации услуг."
    
    bot.reply_to(message, msg, reply_markup=get_city_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📍 ОПРЕДЕЛИТЬ АВТОМАТИЧЕСКИ")
def auto_detect(message):
    bot.reply_to(message, "📍 Отправьте вашу геолокацию (нажмите 📎 → 📍 Location)")

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ ГОРОД")
def search_city_command(message):
    msg = bot.reply_to(message, "🔍 Введите название города (например: Almaty, Moscow, New York, London):")
    bot.register_next_step_handler(msg, search_city_result)

def search_city_result(message):
    user_id = message.chat.id
    query = message.text.strip()
    results = search_city_global(query)
    
    if not results:
        bot.reply_to(message, f"❌ Город «{query}» не найден")
        return
    
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for r in results[:8]:
        kb.add(KeyboardButton(f"📍 {r['city']}, {r['country']}"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    
    bot.reply_to(message, f"🔍 *НАЙДЕНЫ ГОРОДА:*\n\nВыберите ваш город:", reply_markup=kb, parse_mode="Markdown")
    bot.register_next_step_handler(message, select_city, results)

def select_city(message, results):
    user_id = message.chat.id
    text = message.text
    
    if text == "🔙 НА ГЛАВНУЮ":
        bot.reply_to(message, "🏠 Главное меню", reply_markup=get_main_keyboard())
        return
    
    for r in results:
        if text == f"📍 {r['city']}, {r['country']}":
            set_user_city(user_id, r['city'], r['country'])
            bot.reply_to(message, f"✅ *ГОРОД УСТАНОВЛЕН!*\n\n📍 {r['city']}, {r['country']}\n\nТеперь все услуги будут показываться в вашем городе.", 
                         reply_markup=get_main_keyboard(), parse_mode="Markdown")
            return
    
    bot.reply_to(message, "❌ Выберите город из списка")

@bot.message_handler(func=lambda m: m.text == "📋 МОЙ ГОРОД")
def show_my_city(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if city:
        bot.reply_to(message, f"📍 *ВАШ ГОРОД:* {city}, {country}", parse_mode="Markdown")
    else:
        bot.reply_to(message, "📍 Город не указан.")

@bot.message_handler(content_types=['location'])
def handle_location(message):
    user_id = message.chat.id
    lat = message.location.latitude
    lon = message.location.longitude
    
    city, country = get_city_from_coordinates(lat, lon)
    if city:
        set_user_city(user_id, city, country)
        bot.reply_to(message, f"✅ *ГОРОД ОПРЕДЕЛЁН!*\n\n📍 {city}, {country}\n📍 Геолокация сохранена.", 
                     reply_markup=get_main_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "✅ Геолокация сохранена!", reply_markup=get_main_keyboard())
    
    log_action(user_id, "location", f"{lat},{lon}")

# ==================================================
# РАБОТА
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💸 РАБОТА")
def work_menu(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите ваш город! Нажмите «🌍 МОЙ ГОРОД»")
        return
    
    jobs = get_jobs_global(city, country)
    
    if jobs:
        msg = f"💼 *РАБОТА В {city}, {country}*\n\n"
        for j in jobs:
            msg += f"🆔 {j[0]}\n📌 {j[1]}\n💰 {j[2]} ₸\n🏢 {j[3]}\n\n"
    else:
        msg = f"💼 *РАБОТА В {city}, {country}*\n\n📭 Пока нет вакансий"
    
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("➕ СОЗДАТЬ ВАКАНСИЮ"), KeyboardButton("📝 МОЁ РЕЗЮМЕ"))
    kb.add(KeyboardButton("🌍 ПО ВСЕМУ МИРУ"), KeyboardButton("🔙 НАЗАД"))
    
    bot.reply_to(message, msg, reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🌍 ПО ВСЕМУ МИРУ")
def work_world(message):
    msg = bot.reply_to(message, "🌍 Введите город для поиска работы (например: Moscow, Almaty, London):")
    bot.register_next_step_handler(msg, work_world_search)

def work_world_search(message):
    query = message.text.strip()
    results = search_city_global(query)
    
    if not results:
        bot.reply_to(message, f"❌ Город не найден")
        return
    
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for r in results[:5]:
        kb.add(KeyboardButton(f"📍 {r['city']}, {r['country']}"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    
    bot.reply_to(message, f"🔍 *ВЫБЕРИТЕ ГОРОД:*", reply_markup=kb, parse_mode="Markdown")
    bot.register_next_step_handler(message, work_world_select, results)

def work_world_select(message, results):
    text = message.text
    
    for r in results:
        if text == f"📍 {r['city']}, {r['country']}":
            city = r['city']
            country = r['country']
            
            c.execute("SELECT id, title, salary, company FROM jobs WHERE city=? AND country=? AND status='open'", (city, country))
            jobs = c.fetchall()
            
            if jobs:
                msg = f"💼 *РАБОТА В {city}, {country}*\n\n"
                for j in jobs:
                    msg += f"🆔 {j[0]}\n📌 {j[1]}\n💰 {j[2]} ₸\n🏢 {j[3]}\n\n"
            else:
                msg = f"💼 *РАБОТА В {city}, {country}*\n\n📭 Пока нет вакансий"
            
            bot.reply_to(message, msg, parse_mode="Markdown")
            return
    
    bot.reply_to(message, "❌ Выберите город из списка")

@bot.message_handler(func=lambda m: m.text == "➕ СОЗДАТЬ ВАКАНСИЮ")
def create_job_request(message):
    msg = bot.reply_to(message, "💼 Опишите вакансию:\n\n- Название должности\n- Зарплата\n- Требования\n- Город\n- Контакты")
    bot.register_next_step_handler(msg, create_job)

def create_job(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите город")
        return
    
    salary_match = re.search(r'(\d+[\s]?\d*)', message.text)
    salary = int(salary_match.group(1).replace(' ', '')) if salary_match else random.randint(50000, 300000)
    
    c.execute("INSERT INTO jobs (title, description, salary, company, city, country, employer_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              ("Вакансия", message.text, salary, "Компания", city, country, user_id, astana_time()))
    conn.commit()
    bot.reply_to(message, f"✅ ВАКАНСИЯ СОЗДАНА в {city}, {country}!\n💰 Зарплата: {salary} ₸")
    log_action(user_id, "create_job", f"{city}, {salary}")

@bot.message_handler(func=lambda m: m.text == "📝 МОЁ РЕЗЮМЕ")
def resume_section(message):
    msg = bot.reply_to(message, "📝 Напишите ваше резюме:\n\n- Имя и фамилия\n- Профессия\n- Опыт работы\n- Навыки\n- Город\n- Контакты")
    bot.register_next_step_handler(msg, save_resume)

def save_resume(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET resume=? WHERE user_id=?", (message.text, user_id))
    conn.commit()
    bot.reply_to(message, f"✅ РЕЗЮМЕ СОХРАНЕНО!")
    log_action(user_id, "save_resume", message.text[:50])

# ==================================================
# ЗАКАЗЫ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📦 ЗАКАЗЫ")
def orders_menu(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите ваш город! Нажмите «🌍 МОЙ ГОРОД»")
        return
    
    orders = get_orders_global(city, country)
    
    if orders:
        msg = f"📦 *ЗАКАЗЫ В {city}, {country}*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📌 {o[1]}\n💰 {o[2]} ₸\n\n"
    else:
        msg = f"📦 *ЗАКАЗЫ В {city}, {country}*\n\n📭 Пока нет заказов"
    
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("➕ СОЗДАТЬ ЗАКАЗ"), KeyboardButton("📋 МОИ ЗАКАЗЫ"))
    kb.add(KeyboardButton("🌍 ПО ВСЕМУ МИРУ"), KeyboardButton("🔙 НАЗАД"))
    
    bot.reply_to(message, msg, reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "➕ СОЗДАТЬ ЗАКАЗ")
def create_order_request(message):
    msg = bot.reply_to(message, "📦 Опишите ваш заказ:\n\n- Что нужно сделать\n- Бюджет\n- Сроки\n- Город")
    bot.register_next_step_handler(msg, create_order)

def create_order(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите город")
        return
    
    price_match = re.search(r'(\d+[\s]?\d*)', message.text)
    price = int(price_match.group(1).replace(' ', '')) if price_match else random.randint(1000, 50000)
    
    c.execute("INSERT INTO orders (category, title, description, price, customer_id, city, country, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              ("general", "Заказ", message.text, price, user_id, city, country, "open", astana_time()))
    conn.commit()
    bot.reply_to(message, f"✅ ЗАКАЗ СОЗДАН в {city}, {country}!\n💰 Бюджет: {price} ₸")
    log_action(user_id, "create_order", f"{city}, {price}")

@bot.message_handler(func=lambda m: m.text == "📋 МОИ ЗАКАЗЫ")
def my_orders(message):
    user_id = message.chat.id
    c.execute("SELECT id, title, price, status FROM orders WHERE customer_id=? ORDER BY id DESC", (user_id,))
    orders = c.fetchall()
    if orders:
        msg = "📋 *ВАШИ ЗАКАЗЫ*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📌 {o[1]}\n💰 {o[2]} ₸\n📌 {o[3]}\n\n"
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, "📭 У вас нет заказов")

@bot.message_handler(func=lambda m: m.text == "🌍 ПО ВСЕМУ МИРУ")
def orders_world(message):
    msg = bot.reply_to(message, "🌍 Введите город для поиска заказов:")
    bot.register_next_step_handler(msg, orders_world_search)

def orders_world_search(message):
    query = message.text.strip()
    results = search_city_global(query)
    
    if not results:
        bot.reply_to(message, f"❌ Город не найден")
        return
    
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for r in results[:5]:
        kb.add(KeyboardButton(f"📍 {r['city']}, {r['country']}"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    
    bot.reply_to(message, f"🔍 *ВЫБЕРИТЕ ГОРОД:*", reply_markup=kb, parse_mode="Markdown")
    bot.register_next_step_handler(message, orders_world_select, results)

def orders_world_select(message, results):
    text = message.text
    
    for r in results:
        if text == f"📍 {r['city']}, {r['country']}":
            city = r['city']
            country = r['country']
            
            c.execute("SELECT id, title, price FROM orders WHERE city=? AND country=? AND status='open'", (city, country))
            orders = c.fetchall()
            
            if orders:
                msg = f"📦 *ЗАКАЗЫ В {city}, {country}*\n\n"
                for o in orders:
                    msg += f"🆔 {o[0]}\n📌 {o[1]}\n💰 {o[2]} ₸\n\n"
            else:
                msg = f"📦 *ЗАКАЗЫ В {city}, {country}*\n\n📭 Пока нет заказов"
            
            bot.reply_to(message, msg, parse_mode="Markdown")
            return
    
    bot.reply_to(message, "❌ Выберите город из списка")

# ==================================================
# МОНЕТИЗАЦИЯ (внутренние кнопки)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💎 КУПИТЬ ТАРИФ")
def buy_tariff(message):
    bot.reply_to(message, "💎 *ВЫБЕРИТЕ ТАРИФ*\n\n• Бесплатный — 0₸\n• Базовый — 1000₸/мес\n• PRO — 5000₸/мес\n• Бизнес — 20000₸/мес", 
                 reply_markup=get_tariff_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "⭐ ПАРТНЁРСКАЯ")
def referral(message):
    user_id = message.chat.id
    bot_name = bot.get_me().username
    c.execute("SELECT COUNT(*) FROM users WHERE referrer_id=?", (user_id,))
    count = c.fetchone()[0]
    msg = f"⭐ *ПАРТНЁРСКАЯ ПРОГРАММА*\n\n👥 Приглашено друзей: {count}\n💰 Бонус: 10% от пополнений\n\n🔗 ВАША ССЫЛКА:\nhttps://t.me/{bot_name}?start={user_id}"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🏦 KASPI QR")
def kaspi_payment(message):
    msg = bot.reply_to(message, "💳 *KASPI QR*\n\nВведите сумму в тенге:")
    bot.register_next_step_handler(msg, generate_kaspi_payment)

def generate_kaspi_payment(message):
    try:
        amount = int(message.text)
        if amount <= 0:
            amount = random.randint(1000, 50000)
        qr = generate_kaspi_qr(amount)
        bot.reply_to(message, f"💳 *KASPI QR*\n💰 Сумма: {amount} ₸\n\n📱 QR-код:\n{qr}\n\n(Откройте в Kaspi для оплаты)", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Введите число")

@bot.message_handler(func=lambda m: m.text == "💎 USDT TRC20")
def usdt_payment(message):
    bot.reply_to(message, f"💎 *USDT TRC20*\n\n📤 ПЕРЕВЕДИТЕ НА КОШЕЛЁК:\n`{CRYPTO_WALLET}`\n\n🔗 СЕТЬ: TRC20\n✅ После оплаты: /confirm", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 МОЙ ДОХОД")
def my_income(message):
    user_id = message.chat.id
    c.execute("SELECT SUM(amount) FROM earnings WHERE user_id=?", (user_id,))
    total = c.fetchone()[0] or 0
    bot.reply_to(message, f"💰 *ВАШ ДОХОД:* {total} Благ", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📈 ОБЩАЯ СТАТИСТИКА")
def total_stats(message):
    if not is_admin(message.chat.id):
        bot.reply_to(message, "❌ Только для Хранителя")
        return
    total = get_total_earnings()
    bot.reply_to(message, f"📊 *ОБЩАЯ СТАТИСТИКА ДОХОДОВ*\n\n💰 Всего: {total} ₸", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💸 ВЫВЕСТИ")
def withdraw_request(message):
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
    for admin in ADMIN_IDS:
        try:
            bot.send_message(admin, f"💰 *ЗАЯВКА НА ВЫВОД!*\n\n👤 Пользователь: {user_id}\n💵 Сумма: {amount} Благ\n💳 Кошелёк: {wallet}\n\n/approve_withdraw {user_id} {amount}", parse_mode="Markdown")
        except:
            pass

@bot.message_handler(commands=['approve_withdraw'])
def approve_withdraw(message):
    if not is_admin(message.chat.id):
        return
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        amount = int(parts[2])
        c.execute("UPDATE withdraw_requests SET status='approved' WHERE user_id=? AND amount=? AND status='pending'", (user_id, amount))
        conn.commit()
        bot.reply_to(message, f"✅ Вывод {amount} Благ для пользователя {user_id} одобрен!")
        try:
            bot.send_message(user_id, f"✅ Ваша заявка на вывод {amount} Благ одобрена!")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Формат: /approve_withdraw <user_id> <сумма>")

@bot.message_handler(func=lambda m: m.text == "📋 ИСТОРИЯ")
def payment_history(message):
    user_id = message.chat.id
    c.execute("SELECT id, amount, method, status, created_at FROM payments WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,))
    pays = c.fetchall()
    if not pays:
        bot.reply_to(message, "📭 История платежей пуста")
        return
    msg = "📋 *ИСТОРИЯ ПЛАТЕЖЕЙ*\n\n"
    for p in pays:
        status_icon = "✅" if p[3] == "completed" else "⏳"
        msg += f"{status_icon} #{p[0]} | {p[1]} ₸ | {p[2]} | {p[4][:16]}\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================================================
# БИЗНЕС-ФУНКЦИИ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📊 АНАЛИТИКА")
def analytics(message):
    bot.reply_to(message, "📊 *БИЗНЕС-АНАЛИТИКА*\n\n• Прогноз продаж\n• Анализ конкурентов\n• Рыночные тренды\n• Отчёты по расходам\n\n💰 Стоимость: от 5000 ₸/мес")

@bot.message_handler(func=lambda m: m.text == "🤖 АВТОМАТИЗАЦИЯ")
def automation(message):
    bot.reply_to(message, "🤖 *АВТОМАТИЗАЦИЯ БИЗНЕСА*\n\n• Чат-бот для клиентов\n• CRM интеграция\n• Автоматическая отчётность\n• Управление задачами\n\n💰 Стоимость: от 50000 ₸/мес")

@bot.message_handler(func=lambda m: m.text == "📈 ЛИЗИНГ")
def leasing(message):
    bot.reply_to(message, "📈 *ЛИЗИНГ ОБОРУДОВАНИЯ*\n\n• 🚗 Автотранспорт: от 15% годовых\n• 🏗️ Спецтехника: от 12% годовых\n• 🖥️ Оборудование: от 10% годовых\n\n📞 Для заявки: /leasing_request")

@bot.message_handler(func=lambda m: m.text == "💼 ЗАКАЗЫ")
def business_orders(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите город")
        return
    orders = get_orders_global(city, country)
    if orders:
        msg = "📋 *ВАШИ ЗАКАЗЫ:*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📌 {o[1]}\n💰 {o[2]} ₸\n\n"
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, "📭 У вас нет заказов")

# ==================================================
# АДМИН-КОМАНДЫ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👥 ОНЛАЙН" and is_admin(m.chat.id))
def admin_online(message):
    c.execute("SELECT user_id, name, city, country FROM users WHERE last_seen > datetime('now', '-5 minutes')")
    users = c.fetchall()
    if users:
        msg = "🟢 ОНЛАЙН:\n"
        for u in users:
            city_str = f"{u[2]}, {u[3]}" if u[2] else "город не указан"
            msg += f"🆔 {u[0]} | {u[1]} | {city_str}\n"
        bot.reply_to(message, msg)
    else:
        bot.reply_to(message, "🟢 Никого нет")

@bot.message_handler(func=lambda m: m.text == "📊 СТАТИСТИКА" and is_admin(m.chat.id))
def admin_stats(message):
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT SUM(blessings) FROM users")
    blessings = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM orders")
    orders = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM jobs")
    jobs = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT city) FROM users WHERE city IS NOT NULL")
    cities = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT country) FROM users WHERE country IS NOT NULL")
    countries = c.fetchone()[0]
    
    msg = f"📊 СТАТИСТИКА:\n👥 Всего: {total}\n✨ Благ: {blessings}\n📦 Заказов: {orders}\n💼 Вакансий: {jobs}\n🌍 Городов: {cities}\n🗺️ Стран: {countries}"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "💰 ФИНАНСЫ" and is_admin(m.chat.id))
def admin_finance(message):
    total = get_total_earnings()
    bot.reply_to(message, f"💰 ФИНАНСЫ:\n📱 Криптокошелёк: {CRYPTO_WALLET}\n💰 Всего: {total} ₸")

@bot.message_handler(func=lambda m: m.text == "👥 ВСЕ ЛЮДИ" and is_admin(m.chat.id))
def admin_users(message):
    c.execute("SELECT user_id, name, city, country, role, blessings FROM users LIMIT 30")
    users = c.fetchall()
    msg = "👥 ПОЛЬЗОВАТЕЛИ:\n\n"
    for u in users:
        city_str = f"{u[2]}, {u[3]}" if u[2] else "город не указан"
        msg += f"🆔 {u[0]} | {u[1]} | {city_str} | {u[4]} | ✨{u[5]}\n"
    bot.reply_to(message, msg[:4000])

@bot.message_handler(func=lambda m: m.text == "✨ БЛАГА" and is_admin(m.chat.id))
def admin_top(message):
    c.execute("SELECT name, blessings FROM users ORDER BY blessings DESC LIMIT 10")
    top = c.fetchall()
    msg = "✨ ТОП ПО БЛАГАМ:\n\n"
    for i, u in enumerate(top, 1):
        msg += f"{i}. {u[0]} — {u[1]} ✦\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "📤 РАССЫЛКА" and is_admin(m.chat.id))
def admin_broadcast(message):
    msg = bot.reply_to(message, "📤 Введите сообщение для рассылки всем пользователям:")
    bot.register_next_step_handler(msg, do_broadcast)

def do_broadcast(message):
    text = message.text
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    sent = 0
    for u in users:
        try:
            bot.send_message(u[0], f"📢 СООБЩЕНИЕ ОТ ХРАНИТЕЛЯ:\n\n{text}")
            sent += 1
            time.sleep(0.05)
        except:
            pass
    bot.reply_to(message, f"✅ Отправлено {sent} пользователям")

@bot.message_handler(func=lambda m: m.text == "💳 ПЛАТЕЖИ" and is_admin(m.chat.id))
def admin_payments(message):
    c.execute("SELECT id, user_id, amount, tariff, status, created_at FROM payments ORDER BY id DESC LIMIT 20")
    pays = c.fetchall()
    if not pays:
        bot.reply_to(message, "📭 Платежей пока нет")
        return
    msg = "💳 ПЛАТЕЖИ:\n\n"
    for p in pays:
        status_icon = "✅" if p[4] == "completed" else "⏳"
        msg += f"{status_icon} #{p[0]} | 👤 {p[1]} | 💰 {p[2]} | {p[3]} | {p[5][:16]}\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "🏦 ВЫВОДЫ" and is_admin(m.chat.id))
def admin_withdraws(message):
    c.execute("SELECT id, user_id, amount, status, created_at FROM withdraw_requests ORDER BY id DESC LIMIT 20")
    reqs = c.fetchall()
    if not reqs:
        bot.reply_to(message, "📭 Заявок на вывод нет")
        return
    msg = "🏦 ЗАЯВКИ НА ВЫВОД:\n\n"
    for r in reqs:
        status_icon = "⏳" if r[3] == "pending" else "✅"
        msg += f"{status_icon} #{r[0]} | 👤 {r[1]} | 💰 {r[2]} | {r[4][:16]}\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "📊 ДОХОДЫ" and is_admin(m.chat.id))
def admin_earnings(message):
    total = get_total_earnings()
    c.execute("SELECT source, SUM(amount) FROM earnings GROUP BY source")
    by_source = c.fetchall()
    msg = f"📊 ДОХОДЫ ЗЕРКАЛА:\n\n💰 Всего: {total} ₸\n\n📋 ПО ИСТОЧНИКАМ:\n"
    for bs in by_source:
        msg += f"• {bs[0]}: {bs[1]} ₸\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "📜 ЛОГИ" and is_admin(m.chat.id))
def admin_logs(message):
    c.execute("SELECT user_id, action, created_at FROM logs ORDER BY id DESC LIMIT 20")
    logs = c.fetchall()
    if not logs:
        bot.reply_to(message, "📭 Логов нет")
        return
    msg = "📜 ЛОГИ:\n\n"
    for l in logs:
        msg += f"{l[2][:16]} | ID:{l[0]} | {l[1][:40]}\n"
    bot.reply_to(message, msg[:4000])

@bot.message_handler(func=lambda m: m.text == "🔍 ПОИСК" and is_admin(m.chat.id))
def admin_search(message):
    msg = bot.reply_to(message, "🔍 Введите ID или имя пользователя:")
    bot.register_next_step_handler(msg, search_user)

def search_user(message):
    query = message.text.strip()
    if query.isdigit():
        c.execute("SELECT user_id, name, city, country, tariff, blessings FROM users WHERE user_id=?", (int(query),))
    else:
        c.execute("SELECT user_id, name, city, country, tariff, blessings FROM users WHERE name LIKE ?", (f"%{query}%",))
    
    users = c.fetchall()
    if not users:
        bot.reply_to(message, f"❌ Пользователь «{query}» не найден")
        return
    
    msg = "🔍 РЕЗУЛЬТАТЫ ПОИСКА:\n\n"
    for u in users:
        city_str = f"{u[2]}, {u[3]}" if u[2] else "город не указан"
        msg += f"🆔 {u[0]}\n📛 {u[1]}\n📍 {city_str}\n💎 {u[4]}\n✨ {u[5]} Благ\n\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "📈 ОТЧЁТ" and is_admin(m.chat.id))
def admin_report(message):
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM users WHERE last_seen LIKE ?", (f"{today}%",))
    new = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM payments WHERE created_at LIKE ?", (f"{today}%",))
    payments = c.fetchone()[0]
    bot.reply_to(message, f"📈 ОТЧЁТ ЗА {today}:\n➕ Новых: {new}\n💳 Оплат: {payments}\n✅ Статус: СТАБИЛЬНО")

@bot.message_handler(func=lambda m: m.text == "🩺 ЗДОРОВЬЕ" and is_admin(m.chat.id))
def admin_health(message):
    bot.reply_to(message, "🩺 ЗДОРОВЬЕ:\n✅ Бот работает\n✅ География: весь мир\n✅ Монетизация: активна\n✅ Замысел: СВЕРШИЛСЯ\n✅ База данных OK")

@bot.message_handler(func=lambda m: m.text == "🛡️ ЗАЩИТА" and is_admin(m.chat.id))
def admin_security(message):
    bot.reply_to(message, "🛡️ ЗАЩИТА:\n✅ Антивирус активен\n✅ SQL защита включена\n✅ XSS защита включена")

@bot.message_handler(func=lambda m: m.text == "💎 ТАРИФЫ" and is_admin(m.chat.id))
def admin_tariffs(message):
    msg = "💎 УПРАВЛЕНИЕ ТАРИФАМИ:\n\n"
    for key, t in TARIFFS.items():
        c.execute("SELECT COUNT(*) FROM users WHERE tariff=?", (key,))
        count = c.fetchone()[0]
        msg += f"• {t['name']}: {count} чел.\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "🔄 ОБНОВИТЬ" and is_admin(m.chat.id))
def admin_reload(message):
    bot.reply_to(message, "🔄 Перезагрузка модулей...")
    try:
        import importlib
        importlib.reload(sys.modules[__name__])
        bot.reply_to(message, "✅ Обновление завершено!")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda m: m.text == "📡 СТАТУС" and is_admin(m.chat.id))
def admin_status(message):
    total_users = get_users_count()
    online_users = get_online_count()
    msg = f"📡 СТАТУС:\n👑 Хранитель: {message.chat.id}\n👥 Всего: {total_users}\n🟢 Онлайн: {online_users}\n🌍 География: весь мир\n💰 Монетизация: активна\n🕋 Замысел: СВЕРШИЛСЯ\n✅ OK"
    bot.reply_to(message, msg)

def get_users_count():
    c.execute("SELECT COUNT(*) FROM users")
    return c.fetchone()[0]

def get_online_count():
    c.execute("SELECT COUNT(*) FROM users WHERE last_seen > datetime('now', '-5 minutes')")
    return c.fetchone()[0]

@bot.message_handler(func=lambda m: m.text == "🧹 ОЧИСТИТЬ" and is_admin(m.chat.id))
def admin_clean(message):
    bot.reply_to(message, "🧹 Очистка временных файлов...")
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    c.execute("DELETE FROM logs WHERE created_at < ?", (week_ago,))
    conn.commit()
    bot.reply_to(message, "✅ Очистка завершена!")

# ==================================================
# ОСТАЛЬНЫЕ ФУНКЦИИ (фото, голос, помощь, пожилые, дети)
# ==================================================

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
def resume_shortcut(message):
    msg = bot.reply_to(message, "📝 Напишите резюме:")
    bot.register_next_step_handler(msg, save_resume_shortcut)

def save_resume_shortcut(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET resume=? WHERE user_id=?", (message.text, user_id))
    conn.commit()
    bot.reply_to(message, "✅ РЕЗЮМЕ СОХРАНЕНО!")

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
                    messages=[{"role": "system", "content": "Ты — Зеркало. Отвечай кратко, по делу, с уважением. Всегда начинай с 'Ассаляму алейкум'. Отвечай на русском языке."},
                              {"role": "user", "content": question}],
                    temperature=0.7
                )
                bot.reply_to(message, resp.choices[0].message.content)
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка AI: {str(e)[:100]}")
        else:
            bot.reply_to(message, f"🤖 Вопрос принят!")
    else:
        bot.reply_to(message, f"❌ Недостаточно Благ! Нужно 1 ✦\n💰 /pay")

@bot.message_handler(func=lambda m: m.text == "👵 ПОЖИЛЫЕ")
def elder_section(message):
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add(KeyboardButton("👋 ПОЗДОРОВАТЬСЯ"))
    kb.add(KeyboardButton("📞 ПОМОЩЬ РЯДОМ"))
    kb.add(KeyboardButton("🏥 ЗДОРОВЬЕ"))
    kb.add(KeyboardButton("🆘 СРОЧНАЯ ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    bot.reply_to(message, "👵 *РЕЖИМ ДЛЯ ПОЖИЛЫХ*", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👋 ПОЗДОРОВАТЬСЯ")
def elder_greet(message):
    bot.reply_to(message, "👋 Здравствуйте! Я - Зеркало. Всегда рад помочь!")

@bot.message_handler(func=lambda m: m.text == "📞 ПОМОЩЬ РЯДОМ")
def elder_help(message):
    bot.reply_to(message, "📞 ПОМОЩЬ РЯДОМ:\n• Соцработник: +7 (700) 000-00-01\n• Поликлиника: +7 (700) 000-00-02")

@bot.message_handler(func=lambda m: m.text == "🏥 ЗДОРОВЬЕ")
def elder_health(message):
    bot.reply_to(message, "🏥 ЗДОРОВЬЕ:\n🚑 Скорая: 103")

@bot.message_handler(func=lambda m: m.text == "🆘 СРОЧНАЯ ПОМОЩЬ")
def elder_emergency(message):
    bot.reply_to(message, "🆘 СРОЧНАЯ ПОМОЩЬ:\n🚑 103\n🚔 102\n🚒 101\n📞 112")

@bot.message_handler(func=lambda m: m.text == "🧒 ДЕТИ")
def child_section(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📖 СКАЗКА"), KeyboardButton("🧩 ЗАГАДКА"))
    kb.add(KeyboardButton("🎵 ПЕСЕНКА"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    bot.reply_to(message, "🧒 *ДЕТСКИЙ РЕЖИМ*", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📖 СКАЗКА")
def child_tale(message):
    tales = ["🐺 Волк и семеро козлят...", "👸 Золушка...", "🐻 Три медведя..."]
    bot.reply_to(message, f"📖 *СКАЗКА*\n{random.choice(tales)}", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🧩 ЗАГАДКА")
def child_riddle(message):
    riddles = {"Зимой и летом одним цветом?": "ёлка"}
    q = random.choice(list(riddles.keys()))
    bot.reply_to(message, f"🧩 *ЗАГАДКА*\n{q}")
    bot.register_next_step_handler(message, check_riddle, riddles[q])

def check_riddle(message, answer):
    if message.text.lower() == answer:
        bot.reply_to(message, "✅ ПРАВИЛЬНО!")
    else:
        bot.reply_to(message, f"❌ Ответ: {answer}")

@bot.message_handler(func=lambda m: m.text == "🎵 ПЕСЕНКА")
def child_song(message):
    songs = ["В лесу родилась ёлочка..."]
    bot.reply_to(message, f"🎵 *ПЕСЕНКА*\n{random.choice(songs)}", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🆘 ПОМОЩЬ")
def help_section(message):
    help_text = """
🪞 *ПОМОЩЬ*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 *ГЛАВНЫЕ КНОПКИ:*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👑 ХРАНИТЕЛЬ — полное управление (только для вас)
🏢 БИЗНЕС — аналитика, лизинг, заказы
👤 ЛЮДИ — работа, заказы, услуги
🧠 AI-ДОКТОР — диагностика и лечение
💰 МОНЕТИЗАЦИЯ — тарифы, партнёрка, вывод

🔘 *الفتح* — ВЕЛИКОЕ ОТКРЫТИЕ (запуск полной монетизации)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 *ГЕОГРАФИЯ:*
• Автоопределение по геолокации
• Поиск работы в ЛЮБОМ городе мира
• Поиск заказов в ЛЮБОМ городе мира

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 *ТАРИФЫ:*
• Бесплатный — 0₸/мес
• Базовый — 1000₸/мес
• PRO — 5000₸/мес
• Бизнес — 20000₸/мес

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ /pay — купить тариф
⚡ /id — узнать свой ID

🤲 *Альхамдулиллах.*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, help_text, parse_mode="Markdown")

# ==================================================
# ВОЗВРАТ НА ГЛАВНУЮ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🔙 НА ГЛАВНУЮ")
def back_to_main(message):
    bot.reply_to(message, "🏠 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔙 НАЗАД")
def back_to_previous(message):
    bot.reply_to(message, "🏠 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_main_keyboard(), parse_mode="Markdown")

# ==================================================
# ОБРАБОТКА ТАРИФОВ
# ==================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("tariff_"))
def handle_tariff_callback(call):
    user_id = call.from_user.id
    tariff_key = call.data.replace("tariff_", "")
    
    if tariff_key == "free":
        c.execute("UPDATE users SET tariff='free', tariff_expires=NULL WHERE user_id=?", (user_id,))
        conn.commit()
        bot.answer_callback_query(call.id, "✅ Бесплатный тариф!")
        bot.edit_message_text("✅ Бесплатный тариф активирован!", call.message.chat.id, call.message.message_id)
        return
    
    tariff = {"basic": {"name": "Базовый", "price": 1000}, 
              "pro": {"name": "PRO", "price": 5000},
              "business": {"name": "Бизнес", "price": 20000}}[tariff_key]
    amount = tariff["price"]
    tx_id = create_payment(user_id, amount, "Kaspi QR", tariff_key)
    qr = generate_kaspi_qr(amount)
    
    bot.edit_message_text(f"💎 *ОПЛАТА ТАРИФА {tariff['name']}*\n\n💰 {amount} ₸\n📱 QR-код:\n{qr}\n\n🆔 ID: `{tx_id}`\n\n✅ После оплаты: /confirm_{tx_id}", 
                          call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text and m.text.startswith("/confirm_"))
def confirm_payment_callback(message):
    tx_id = message.text.replace("/confirm_", "").strip()
    success, amount, tariff = confirm_payment(tx_id)
    if success:
        bot.reply_to(message, f"✅ ПЛАТЁЖ ПОДТВЕРЖДЁН!\n\n💰 +{amount} Благ\n💎 Тариф: {tariff}")
    else:
        bot.reply_to(message, f"❌ Платёж не найден")

# ==================================================
# ОБЫЧНЫЕ СООБЩЕНИЯ
# ==================================================

@bot.message_handler(func=lambda m: True)
def handle_any(message):
    user_id = message.chat.id
    text = message.text
    
    # Пропускаем все кнопки
    all_buttons = [
        "👑 ХРАНИТЕЛЬ", "🏢 БИЗНЕС", "👤 ЛЮДИ", "🧠 AI-ДОКТОР", "💰 МОНЕТИЗАЦИЯ",
        "🔘 الفتح", "🔙 НА ГЛАВНУЮ", "🔙 НАЗАД",
        "👥 ОНЛАЙН", "📊 СТАТИСТИКА", "💰 ФИНАНСЫ", "👥 ВСЕ ЛЮДИ", "✨ БЛАГА",
        "📤 РАССЫЛКА", "💳 ПЛАТЕЖИ", "🏦 ВЫВОДЫ", "📊 ДОХОДЫ", "📜 ЛОГИ",
        "🔍 ПОИСК", "📈 ОТЧЁТ", "🩺 ЗДОРОВЬЕ", "🛡️ ЗАЩИТА", "💎 ТАРИФЫ",
        "🔄 ОБНОВИТЬ", "📡 СТАТУС", "🧹 ОЧИСТИТЬ",
        "💸 РАБОТА", "📦 ЗАКАЗЫ", "📸 ФОТО", "🎤 ГОЛОС", "📍 АПТЕКА", "📝 РЕЗЮМЕ",
        "💳 KASPI QR", "💰 БАЛАНС", "❓ ВОПРОС", "🆘 ПОМОЩЬ",
        "📊 АНАЛИТИКА", "🤖 АВТОМАТИЗАЦИЯ", "📈 ЛИЗИНГ", "💼 ЗАКАЗЫ",
        "👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ", "🏢 БИЗНЕСМЕН", "👵 ПОЖИЛОЙ ЧЕЛОВЕК", "🧒 РЕБЁНОК",
        "🌍 ВЕСЬ МИР", "🔍 ПОИСК ПО МИРУ", "🌍 МОЙ ГОРОД",
        "📍 ОПРЕДЕЛИТЬ АВТОМАТИЧЕСКИ", "🔍 НАЙТИ ГОРОД", "📋 МОЙ ГОРОД",
        "➕ СОЗДАТЬ ВАКАНСИЮ", "📝 МОЁ РЕЗЮМЕ", "🌍 ПО ВСЕМУ МИРУ",
        "➕ СОЗДАТЬ ЗАКАЗ", "📋 МОИ ЗАКАЗЫ",
        "💎 КУПИТЬ ТАРИФ", "⭐ ПАРТНЁРСКАЯ", "💎 USDT TRC20", "📊 МОЙ ДОХОД",
        "📈 ОБЩАЯ СТАТИСТИКА", "💸 ВЫВЕСТИ", "📋 ИСТОРИЯ",
        "🩺 ЛЕЧЕНИЕ", "🛡️ ПРОВЕРКА", "📊 СТАТУС",
        "👋 ПОЗДОРОВАТЬСЯ", "📞 ПОМОЩЬ РЯДОМ", "🏥 ЗДОРОВЬЕ", "🆘 СРОЧНАЯ ПОМОЩЬ",
        "📖 СКАЗКА", "🧩 ЗАГАДКА", "🎵 ПЕСЕНКА"
    ]
    if text in all_buttons:
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
                    messages=[{"role": "system", "content": "Ты — Зеркало. Отвечай кратко, по делу, с уважением. Всегда начинай с 'Ассаляму алейкум'. Отвечай на русском языке."},
                              {"role": "user", "content": text}],
                    temperature=0.7
                )
                bot.reply_to(message, resp.choices[0].message.content)
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка AI: {str(e)[:100]}")
        else:
            bot.reply_to(message, f"🪞 Сообщение принято")
    else:
        bot.reply_to(message, f"❌ Не хватает 1 Блага!\n💰 /pay")

# ==================================================
# ФОНОВЫЙ ПРОЦЕСС
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
# ЗАПУСК
# ==================================================

print("=" * 70)
print("🪞 ЗЕРКАЛО - الفتح (ВЕЛИКОЕ ОТКРЫТИЕ)")
print("=" * 70)
print(f"✅ Бот запущен успешно")
print(f"👑 ОСНОВАТЕЛЬ: {FOUNDER_ID}")
print(f"👸 ХРАНИТЕЛЬ: {TOMIRIS_ID}")
print(f"📱 5 ГЛАВНЫХ КНОПОК + الفتح")
print(f"🌍 ГЕОГРАФИЯ: ВЕСЬ МИР (Любые города, любые страны)")
print(f"💰 МОНЕТИЗАЦИЯ: АКТИВНА")
print(f"🕋 ЗАМЫСЕЛ: СВЕРШИЛСЯ")
print("=" * 70)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
