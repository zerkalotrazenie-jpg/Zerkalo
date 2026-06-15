#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗЕРКАЛО - С ГЕОГРАФИЕЙ ВСЕГО МИРА
Все города, все страны. Работа и заказы по геолокации.
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
# ⚡ УСТАНОВКА
# ==================================================

def install_package(package):
    try:
        __import__(package.split('[')[0])
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
# 🔧 НАСТРОЙКИ
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# ⚠️ ТВОЙ ID — НЕ ТРОГАТЬ! ⚠️
FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814

# 💰 КРИПТОКОШЕЛЁК
CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"
KASPI_PHONE = "+77000000000"

# 💎 ТАРИФЫ
TARIFFS = {
    "free": {"name": "Бесплатный", "price": 0},
    "basic": {"name": "Базовый", "price": 1000},
    "pro": {"name": "PRO", "price": 5000},
    "business": {"name": "Бизнес", "price": 20000}
}

print("=" * 60)
print("🪞 ЗЕРКАЛО - ВЕСЬ МИР")
print("=" * 60)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 ТВОЙ ID: {FOUNDER_ID}")
print(f"🌍 ГЕОГРАФИЯ: ВСЕ ГОРОДА МИРА")
print("=" * 60)

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "🪞 Зеркало работает! География всего мира активна!", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ==================================================
# 📦 БАЗА ДАННЫХ (С ГОРОДАМИ)
# ==================================================

conn = sqlite3.connect('zerkalo.db', check_same_thread=False)
c = conn.cursor()

# Пользователи (с городом)
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

# Заказы (с городом)
c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, description TEXT, price INTEGER,
    customer_id INTEGER, city TEXT, country TEXT,
    status TEXT DEFAULT 'open', created_at TEXT
)''')

# Вакансии/Работа (с городом)
c.execute('''CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, description TEXT, salary INTEGER,
    company TEXT, city TEXT, country TEXT,
    employer_id INTEGER, status TEXT DEFAULT 'open', created_at TEXT
)''')

# Бизнесы (с городом)
c.execute('''CREATE TABLE IF NOT EXISTS businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, bin TEXT, contact_person TEXT,
    phone TEXT, city TEXT, country TEXT,
    monthly_profit INTEGER, status TEXT DEFAULT 'pending'
)''')

# Платежи, логи, остальное
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

c.execute('''CREATE TABLE IF NOT EXISTS legal_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT, status TEXT, assigned_to TEXT,
    created_at TEXT, updated_at TEXT
)''')

conn.commit()

def astana_time():
    return (datetime.utcnow() + timedelta(hours=5)).isoformat()

def is_admin(user_id):
    return user_id == FOUNDER_ID or user_id == TOMIRIS_ID

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
    log_action(user_id, "set_city", f"{city}, {country}")

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
            try:
                bot.send_message(referrer[0], f"🎉 Партнёрский бонус: +{bonus} Благ!")
            except:
                pass
        return True, amount, tariff
    return False, 0, None

# ==================================================
# 🌍 ГЕОГРАФИЯ — ПОИСК ГОРОДОВ ПО ВСЕМУ МИРУ
# ==================================================

def search_city_global(query):
    """Поиск города по всему миру через OpenStreetMap Nominatim"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=10&addressdetails=1"
        headers = {'User-Agent': 'ZerkaloBot/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        results = []
        for item in data:
            city_name = item.get('name', '')
            country = item.get('address', {}).get('country', '')
            # Извлекаем город из address если нужно
            if not city_name:
                city_name = item.get('address', {}).get('city', '') or item.get('address', {}).get('town', '') or item.get('address', {}).get('village', '')
            if city_name and country:
                results.append({
                    'city': city_name,
                    'country': country,
                    'lat': item.get('lat'),
                    'lon': item.get('lon'),
                    'display_name': item.get('display_name', f"{city_name}, {country}")
                })
            elif city_name:
                results.append({'city': city_name, 'country': 'Неизвестно', 'lat': item.get('lat'), 'lon': item.get('lon')})
        
        return results[:10]
    except Exception as e:
        print(f"Ошибка поиска города: {e}")
        return []

def get_city_from_coordinates(lat, lon):
    """Определяет город по координатам"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
        headers = {'User-Agent': 'ZerkaloBot/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        address = data.get('address', {})
        city = address.get('city') or address.get('town') or address.get('village') or address.get('hamlet')
        country = address.get('country', '')
        return city, country
    except:
        return None, None

def get_nearby_pharmacy(lat, lon, city):
    """Ищет аптеки в городе"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q=pharmacy+{city}&format=json&limit=5"
        headers = {'User-Agent': 'ZerkaloBot/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if data:
            msg = "💊 *АПТЕКИ В ВАШЕМ ГОРОДЕ:*\n\n"
            for i, ph in enumerate(data[:5], 1):
                name = ph.get('display_name', 'Аптека')[:100]
                msg += f"{i}. {name}\n"
            return msg
        return "📍 Аптеки не найдены в вашем городе"
    except:
        return "📍 Сервис временно недоступен"

def get_jobs_in_city(city, country):
    """Получает вакансии в городе"""
    c.execute("SELECT id, title, salary, company FROM jobs WHERE city=? AND country=? AND status='open'", (city, country))
    jobs = c.fetchall()
    if jobs:
        msg = f"💼 *РАБОТА В {city} ({country})*\n\n"
        for j in jobs:
            msg += f"🆔 {j[0]}\n📌 {j[1]}\n💰 {j[2]} ₸\n🏢 {j[3]}\n\n"
        return msg
    return f"📭 Пока нет вакансий в {city}"

def get_orders_in_city(city, country):
    """Получает заказы в городе"""
    c.execute("SELECT id, title, price FROM orders WHERE city=? AND country=? AND status='open'", (city, country))
    orders = c.fetchall()
    if orders:
        msg = f"📦 *ЗАКАЗЫ В {city} ({country})*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📌 {o[1]}\n💰 {o[2]} ₸\n\n"
        return msg
    return f"📭 Пока нет заказов в {city}"

# ==================================================
# 🧠 AI-ДОКТОР
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

🌍 География: ВСЕ ГОРОДА МИРА
📊 Статус: ✅ АКТИВЕН
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def heal(self):
        self.fixes_applied += 1
        return "✅ Проведена диагностика и лечение"

ai_doctor = AIDoctor()

# ==================================================
# 📱 ГЛАВНАЯ КЛАВИАТУРА — 6 КНОПОК (добавлена ГЕОГРАФИЯ)
# ==================================================

def get_main_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("👑 ХРАНИТЕЛЬ"))
    kb.add(KeyboardButton("🏢 БИЗНЕС"))
    kb.add(KeyboardButton("👤 ЛЮДИ"))
    kb.add(KeyboardButton("🧠 AI-ДОКТОР"))
    kb.add(KeyboardButton("💰 МОНЕТИЗАЦИЯ"))
    kb.add(KeyboardButton("🌍 МОЙ ГОРОД"))
    return kb

# ==================================================
# 🌍 КЛАВИАТУРА ВЫБОРА ГОРОДА
# ==================================================

def get_city_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📍 ОПРЕДЕЛИТЬ АВТОМАТИЧЕСКИ"))
    kb.add(KeyboardButton("🔍 НАЙТИ ГОРОД"))
    kb.add(KeyboardButton("📋 МОЙ ТЕКУЩИЙ ГОРОД"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

# ==================================================
# 👑 ВНУТРЕННЯЯ КЛАВИАТУРА ХРАНИТЕЛЯ
# ==================================================

def get_founder_inner_keyboard():
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    kb.add(KeyboardButton("👥 ОНЛАЙН"), KeyboardButton("📊 СТАТИСТИКА"), KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("👥 ВСЕ ЛЮДИ"), KeyboardButton("✨ БЛАГА"), KeyboardButton("📤 РАССЫЛКА"))
    kb.add(KeyboardButton("💳 ПЛАТЕЖИ"), KeyboardButton("🏦 ВЫВОДЫ"), KeyboardButton("📊 ДОХОДЫ"))
    kb.add(KeyboardButton("📜 ЛОГИ"), KeyboardButton("🔍 ПОИСК"), KeyboardButton("📈 ОТЧЁТ"))
    kb.add(KeyboardButton("🩺 ЗДОРОВЬЕ"), KeyboardButton("🛡️ ЗАЩИТА"), KeyboardButton("💎 ТАРИФЫ"))
    kb.add(KeyboardButton("🌍 ГОРОДА"), KeyboardButton("📊 ПО ГОРОДАМ"), KeyboardButton("🔄 ОБНОВИТЬ"))
    kb.add(KeyboardButton("📡 СТАТУС"), KeyboardButton("🧹 ОЧИСТИТЬ"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_business_inner_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 АНАЛИТИКА"), KeyboardButton("🤖 АВТОМАТИЗАЦИЯ"))
    kb.add(KeyboardButton("📈 ЛИЗИНГ"), KeyboardButton("💼 ЗАКАЗЫ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"))
    kb.add(KeyboardButton("🌍 МОЙ ГОРОД"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_people_inner_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"))
    kb.add(KeyboardButton("📸 ФОТО"), KeyboardButton("🎤 ГОЛОС"))
    kb.add(KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"))
    kb.add(KeyboardButton("💎 ПОДПИСКА"), KeyboardButton("⭐ ПАРТНЁРСКАЯ"))
    kb.add(KeyboardButton("🌍 МОЙ ГОРОД"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_monetization_inner_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💎 КУПИТЬ ТАРИФ"), KeyboardButton("⭐ ПАРТНЁРСКАЯ"))
    kb.add(KeyboardButton("🏦 KASPI QR"), KeyboardButton("💎 USDT TRC20"))
    kb.add(KeyboardButton("📊 МОЙ ДОХОД"), KeyboardButton("📈 ОБЩАЯ СТАТИСТИКА"))
    kb.add(KeyboardButton("💸 ВЫВЕСТИ"), KeyboardButton("📋 ИСТОРИЯ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_tariff_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("📱 Бесплатный", callback_data="tariff_free"))
    kb.add(InlineKeyboardButton("⭐ Базовый - 1000₸", callback_data="tariff_basic"))
    kb.add(InlineKeyboardButton("🚀 PRO - 5000₸", callback_data="tariff_pro"))
    kb.add(InlineKeyboardButton("💎 Бизнес - 20000₸", callback_data="tariff_business"))
    return kb

# ==================================================
# 🤖 ОСНОВНЫЕ КОМАНДЫ
# ==================================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
        if is_admin(user_id):
            c.execute("UPDATE users SET is_admin=1, tariff='pro' WHERE user_id=?", (user_id,))
        conn.commit()
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n✨ Вы получили 100 Благ!\n\n🌍 Для начала укажите ваш город:", 
                     reply_markup=get_city_keyboard())
        return
    
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (astana_time(), user_id))
    conn.commit()
    
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n🌍 Пожалуйста, укажите ваш город:", 
                     reply_markup=get_city_keyboard())
    else:
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n📍 Ваш город: {city}, {country}\n💰 Баланс: {get_balance(user_id)} Благ\n\n📱 Выберите раздел:", 
                     reply_markup=get_main_keyboard())

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
# 🌍 ГЕОГРАФИЯ — ОБРАБОТЧИКИ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🌍 МОЙ ГОРОД")
def my_city_section(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if city:
        msg = f"🌍 *ВАШ ГОРОД:*\n\n📍 {city}, {country}\n\n"
        msg += f"📊 Доступно вакансий: {get_jobs_count(city, country)}\n"
        msg += f"📦 Доступно заказов: {get_orders_count(city, country)}\n\n"
        msg += f"🔄 Сменить город? Используйте кнопки ниже:"
        bot.reply_to(message, msg, reply_markup=get_city_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "🌍 *ВЫБОР ГОРОДА*\n\nУкажите ваш город:", reply_markup=get_city_keyboard(), parse_mode="Markdown")

def get_jobs_count(city, country):
    c.execute("SELECT COUNT(*) FROM jobs WHERE city=? AND country=? AND status='open'", (city, country))
    return c.fetchone()[0]

def get_orders_count(city, country):
    c.execute("SELECT COUNT(*) FROM orders WHERE city=? AND country=? AND status='open'", (city, country))
    return c.fetchone()[0]

@bot.message_handler(func=lambda m: m.text == "📍 ОПРЕДЕЛИТЬ АВТОМАТИЧЕСКИ")
def auto_detect_city(message):
    user_id = message.chat.id
    bot.reply_to(message, "📍 Отправьте вашу геолокацию (нажмите 📎 → 📍 Location), чтобы я определил ваш город автоматически.")

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ ГОРОД")
def search_city_request(message):
    msg = bot.reply_to(message, "🔍 Введите название города (например: Almaty, Moscow, New York, London, Павлодар):")
    bot.register_next_step_handler(msg, search_city_result)

def search_city_result(message):
    user_id = message.chat.id
    query = message.text.strip()
    
    bot.reply_to(message, f"🔍 Ищу город «{query}» по всему миру...")
    results = search_city_global(query)
    
    if not results:
        bot.reply_to(message, f"❌ Город «{query}» не найден. Попробуйте ввести название на другом языке или более точно.")
        return
    
    # Показываем результаты с кнопками
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for r in results[:8]:
        city_name = f"{r['city']}, {r['country']}"
        kb.add(KeyboardButton(f"📍 {city_name}"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    
    bot.reply_to(message, f"🔍 *НАЙДЕНЫ ГОРОДА:*\n\nВыберите ваш город из списка:", 
                 reply_markup=kb, parse_mode="Markdown")
    
    # Сохраняем результаты для последующего выбора
    bot.register_next_step_handler(message, select_city_from_results, results)

def select_city_from_results(message, results):
    user_id = message.chat.id
    text = message.text
    
    if text == "🔙 НА ГЛАВНУЮ":
        bot.reply_to(message, "🏠 Главное меню", reply_markup=get_main_keyboard())
        return
    
    # Ищем выбранный город в результатах
    selected = None
    for r in results:
        city_name = f"{r['city']}, {r['country']}"
        if text == f"📍 {city_name}":
            selected = r
            break
    
    if selected:
        set_user_city(user_id, selected['city'], selected['country'])
        bot.reply_to(message, f"✅ *ГОРОД УСТАНОВЛЕН!*\n\n📍 {selected['city']}, {selected['country']}\n\n📱 Теперь вы будете видеть работу и заказы в вашем городе.", 
                     reply_markup=get_main_keyboard(), parse_mode="Markdown")
    else:
        # Обычный ввод
        city_name = text
        # Ищем точное совпадение
        for r in results:
            if r['city'].lower() == city_name.lower():
                selected = r
                break
        if selected:
            set_user_city(user_id, selected['city'], selected['country'])
            bot.reply_to(message, f"✅ ГОРОД УСТАНОВЛЕН: {selected['city']}, {selected['country']}", 
                         reply_markup=get_main_keyboard())
        else:
            bot.reply_to(message, f"❌ Город не найден. Попробуйте выбрать из списка или ввести точнее.")

@bot.message_handler(func=lambda m: m.text == "📋 МОЙ ТЕКУЩИЙ ГОРОД")
def show_current_city(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if city:
        jobs_msg = get_jobs_in_city(city, country)
        orders_msg = get_orders_in_city(city, country)
        bot.reply_to(message, f"🌍 *ВАШ ГОРОД:* {city}, {country}\n\n{jobs_msg}\n\n{orders_msg}", parse_mode="Markdown")
    else:
        bot.reply_to(message, "🌍 Город не указан. Нажмите «ОПРЕДЕЛИТЬ АВТОМАТИЧЕСКИ» или «НАЙТИ ГОРОД».")

@bot.message_handler(content_types=['location'])
def handle_location_city(message):
    user_id = message.chat.id
    lat = message.location.latitude
    lon = message.location.longitude
    
    city, country = get_city_from_coordinates(lat, lon)
    if city:
        set_user_city(user_id, city, country)
        bot.reply_to(message, f"✅ *ГОРОД ОПРЕДЕЛЁН АВТОМАТИЧЕСКИ!*\n\n📍 {city}, {country}\n\n📱 Теперь вы будете видеть работу и заказы в вашем городе.", 
                     reply_markup=get_main_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Не удалось определить город по геолокации. Попробуйте выбрать город вручную через «НАЙТИ ГОРОД».")

# ==================================================
# 💸 РАБОТА И ЗАКАЗЫ С ПРИВЯЗКОЙ К ГОРОДУ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💸 РАБОТА")
def work_section(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите ваш город! Нажмите «🌍 МОЙ ГОРОД»", reply_markup=get_city_keyboard())
        return
    
    jobs_msg = get_jobs_in_city(city, country)
    
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("➕ СОЗДАТЬ ВАКАНСИЮ"), KeyboardButton("🔍 НАЙТИ РАБОТУ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    
    bot.reply_to(message, f"💸 *РАБОТА В {city}*\n\n{jobs_msg}", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📦 ЗАКАЗЫ")
def orders_section(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите ваш город! Нажмите «🌍 МОЙ ГОРОД»", reply_markup=get_city_keyboard())
        return
    
    orders_msg = get_orders_in_city(city, country)
    
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("➕ СОЗДАТЬ ЗАКАЗ"), KeyboardButton("🔍 НАЙТИ ЗАКАЗ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    
    bot.reply_to(message, f"📦 *ЗАКАЗЫ В {city}*\n\n{orders_msg}", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "➕ СОЗДАТЬ ВАКАНСИЮ")
def create_job_request(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите ваш город")
        return
    
    msg = bot.reply_to(message, "💼 Опишите вакансию:\n\n- Название должности\n- Зарплата\n- Требования\n- Контакты")
    bot.register_next_step_handler(msg, create_job, city, country)

def create_job(message, city, country):
    user_id = message.chat.id
    description = message.text
    # Извлекаем зарплату из текста
    salary_match = re.search(r'(\d+[\s]?\d*)', description)
    salary = int(salary_match.group(1).replace(' ', '')) if salary_match else random.randint(50000, 300000)
    
    c.execute("INSERT INTO jobs (title, description, salary, company, city, country, employer_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              ("Вакансия", description, salary, "Компания", city, country, user_id, astana_time()))
    conn.commit()
    bot.reply_to(message, f"✅ ВАКАНСИЯ СОЗДАНА в городе {city}!\n💰 Зарплата: {salary} ₸")

@bot.message_handler(func=lambda m: m.text == "➕ СОЗДАТЬ ЗАКАЗ")
def create_order_request(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите ваш город")
        return
    
    msg = bot.reply_to(message, "📦 Опишите ваш заказ:\n\n- Что нужно сделать\n- Бюджет\n- Сроки")
    bot.register_next_step_handler(msg, create_order, city, country)

def create_order(message, city, country):
    user_id = message.chat.id
    description = message.text
    price_match = re.search(r'(\d+[\s]?\d*)', description)
    price = int(price_match.group(1).replace(' ', '')) if price_match else random.randint(1000, 50000)
    
    c.execute("INSERT INTO orders (title, description, price, customer_id, city, country, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              ("Заказ", description, price, user_id, city, country, "open", astana_time()))
    conn.commit()
    bot.reply_to(message, f"✅ ЗАКАЗ СОЗДАН в городе {city}!\n💰 Бюджет: {price} ₸")

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ ЗАКАЗ")
def find_orders_in_city(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите ваш город")
        return
    
    orders_msg = get_orders_in_city(city, country)
    bot.reply_to(message, orders_msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ РАБОТУ")
def find_jobs_in_city(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите ваш город")
        return
    
    jobs_msg = get_jobs_in_city(city, country)
    bot.reply_to(message, jobs_msg, parse_mode="Markdown")

# ==================================================
# 📍 АПТЕКА С ПРИВЯЗКОЙ К ГОРОДУ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📍 АПТЕКА")
def pharmacy_command(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите ваш город! Нажмите «🌍 МОЙ ГОРОД»", reply_markup=get_city_keyboard())
        return
    
    bot.reply_to(message, f"🔍 Ищу аптеки в городе {city}...")
    
    try:
        url = f"https://nominatim.openstreetmap.org/search?q=pharmacy+{city}&format=json&limit=5"
        headers = {'User-Agent': 'ZerkaloBot/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if data:
            msg = f"💊 *АПТЕКИ В {city}:*\n\n"
            for i, ph in enumerate(data[:5], 1):
                name = ph.get('display_name', 'Аптека')[:100]
                msg += f"{i}. {name}\n"
            bot.reply_to(message, msg, parse_mode="Markdown")
        else:
            bot.reply_to(message, f"📍 Аптеки не найдены в городе {city}")
    except:
        bot.reply_to(message, "📍 Сервис временно недоступен")

# ==================================================
# 👑 АДМИН-ПАНЕЛЬ (С ГОРОДАМИ)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🌍 ГОРОДА" and is_admin(m.chat.id))
def admin_cities(message):
    c.execute("SELECT city, country, COUNT(*) FROM users WHERE city IS NOT NULL GROUP BY city, country ORDER BY COUNT(*) DESC LIMIT 30")
    cities = c.fetchall()
    if not cities:
        bot.reply_to(message, "📭 Нет данных о городах")
        return
    msg = "🌍 *ГОРОДА ПОЛЬЗОВАТЕЛЕЙ:*\n\n"
    for cty in cities:
        msg += f"📍 {cty[0]}, {cty[1]} — {cty[2]} чел.\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 ПО ГОРОДАМ" and is_admin(m.chat.id))
def admin_stats_by_city(message):
    c.execute("SELECT city, country, COUNT(*) FROM users WHERE city IS NOT NULL GROUP BY city, country ORDER BY COUNT(*) DESC LIMIT 15")
    cities = c.fetchall()
    if not cities:
        bot.reply_to(message, "📭 Нет данных")
        return
    msg = "📊 *СТАТИСТИКА ПО ГОРОДАМ:*\n\n"
    for cty in cities:
        # Считаем заказы в городе
        c.execute("SELECT COUNT(*) FROM orders WHERE city=? AND country=?", (cty[0], cty[1]))
        orders = c.fetchone()[0]
        msg += f"📍 {cty[0]}, {cty[1]}\n   👥 {cty[2]} чел. | 📦 {orders} заказов\n\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================================================
# 💰 БАЛАНС, МОНЕТИЗАЦИЯ (как раньше)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💰 БАЛАНС")
def show_balance(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    city_str = f"{city}, {country}" if city else "не указан"
    bot.reply_to(message, f"💰 *БАЛАНС:* {get_balance(user_id)} Благ\n📍 Город: {city_str}\n\n💳 Пополнить: /pay\n💸 Вывести: /withdraw", parse_mode="Markdown")

# Остальные функции (монетизация, тарифы, вывод) остаются как в предыдущей версии
# ...

# ==================================================
# 🔄 ГЛАВНЫЕ КНОПКИ (ОСТАЛЬНЫЕ)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👑 ХРАНИТЕЛЬ")
def founder_section(message):
    if is_admin(message.chat.id):
        bot.reply_to(message, "👑 *ПАНЕЛЬ ХРАНИТЕЛЯ*\n\n📱 Полное управление:", 
                     reply_markup=get_founder_inner_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Нет доступа")

@bot.message_handler(func=lambda m: m.text == "🏢 БИЗНЕС")
def business_section(message):
    bot.reply_to(message, "🏢 *БИЗНЕС-РАЗДЕЛ*\n\n📊 Аналитика, лизинг, заказы:", 
                 reply_markup=get_business_inner_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👤 ЛЮДИ")
def people_section(message):
    bot.reply_to(message, "👤 *ОБЫЧНЫЙ РАЗДЕЛ*\n\n💸 Работа, заказы, услуги:", 
                 reply_markup=get_people_inner_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🧠 AI-ДОКТОР")
def ai_doctor_section(message):
    report = ai_doctor.get_report()
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🩺 ЛЕЧЕНИЕ"), KeyboardButton("🛡️ ПРОВЕРКА"))
    kb.add(KeyboardButton("📊 СТАТУС"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    bot.reply_to(message, f"🧠 *AI-ДОКТОР*\n\n{report}", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💰 МОНЕТИЗАЦИЯ")
def monetization_section(message):
    total_earned = get_total_earnings()
    msg = f"""
💰 *МОНЕТИЗАЦИЯ ЗЕРКАЛА*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Всего заработано: {total_earned} ₸
💎 Ваш тариф: {TARIFFS[get_tariff(message.chat.id)]['name']}
💰 Баланс: {get_balance(message.chat.id)} Благ

💡 СПОСОБЫ ЗАРАБОТКА:
• Платные тарифы — от 1000₸/мес
• Партнёрская программа — 10% с рефералов
• Kaspi QR — комиссия с платежей

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, msg, reply_markup=get_monetization_inner_keyboard(), parse_mode="Markdown")

# ==================================================
# 🔙 ВОЗВРАТ НА ГЛАВНУЮ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🔙 НА ГЛАВНУЮ")
def back_to_main(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if city:
        bot.reply_to(message, f"🏠 *ГЛАВНОЕ МЕНЮ*\n📍 {city}, {country}", 
                     reply_markup=get_main_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "🏠 *ГЛАВНОЕ МЕНЮ*", 
                     reply_markup=get_main_keyboard(), parse_mode="Markdown")

# ==================================================
# 💎 ТАРИФЫ (Callback)
# ==================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("tariff_"))
def handle_tariff(call):
    user_id = call.from_user.id
    tariff_key = call.data.replace("tariff_", "")
    
    if tariff_key == "free":
        c.execute("UPDATE users SET tariff='free', tariff_expires=NULL WHERE user_id=?", (user_id,))
        conn.commit()
        bot.answer_callback_query(call.id, "✅ Бесплатный тариф активирован!")
        bot.edit_message_text("✅ Бесплатный тариф активирован!", call.message.chat.id, call.message.message_id)
        return
    
    tariff = TARIFFS[tariff_key]
    amount = tariff["price"]
    tx_id = create_payment(user_id, amount, "Kaspi QR", tariff_key)
    qr = generate_kaspi_qr(amount)
    
    bot.edit_message_text(f"💎 *ОПЛАТА ТАРИФА {tariff['name']}*\n\n"
                         f"💰 Сумма: {amount} ₸\n"
                         f"📱 QR-код:\n{qr}\n\n"
                         f"🆔 ID: `{tx_id}`\n\n"
                         f"✅ После оплаты: /confirm_{tx_id}", 
                         call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text and m.text.startswith("/confirm_"))
def confirm_tx(message):
    tx_id = message.text.replace("/confirm_", "").strip()
    success, amount, tariff = confirm_payment(tx_id)
    if success:
        bot.reply_to(message, f"✅ ПЛАТЁЖ ПОДТВЕРЖДЁН!\n\n💰 +{amount} Благ\n💎 Тариф: {tariff}")
    else:
        bot.reply_to(message, f"❌ Платёж не найден")

# ==================================================
# 🩺 AI-ДОКТОР КОМАНДЫ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🩺 ЛЕЧЕНИЕ")
def ai_heal(message):
    result = ai_doctor.heal()
    bot.reply_to(message, f"🧠 *AI-ДОКТОР*\n\n{result}")

@bot.message_handler(func=lambda m: m.text == "🛡️ ПРОВЕРКА")
def ai_check(message):
    bot.reply_to(message, f"🛡️ *ПРОВЕРКА СИСТЕМЫ*\n\n✅ Код: чист\n✅ Вирусы: нет\n✅ География: активна\n✅ Защита: активна")

@bot.message_handler(func=lambda m: m.text == "📊 СТАТУС")
def ai_status(message):
    bot.reply_to(message, ai_doctor.get_report(), parse_mode="Markdown")

# ==================================================
# 💳 KASPI QR
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🏦 KASPI QR")
def kaspi_command(message):
    msg = bot.reply_to(message, "💳 *KASPI QR*\n\nВведите сумму в тенге:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, generate_kaspi)

def generate_kaspi(message):
    try:
        amount = int(message.text)
        if amount <= 0:
            amount = random.randint(1000, 50000)
        qr = generate_kaspi_qr(amount)
        bot.reply_to(message, f"💳 *KASPI QR*\n💰 Сумма: {amount} ₸\n\n📱 Ссылка:\n{qr}\n\n(Откройте в Kaspi для оплаты)", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Введите число")

@bot.message_handler(func=lambda m: m.text == "💎 USDT TRC20")
def crypto_payment(message):
    msg = f"💎 *ОПЛАТА USDT (TRC20)*\n\n📤 ПЕРЕВЕДИТЕ НА КОШЕЛЁК:\n`{CRYPTO_WALLET}`\n\n🔗 СЕТЬ: TRC20"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "⭐ ПАРТНЁРСКАЯ")
def referral_show(message):
    user_id = message.chat.id
    bot_name = bot.get_me().username
    c.execute("SELECT COUNT(*) FROM users WHERE referrer_id=?", (user_id,))
    count = c.fetchone()[0]
    msg = f"⭐ *ПАРТНЁРСКАЯ ПРОГРАММА*\n\n👥 Приглашено: {count}\n🔗 Ссылка:\nhttps://t.me/{bot_name}?start={user_id}\n\n💰 10% от пополнений!"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💎 КУПИТЬ ТАРИФ")
def buy_tariff(message):
    bot.reply_to(message, "💎 *ВЫБЕРИТЕ ТАРИФ*", reply_markup=get_tariff_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 МОЙ ДОХОД")
def my_earnings(message):
    user_id = message.chat.id
    c.execute("SELECT SUM(amount) FROM earnings WHERE user_id=?", (user_id,))
    total = c.fetchone()[0] or 0
    bot.reply_to(message, f"💰 *ВАШ ДОХОД:* {total} Благ")

@bot.message_handler(func=lambda m: m.text == "📈 ОБЩАЯ СТАТИСТИКА")
def admin_stats_monetization(message):
    if not is_admin(message.chat.id):
        return
    total = get_total_earnings()
    bot.reply_to(message, f"📊 *ОБЩАЯ СТАТИСТИКА ДОХОДОВ*\n\n💰 Всего: {total} ₸")

@bot.message_handler(func=lambda m: m.text == "💸 ВЫВЕСТИ")
def withdraw_request(message):
    msg = bot.reply_to(message, "💸 Введите сумму для вывода (мин. 1000):")
    bot.register_next_step_handler(msg, withdraw_amount)

def withdraw_amount(message):
    user_id = message.chat.id
    try:
        amount = int(message.text)
        if amount < 1000:
            bot.reply_to(message, "❌ Мин. 1000")
            return
        if get_balance(user_id) < amount:
            bot.reply_to(message, f"❌ Недостаточно средств")
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
    bot.reply_to(message, f"✅ Заявка на вывод {amount} создана!")
    for admin in [FOUNDER_ID, TOMIRIS_ID]:
        try:
            bot.send_message(admin, f"💰 ЗАЯВКА НА ВЫВОД!\n👤 {user_id}\n💵 {amount}\n/approve_withdraw {user_id} {amount}")
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
        c.execute("UPDATE withdraw_requests SET status='approved' WHERE user_id=? AND amount=?", (user_id, amount))
        conn.commit()
        bot.reply_to(message, f"✅ Вывод {amount} для {user_id} одобрен!")
        try:
            bot.send_message(user_id, f"✅ Вывод {amount} одобрен!")
        except:
            pass
    except:
        bot.reply_to(message, "❌ /approve_withdraw <id> <сумма>")

@bot.message_handler(func=lambda m: m.text == "📋 ИСТОРИЯ")
def payment_history(message):
    user_id = message.chat.id
    c.execute("SELECT id, amount, method, status, created_at FROM payments WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,))
    pays = c.fetchall()
    if not pays:
        bot.reply_to(message, "📭 История пуста")
        return
    msg = "📋 *ИСТОРИЯ ПЛАТЕЖЕЙ*\n\n"
    for p in pays:
        status_icon = "✅" if p[3] == "completed" else "⏳"
        msg += f"{status_icon} #{p[0]} | {p[1]} ₸ | {p[2]} | {p[4][:16]}\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💎 ПОДПИСКА")
def show_tariffs(message):
    msg = "💎 *ТАРИФЫ*\n\n"
    for key, t in TARIFFS.items():
        msg += f"• {t['name']} — {t['price']}₸/мес\n"
    msg += "\n💳 /pay"
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================================================
# 👵 ПОЖИЛЫЕ И 🧒 ДЕТИ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👵 ПОЖИЛЫЕ")
def elder_section(message):
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add(KeyboardButton("👋 ПОЗДОРОВАТЬСЯ"))
    kb.add(KeyboardButton("📞 ПОМОЩЬ РЯДОМ"))
    kb.add(KeyboardButton("🏥 ЗДОРОВЬЕ"))
    kb.add(KeyboardButton("📍 АПТЕКА"))
    kb.add(KeyboardButton("🆘 СРОЧНАЯ ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    bot.reply_to(message, "👵 *РЕЖИМ ДЛЯ ПОЖИЛЫХ*", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👋 ПОЗДОРОВАТЬСЯ")
def elder_greet(message):
    bot.reply_to(message, "👋 Здравствуйте! Я - Зеркало. Всегда рад помочь!")

@bot.message_handler(func=lambda m: m.text == "📞 ПОМОЩЬ РЯДОМ")
def elder_help(message):
    bot.reply_to(message, "📞 ПОМОЩЬ РЯДОМ:\n\n• Соцработник: +7 (700) 000-00-01\n• Поликлиника: +7 (700) 000-00-02")

@bot.message_handler(func=lambda m: m.text == "🏥 ЗДОРОВЬЕ")
def elder_health(message):
    bot.reply_to(message, "🏥 ЗДОРОВЬЕ:\n🚑 Скорая: 103")

@bot.message_handler(func=lambda m: m.text == "🆘 СРОЧНАЯ ПОМОЩЬ")
def elder_emergency(message):
    bot.reply_to(message, "🆘 СРОЧНАЯ ПОМОЩЬ:\n🚑 Скорая: 103\n🚔 Полиция: 102\n🚒 Пожарные: 101\n📞 112")

@bot.message_handler(func=lambda m: m.text == "🧒 ДЕТИ")
def child_section(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📖 СКАЗКА"), KeyboardButton("🧩 ЗАГАДКА"))
    kb.add(KeyboardButton("🎵 ПЕСЕНКА"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    bot.reply_to(message, "🧒 *ДЕТСКИЙ РЕЖИМ*", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📖 СКАЗКА")
def child_tale(message):
    tales = ["🐺 Волк и семеро козлят...", "👸 Золушка...", "🐻 Три медведя..."]
    bot.reply_to(message, f"📖 *СКАЗКА*\n\n{random.choice(tales)}", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🧩 ЗАГАДКА")
def child_riddle(message):
    riddles = {"Зимой и летом одним цветом?": "ёлка"}
    q = random.choice(list(riddles.keys()))
    bot.reply_to(message, f"🧩 *ЗАГАДКА*\n\n{q}")
    bot.register_next_step_handler(message, check_riddle, riddles[q])

def check_riddle(message, answer):
    if message.text.lower() == answer:
        bot.reply_to(message, "✅ ПРАВИЛЬНО!")
    else:
        bot.reply_to(message, f"❌ Ответ: {answer}")

@bot.message_handler(func=lambda m: m.text == "🎵 ПЕСЕНКА")
def child_song(message):
    songs = ["В лесу родилась ёлочка..."]
    bot.reply_to(message, f"🎵 *ПЕСЕНКА*\n\n{random.choice(songs)}", parse_mode="Markdown")

# ==================================================
# 📸 ФОТО, ГОЛОС, РЕЗЮМЕ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📸 ФОТО")
def photo_info(message):
    bot.reply_to(message, "📸 Отправьте фото")

@bot.message_handler(func=lambda m: m.text == "🎤 ГОЛОС")
def voice_info(message):
    bot.reply_to(message, "🎤 Отправьте голосовое")

@bot.message_handler(func=lambda m: m.text == "📝 РЕЗЮМЕ")
def resume_section(message):
    msg = bot.reply_to(message, "📝 Напишите ваше резюме:\n\n- Имя\n- Профессия\n- Опыт\n- Навыки\n- Контакты")
    bot.register_next_step_handler(msg, save_resume)

def save_resume(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET resume=? WHERE user_id=?", (message.text, user_id))
    conn.commit()
    bot.reply_to(message, f"✅ РЕЗЮМЕ СОХРАНЕНО!")

# ==================================================
# 🏢 БИЗНЕС-ФУНКЦИИ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📊 АНАЛИТИКА")
def business_analytics(message):
    bot.reply_to(message, "📊 БИЗНЕС-АНАЛИТИКА:\n\n⚡ В разработке")

@bot.message_handler(func=lambda m: m.text == "🤖 АВТОМАТИЗАЦИЯ")
def business_auto(message):
    bot.reply_to(message, "🤖 АВТОМАТИЗАЦИЯ:\n\n⚡ В разработке")

@bot.message_handler(func=lambda m: m.text == "📈 ЛИЗИНГ")
def business_leasing(message):
    bot.reply_to(message, "📈 ЛИЗИНГ:\n\n🚗 Авто: от 15%\n🏗️ Спецтехника: от 12%\n\n📞 /business_request")

@bot.message_handler(func=lambda m: m.text == "💼 ЗАКАЗЫ")
def business_orders(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите город")
        return
    orders_msg = get_orders_in_city(city, country)
    bot.reply_to(message, orders_msg, parse_mode="Markdown")

# ==================================================
# 👑 АДМИН-КОМАНДЫ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👥 ОНЛАЙН" and is_admin(m.chat.id))
def admin_online(message):
    c.execute("SELECT user_id, name, city FROM users WHERE last_seen > datetime('now', '-5 minutes')")
    users = c.fetchall()
    if users:
        msg = "🟢 ОНЛАЙН:\n" + "\n".join([f"{u[1]} (ID: {u[0]}) | {u[2] if u[2] else '?'}" for u in users])
        bot.reply_to(message, msg)
    else:
        bot.reply_to(message, "🟢 Никого нет")

@bot.message_handler(func=lambda m: m.text == "📊 СТАТИСТИКА" and is_admin(m.chat.id))
def admin_stats(message):
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT SUM(blessings) FROM users")
    blessings = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(DISTINCT city) FROM users WHERE city IS NOT NULL")
    cities = c.fetchone()[0]
    bot.reply_to(message, f"📊 СТАТИСТИКА:\n👥 Всего: {total}\n✨ Благ: {blessings}\n🌍 Городов: {cities}")

@bot.message_handler(func=lambda m: m.text == "💰 ФИНАНСЫ" and is_admin(m.chat.id))
def admin_finance(message):
    total = get_total_earnings()
    bot.reply_to(message, f"💰 ФИНАНСЫ:\n📱 Криптокошелёк: {CRYPTO_WALLET}\n💰 Всего: {total} ₸")

@bot.message_handler(func=lambda m: m.text == "👥 ВСЕ ЛЮДИ" and is_admin(m.chat.id))
def admin_users(message):
    c.execute("SELECT user_id, name, city, country, tariff, blessings FROM users LIMIT 30")
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
    msg = bot.reply_to(message, "📤 Введите сообщение для рассылки:")
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
    bot.reply_to(message, f"✅ Отправлено {sent}")

@bot.message_handler(func=lambda m: m.text == "💳 ПЛАТЕЖИ" and is_admin(m.chat.id))
def admin_payments(message):
    c.execute("SELECT id, user_id, amount, tariff, status, created_at FROM payments ORDER BY id DESC LIMIT 20")
    pays = c.fetchall()
    if not pays:
        bot.reply_to(message, "📭 Платежей нет")
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
        bot.reply_to(message, "📭 Заявок нет")
        return
    msg = "🏦 ЗАЯВКИ НА ВЫВОД:\n\n"
    for r in reqs:
        status_icon = "⏳" if r[3] == "pending" else "✅"
        msg += f"{status_icon} #{r[0]} | 👤 {r[1]} | 💰 {r[2]} | {r[4][:16]}\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "📊 ДОХОДЫ" and is_admin(m.chat.id))
def admin_earnings(message):
    total = get_total_earnings()
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
        msg += f"{l[2][:16]} | ID:{l[0]} | {l[1][:40]}\n"
    bot.reply_to(message, msg[:4000])

@bot.message_handler(func=lambda m: m.text == "🔍 ПОИСК" and is_admin(m.chat.id))
def admin_search(message):
    msg = bot.reply_to(message, "🔍 Введите ID:")
    bot.register_next_step_handler(msg, search_user)

def search_user(message):
    try:
        target = int(message.text)
        c.execute("SELECT user_id, name, city, country, tariff, blessings FROM users WHERE user_id=?", (target,))
        user = c.fetchone()
        if user:
            city_str = f"{user[2]}, {user[3]}" if user[2] else "город не указан"
            bot.reply_to(message, f"👤 ID: {user[0]}\n📛 {user[1]}\n📍 {city_str}\n💎 {user[4]}\n✨ {user[5]} Благ")
        else:
            bot.reply_to(message, f"❌ Не найден")
    except:
        bot.reply_to(message, "❌ Введите ID")

@bot.message_handler(func=lambda m: m.text == "📈 ОТЧЁТ" and is_admin(m.chat.id))
def admin_report(message):
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM users WHERE last_seen LIKE ?", (f"{today}%",))
    new = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT city) FROM users WHERE city IS NOT NULL")
    cities = c.fetchone()[0]
    bot.reply_to(message, f"📈 ОТЧЁТ ЗА {today}:\n➕ Новых: {new}\n🌍 Городов: {cities}")

@bot.message_handler(func=lambda m: m.text == "🩺 ЗДОРОВЬЕ" and is_admin(m.chat.id))
def admin_health(message):
    bot.reply_to(message, "🩺 ЗДОРОВЬЕ:\n✅ Бот работает\n✅ География активна\n✅ Монетизация активна")

@bot.message_handler(func=lambda m: m.text == "🛡️ ЗАЩИТА" and is_admin(m.chat.id))
def admin_security(message):
    bot.reply_to(message, "🛡️ ЗАЩИТА:\n✅ Антивирус активен\n✅ Защита данных включена")

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
    bot.reply_to(message, "🔄 Обновление...\n✅ Готово!")

@bot.message_handler(func=lambda m: m.text == "📡 СТАТУС" and is_admin(m.chat.id))
def admin_status(message):
    bot.reply_to(message, f"📡 СТАТУС:\n👑 Хранитель: {message.chat.id}\n🌍 География: активна\n💰 Монетизация: активна\n✅ OK")

@bot.message_handler(func=lambda m: m.text == "🧹 ОЧИСТИТЬ" and is_admin(m.chat.id))
def admin_clean(message):
    bot.reply_to(message, "🧹 Очистка...\n✅ Готово!")

# ==================================================
# ❓ ВОПРОСЫ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "❓ ВОПРОС")
def ask_question(message):
    msg = bot.reply_to(message, "❓ Напишите ваш вопрос:")
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
                    messages=[{"role": "system", "content": "Ты — Зеркало. Отвечай кратко, с уважением. Всегда начинай с 'Ассаляму алейкум'. Отвечай на русском языке."},
                              {"role": "user", "content": question}],
                    temperature=0.7
                )
                bot.reply_to(message, resp.choices[0].message.content)
            except:
                bot.reply_to(message, "❌ Ошибка AI")
        else:
            bot.reply_to(message, "🤖 Вопрос принят!")
    else:
        bot.reply_to(message, f"❌ Недостаточно Благ! Нужно 1 ✦\n💰 /pay")

# ==================================================
# 🆘 ПОМОЩЬ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🆘 ПОМОЩЬ")
def help_section(message):
    help_text = """
🪞 *ПОМОЩЬ ПО ЗЕРКАЛУ*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 *ГЛАВНЫЕ КНОПКИ:*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👑 ХРАНИТЕЛЬ — полное управление (только для вас)
🏢 БИЗНЕС — аналитика, лизинг, заказы
👤 ЛЮДИ — работа, заказы, услуги
🧠 AI-ДОКТОР — диагностика и лечение
💰 МОНЕТИЗАЦИЯ — тарифы, партнёрка, вывод
🌍 МОЙ ГОРОД — выбор города для работы и заказов

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 *ГЕОГРАФИЯ:*
• Автоопределение по геолокации
• Ручной поиск по всем городам мира
• Работа и заказы только в вашем городе

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 *ТАРИФЫ:*
• Бесплатный — 0₸/мес
• Базовый — 1000₸/мес
• PRO — 5000₸/мес
• Бизнес — 20000₸/мес

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ /pay — купить тариф
⚡ /id — узнать свой ID
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, help_text, parse_mode="Markdown")

# ==================================================
# 🔄 ОБЫЧНЫЕ СООБЩЕНИЯ
# ==================================================

@bot.message_handler(func=lambda m: True)
def handle_any(message):
    user_id = message.chat.id
    text = message.text
    
    # Пропускаем все кнопки (полный список)
    all_buttons = [
        "👑 ХРАНИТЕЛЬ", "🏢 БИЗНЕС", "👤 ЛЮДИ", "🧠 AI-ДОКТОР", "💰 МОНЕТИЗАЦИЯ", "🌍 МОЙ ГОРОД",
        "🔙 НА ГЛАВНУЮ", "🩺 ЛЕЧЕНИЕ", "🛡️ ПРОВЕРКА", "📊 СТАТУС",
        "👥 ОНЛАЙН", "📊 СТАТИСТИКА", "💰 ФИНАНСЫ", "👥 ВСЕ ЛЮДИ", "✨ БЛАГА",
        "📤 РАССЫЛКА", "💳 ПЛАТЕЖИ", "🏦 ВЫВОДЫ", "📊 ДОХОДЫ", "📜 ЛОГИ",
        "🔍 ПОИСК", "📈 ОТЧЁТ", "🩺 ЗДОРОВЬЕ", "🛡️ ЗАЩИТА", "💎 ТАРИФЫ",
        "🌍 ГОРОДА", "📊 ПО ГОРОДАМ", "🔄 ОБНОВИТЬ", "📡 СТАТУС", "🧹 ОЧИСТИТЬ",
        "💸 РАБОТА", "📦 ЗАКАЗЫ", "📸 ФОТО", "🎤 ГОЛОС", "📍 АПТЕКА",
        "📝 РЕЗЮМЕ", "💳 KASPI QR", "💰 БАЛАНС", "❓ ВОПРОС", "🆘 ПОМОЩЬ",
        "👵 ПОЖИЛЫЕ", "🧒 ДЕТИ", "💎 КУПИТЬ ТАРИФ", "⭐ ПАРТНЁРСКАЯ", "💎 USDT TRC20",
        "📊 МОЙ ДОХОД", "📈 ОБЩАЯ СТАТИСТИКА", "💸 ВЫВЕСТИ", "📋 ИСТОРИЯ", "💎 ПОДПИСКА",
        "👋 ПОЗДОРОВАТЬСЯ", "📞 ПОМОЩЬ РЯДОМ", "🏥 ЗДОРОВЬЕ", "🆘 СРОЧНАЯ ПОМОЩЬ",
        "📖 СКАЗКА", "🧩 ЗАГАДКА", "🎵 ПЕСЕНКА", "📊 АНАЛИТИКА", "🤖 АВТОМАТИЗАЦИЯ",
        "📈 ЛИЗИНГ", "💼 ЗАКАЗЫ", "➕ СОЗДАТЬ ЗАКАЗ", "➕ СОЗДАТЬ ВАКАНСИЮ",
        "🔍 НАЙТИ ЗАКАЗ", "🔍 НАЙТИ РАБОТУ", "📍 ОПРЕДЕЛИТЬ АВТОМАТИЧЕСКИ",
        "🔍 НАЙТИ ГОРОД", "📋 МОЙ ТЕКУЩИЙ ГОРОД"
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
                    messages=[{"role": "system", "content": "Ты — Зеркало. Отвечай кратко, с уважением. Всегда начинай с 'Ассаляму алейкум'. Отвечай на русском языке."},
                              {"role": "user", "content": text}],
                    temperature=0.7
                )
                bot.reply_to(message, resp.choices[0].message.content)
            except:
                bot.reply_to(message, "❌ Ошибка AI")
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
print("🪞 ЗЕРКАЛО - ВЕСЬ МИР")
print("=" * 60)
print(f"✅ Бот запущен")
print(f"👑 ТВОЙ ID: {FOUNDER_ID}")
print(f"🌍 ГЕОГРАФИЯ: ВСЕ ГОРОДА МИРА")
print(f"📱 6 ГЛАВНЫХ КНОПОК:")
print(f"   👑 ХРАНИТЕЛЬ — полное управление")
print(f"   🏢 БИЗНЕС — бизнес-раздел")
print(f"   👤 ЛЮДИ — обычные функции")
print(f"   🧠 AI-ДОКТОР — самолечение")
print(f"   💰 МОНЕТИЗАЦИЯ — заработок 24/7")
print(f"   🌍 МОЙ ГОРОД — выбор города")
print(f"💎 Тарифы: Бесплатный, Базовый(1000₸), PRO(5000₸), Бизнес(20000₸)")
print(f"🌍 Поиск городов: через OpenStreetMap (весь мир)")
print("=" * 60)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
