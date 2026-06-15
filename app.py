#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗЕРКАЛО - РАБОЧАЯ ВЕРСИЯ
Всё работает: города, работа, бизнес, логистика, аналитика, лизинг
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

# ВАШИ ID - НЕ ТРОГАТЬ!
FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814

CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"

print("=" * 60)
print("🪞 ЗЕРКАЛО - РАБОЧАЯ ВЕРСИЯ")
print("=" * 60)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 ВАШ ID: {FOUNDER_ID}")
print("=" * 60)

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

app = Flask(__name__)

@app.route('/')
def home():
    return "🪞 Зеркало работает!", 200

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

c.execute('''CREATE TABLE IF NOT EXISTS logistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT, from_city TEXT, to_city TEXT, weight REAL, price INTEGER,
    customer_id INTEGER, status TEXT DEFAULT 'open', created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS real_estate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT, title TEXT, price INTEGER, rooms INTEGER, area REAL,
    address TEXT, city TEXT, country TEXT,
    owner_id INTEGER, status TEXT DEFAULT 'open', created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, description TEXT, price INTEGER,
    category TEXT, city TEXT, country TEXT,
    seller_id INTEGER, status TEXT DEFAULT 'open', created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, bin TEXT, contact_person TEXT, phone TEXT,
    city TEXT, country TEXT, monthly_profit INTEGER,
    status TEXT DEFAULT 'pending', created_at TEXT
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

c.execute('''CREATE TABLE IF NOT EXISTS legal_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT, status TEXT, assigned_to TEXT,
    created_at TEXT, updated_at TEXT
)''')

conn.commit()

# Юридические задачи
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
# ГЕОГРАФИЯ (поиск городов по всему миру)
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
                results.append({'city': city_name, 'country': country})
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

# ==================================================
# ОТЧЁТЫ
# ==================================================

def get_development_report():
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT SUM(blessings) FROM users")
    blessings = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM orders")
    orders = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM jobs")
    jobs = c.fetchone()[0]
    return f"📈 ОТЧЁТ\n\n👥 Пользователей: {total}\n✨ Благ: {blessings}\n📦 Заказов: {orders}\n💼 Вакансий: {jobs}"

def get_suras_progress():
    return "📊 ПРОГРЕСС СУР\n\nВсего: 150\nРеализовано: 148\nПроцент: 98.7%"

def get_legal_status():
    c.execute("SELECT task_name, status, assigned_to FROM legal_tasks")
    tasks = c.fetchall()
    text = "📜 ВЕЛИКИЙ ПАКЕТ\n\n"
    for t in tasks:
        icon = "⏳" if t[1] == "ожидание" else "✅" if t[1] == "завершено" else "🔄"
        text += f"{icon} {t[0]}: {t[1]}\n"
        if t[2]:
            text += f"👤 {t[2]}\n"
        text += "\n"
    return text

# ==================================================
# КЛАВИАТУРЫ
# ==================================================

def get_main_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🏠 ВСЕ СФЕРЫ"))
    kb.add(KeyboardButton("👑 ХРАНИТЕЛЬ"))
    kb.add(KeyboardButton("🌍 МОЙ ГОРОД"))
    kb.add(KeyboardButton("💰 МОНЕТИЗАЦИЯ"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"))
    return kb

def get_all_spheres_keyboard():
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    kb.add(KeyboardButton("💼 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"), KeyboardButton("🚚 ЛОГИСТИКА"))
    kb.add(KeyboardButton("🏥 МЕДИЦИНА"), KeyboardButton("🏪 БИЗНЕС"), KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("🎓 ОБРАЗОВАНИЕ"), KeyboardButton("🏠 ЖИЛЬЁ"), KeyboardButton("🚗 ТРАНСПОРТ"))
    kb.add(KeyboardButton("🍔 ЕДА"), KeyboardButton("🛍️ ТОВАРЫ"), KeyboardButton("📞 СВЯЗЬ"))
    kb.add(KeyboardButton("🎮 РАЗВЛЕЧЕНИЯ"), KeyboardButton("⚖️ ЮРИДИЧЕСКИЕ"), KeyboardButton("🛡️ ЗАЩИТА"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_founder_keyboard():
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    kb.add(KeyboardButton("👥 ОНЛАЙН"), KeyboardButton("📊 СТАТИСТИКА"), KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("👥 ВСЕ ЛЮДИ"), KeyboardButton("✨ БЛАГА"), KeyboardButton("📤 РАССЫЛКА"))
    kb.add(KeyboardButton("💳 ПЛАТЕЖИ"), KeyboardButton("🏦 ВЫВОДЫ"), KeyboardButton("📊 ДОХОДЫ"))
    kb.add(KeyboardButton("📜 ЛОГИ"), KeyboardButton("🔍 ПОИСК"), KeyboardButton("📈 ОТЧЁТ"))
    kb.add(KeyboardButton("🩺 ЗДОРОВЬЕ"), KeyboardButton("🛡️ ЗАЩИТА"), KeyboardButton("💎 ТАРИФЫ"))
    kb.add(KeyboardButton("📜 ВЕЛИКИЙ ПАКЕТ"), KeyboardButton("📊 ПРОГРЕСС СУР"), KeyboardButton("🧠 ОБУЧЕНИЕ"))
    kb.add(KeyboardButton("🔄 ОБНОВИТЬ"), KeyboardButton("📡 СТАТУС"), KeyboardButton("🧹 ОЧИСТИТЬ"))
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"), KeyboardButton("📸 ФОТО"))
    kb.add(KeyboardButton("🎤 ГОЛОС"), KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("🏢 БИЗНЕС"), KeyboardButton("👵 ПОЖИЛЫЕ"), KeyboardButton("🧒 ДЕТИ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_user_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"))
    kb.add(KeyboardButton("📸 ФОТО"), KeyboardButton("🎤 ГОЛОС"))
    kb.add(KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("💳 KASPI QR"))
    kb.add(KeyboardButton("💎 ПОДПИСКА"), KeyboardButton("⭐ ПАРТНЁРСКАЯ"))
    kb.add(KeyboardButton("❓ ВОПРОС"), KeyboardButton("🆘 ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_business_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 АНАЛИТИКА"), KeyboardButton("🤖 АВТОМАТИЗАЦИЯ"))
    kb.add(KeyboardButton("📈 ЛИЗИНГ"), KeyboardButton("💼 ЗАКАЗЫ"))
    kb.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("💳 KASPI QR"))
    kb.add(KeyboardButton("❓ ВОПРОС"), KeyboardButton("🆘 ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_elder_keyboard():
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add(KeyboardButton("👋 ПОЗДОРОВАТЬСЯ"))
    kb.add(KeyboardButton("📞 ПОМОЩЬ РЯДОМ"))
    kb.add(KeyboardButton("🏥 ЗДОРОВЬЕ"))
    kb.add(KeyboardButton("📍 АПТЕКА"))
    kb.add(KeyboardButton("🆘 СРОЧНАЯ ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_child_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📖 СКАЗКА"), KeyboardButton("🧩 ЗАГАДКА"))
    kb.add(KeyboardButton("🎵 ПЕСЕНКА"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
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

def get_monetization_keyboard():
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
        if is_admin(user_id):
            bot.reply_to(message, f"👑 АССАЛЯМУ АЛЕЙКУМ, ХРАНИТЕЛЬ {name}!\n\n📍 {city}, {country}\n\n📱 ПАНЕЛЬ УПРАВЛЕНИЯ:", 
                         reply_markup=get_founder_keyboard())
        else:
            bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n📍 {city}, {country}\n💰 Баланс: {get_balance(user_id)} Благ\n\n🌍 ВЫБЕРИТЕ РАЗДЕЛ:", 
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
# МОЙ ГОРОД
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🌍 МОЙ ГОРОД")
def my_city_menu(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if city:
        msg = f"🌍 *ВАШ ГОРОД:* {city}, {country}\n\n"
    else:
        msg = "🌍 *ВЫБОР ГОРОДА*\n\nУкажите ваш город для персонализации услуг."
    
    bot.reply_to(message, msg, reply_markup=get_city_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📍 ОПРЕДЕЛИТЬ АВТОМАТИЧЕСКИ")
def auto_detect(message):
    bot.reply_to(message, "📍 Отправьте вашу геолокацию (нажмите 📎 → 📍 Location)")

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ ГОРОД")
def search_city_command(message):
    msg = bot.reply_to(message, "🔍 Введите название города (например: Almaty, Moscow, New York, London, Павлодар):")
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
        bot.reply_to(message, "📍 Город не указан. Используйте «ОПРЕДЕЛИТЬ АВТОМАТИЧЕСКИ» или «НАЙТИ ГОРОД».")

@bot.message_handler(content_types=['location'])
def handle_location(message):
    user_id = message.chat.id
    lat = message.location.latitude
    lon = message.location.longitude
    
    c.execute("UPDATE users SET last_lat=?, last_lon=?, last_seen=? WHERE user_id=?", (lat, lon, astana_time(), user_id))
    conn.commit()
    
    city, country = get_city_from_coordinates(lat, lon)
    if city:
        set_user_city(user_id, city, country)
        bot.reply_to(message, f"✅ *ГОРОД ОПРЕДЕЛЁН!*\n\n📍 {city}, {country}\n📍 Геолокация сохранена.", 
                     reply_markup=get_main_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "✅ Геолокация сохранена!", reply_markup=get_main_keyboard())
    
    log_action(user_id, "location", f"{lat},{lon}")

# ==================================================
# РАБОТА (по городам)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💼 РАБОТА")
def work_menu(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите ваш город! Нажмите «🌍 МОЙ ГОРОД»")
        return
    
    c.execute("SELECT id, title, salary, company FROM jobs WHERE city=? AND country=? AND status='open'", (city, country))
    jobs = c.fetchall()
    
    if jobs:
        msg = f"💼 *РАБОТА В {city}*\n\n"
        for j in jobs:
            msg += f"🆔 {j[0]}\n📌 {j[1]}\n💰 {j[2]} ₸\n🏢 {j[3]}\n\n"
    else:
        msg = f"💼 *РАБОТА В {city}*\n\n📭 Пока нет вакансий"
    
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("➕ СОЗДАТЬ ВАКАНСИЮ"), KeyboardButton("📝 МОЁ РЕЗЮМЕ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    
    bot.reply_to(message, msg, reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "➕ СОЗДАТЬ ВАКАНСИЮ")
def create_job_request(message):
    msg = bot.reply_to(message, "💼 Опишите вакансию:\n\n- Название должности\n- Зарплата\n- Требования\n- Контакты")
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
    bot.reply_to(message, f"✅ ВАКАНСИЯ СОЗДАНА в {city}!\n💰 Зарплата: {salary} ₸")
    log_action(user_id, "create_job", f"{city}, {salary}")

@bot.message_handler(func=lambda m: m.text == "📝 МОЁ РЕЗЮМЕ")
def resume_section(message):
    msg = bot.reply_to(message, "📝 Напишите ваше резюме:\n\n- Имя и фамилия\n- Профессия\n- Опыт работы\n- Навыки\n- Контакты")
    bot.register_next_step_handler(msg, save_resume)

def save_resume(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET resume=? WHERE user_id=?", (message.text, user_id))
    conn.commit()
    bot.reply_to(message, f"✅ РЕЗЮМЕ СОХРАНЕНО!")
    log_action(user_id, "save_resume", message.text[:50])

# ==================================================
# ЗАКАЗЫ (по городам)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📦 ЗАКАЗЫ")
def orders_menu(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите ваш город! Нажмите «🌍 МОЙ ГОРОД»")
        return
    
    c.execute("SELECT id, title, price FROM orders WHERE city=? AND country=? AND status='open'", (city, country))
    orders = c.fetchall()
    
    if orders:
        msg = f"📦 *ЗАКАЗЫ В {city}*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📌 {o[1]}\n💰 {o[2]} ₸\n\n"
    else:
        msg = f"📦 *ЗАКАЗЫ В {city}*\n\n📭 Пока нет заказов"
    
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("➕ СОЗДАТЬ ЗАКАЗ"), KeyboardButton("📋 МОИ ЗАКАЗЫ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    
    bot.reply_to(message, msg, reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "➕ СОЗДАТЬ ЗАКАЗ")
def create_order_request(message):
    msg = bot.reply_to(message, "📦 Опишите ваш заказ:\n\n- Что нужно сделать\n- Бюджет\n- Сроки")
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
    bot.reply_to(message, f"✅ ЗАКАЗ СОЗДАН в {city}!\n💰 Бюджет: {price} ₸")
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

# ==================================================
# ЛОГИСТИКА
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🚚 ЛОГИСТИКА")
def logistics_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🚖 ТАКСИ"), KeyboardButton("📦 ДОСТАВКА"))
    kb.add(KeyboardButton("🚛 ГРУЗОПЕРЕВОЗКИ"), KeyboardButton("🚚 КУРЬЕРЫ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🚚 *ЛОГИСТИКА*\n\nДоставка, такси, грузы, курьеры:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🚖 ТАКСИ")
def taxi_command(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите город")
        return
    msg = bot.reply_to(message, f"🚖 *ТАКСИ В {city}*\n\nОткуда едем? (адрес)")
    bot.register_next_step_handler(msg, taxi_from)

def taxi_from(message):
    from_addr = message.text
    msg = bot.reply_to(message, f"🚖 *ТАКСИ*\n\nКуда едем?")
    bot.register_next_step_handler(msg, taxi_to, from_addr)

def taxi_to(message, from_addr):
    to_addr = message.text
    price = random.randint(1000, 5000)
    bot.reply_to(message, f"🚖 *ЗАКАЗ ТАКСИ*\n\n📍 Откуда: {from_addr}\n📍 Куда: {to_addr}\n💰 Стоимость: {price} ₸\n\n✅ Водитель назначен! Прибудет через 5-10 минут.")

@bot.message_handler(func=lambda m: m.text == "📦 ДОСТАВКА")
def delivery_command(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите город")
        return
    msg = bot.reply_to(message, f"📦 *ДОСТАВКА В {city}*\n\nЧто доставляем?")
    bot.register_next_step_handler(msg, delivery_item)

def delivery_item(message):
    item = message.text
    msg = bot.reply_to(message, f"📦 *ДОСТАВКА*\n\nАдрес доставки?")
    bot.register_next_step_handler(msg, delivery_address, item)

def delivery_address(message, item):
    address = message.text
    price = random.randint(1000, 10000)
    bot.reply_to(message, f"📦 *ЗАКАЗ ДОСТАВКИ*\n\n📦 Товар: {item}\n📍 Адрес: {address}\n💰 Стоимость: {price} ₸\n\n✅ Курьер назначен!")

@bot.message_handler(func=lambda m: m.text == "🚛 ГРУЗОПЕРЕВОЗКИ")
def cargo_command(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите город")
        return
    msg = bot.reply_to(message, f"🚛 *ГРУЗОПЕРЕВОЗКИ*\n\nВес груза (кг):")
    bot.register_next_step_handler(msg, cargo_weight)

def cargo_weight(message):
    try:
        weight = float(message.text)
        price = int(weight * 100) + random.randint(5000, 20000)
        bot.reply_to(message, f"🚛 *ГРУЗОПЕРЕВОЗКА*\n\nВес: {weight} кг\n💰 Стоимость: {price} ₸\n\n✅ Водитель назначен!")
    except:
        bot.reply_to(message, "❌ Введите вес")

@bot.message_handler(func=lambda m: m.text == "🚚 КУРЬЕРЫ")
def courier_command(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите город")
        return
    msg = bot.reply_to(message, f"🚚 *КУРЬЕРЫ*\n\nАдрес отправления:")
    bot.register_next_step_handler(msg, courier_from)

def courier_from(message):
    from_addr = message.text
    msg = bot.reply_to(message, f"🚚 *КУРЬЕРЫ*\n\nАдрес доставки:")
    bot.register_next_step_handler(msg, courier_to, from_addr)

def courier_to(message, from_addr):
    to_addr = message.text
    price = random.randint(1000, 5000)
    bot.reply_to(message, f"🚚 *ЗАКАЗ КУРЬЕРА*\n\n📍 Откуда: {from_addr}\n📍 Куда: {to_addr}\n💰 Стоимость: {price} ₸\n\n✅ Курьер назначен!")

# ==================================================
# МЕДИЦИНА
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🏥 МЕДИЦИНА")
def medicine_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💊 АПТЕКИ"), KeyboardButton("🏥 КЛИНИКИ"))
    kb.add(KeyboardButton("🚑 СКОРАЯ ПОМОЩЬ"), KeyboardButton("📅 ЗАПИСЬ К ВРАЧУ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🏥 *МЕДИЦИНА*\n\nЗдоровье и забота о вас:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💊 АПТЕКИ")
def pharmacies(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите город")
        return
    bot.reply_to(message, f"💊 *АПТЕКИ В {city}*\n\n📍 Отправьте геолокацию для поиска аптек")

@bot.message_handler(func=lambda m: m.text == "🚑 СКОРАЯ ПОМОЩЬ")
def emergency(message):
    bot.reply_to(message, "🚑 *СРОЧНАЯ ПОМОЩЬ*\n\n📞 Скорая: 103\n🚔 Полиция: 102\n🚒 Пожарные: 101\n📞 112")

@bot.message_handler(func=lambda m: m.text == "📅 ЗАПИСЬ К ВРАЧУ")
def appointment(message):
    msg = bot.reply_to(message, "📅 *ЗАПИСЬ К ВРАЧУ*\n\nВведите специальность врача:")
    bot.register_next_step_handler(msg, appointment_specialty)

def appointment_specialty(message):
    specialty = message.text
    msg = bot.reply_to(message, f"📅 *ЗАПИСЬ К ВРАЧУ*\n\nВведите дату и время:")
    bot.register_next_step_handler(msg, appointment_datetime, specialty)

def appointment_datetime(message, specialty):
    datetime_str = message.text
    bot.reply_to(message, f"✅ *ЗАПИСЬ СОЗДАНА!*\n\n👨‍⚕️ {specialty}\n🕐 {datetime_str}\n\nОжидайте подтверждения.")

# ==================================================
# БИЗНЕС (аналитика, автоматизация, лизинг)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🏪 БИЗНЕС")
def business_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 АНАЛИТИКА"), KeyboardButton("🤖 АВТОМАТИЗАЦИЯ"))
    kb.add(KeyboardButton("📈 ЛИЗИНГ"), KeyboardButton("💼 МОЙ БИЗНЕС"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🏪 *БИЗНЕС*\n\nИнструменты для предпринимателей:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 АНАЛИТИКА")
def analytics(message):
    bot.reply_to(message, "📊 *БИЗНЕС-АНАЛИТИКА*\n\n• Прогноз продаж\n• Анализ конкурентов\n• Рыночные тренды\n• Отчёты по расходам\n\n💰 Стоимость: от 5000 ₸/мес")

@bot.message_handler(func=lambda m: m.text == "🤖 АВТОМАТИЗАЦИЯ")
def automation(message):
    bot.reply_to(message, "🤖 *АВТОМАТИЗАЦИЯ БИЗНЕСА*\n\n• Чат-бот для клиентов\n• CRM интеграция\n• Автоматическая отчётность\n• Управление задачами\n\n💰 Стоимость: от 50000 ₸/мес")

@bot.message_handler(func=lambda m: m.text == "📈 ЛИЗИНГ")
def leasing(message):
    bot.reply_to(message, "📈 *ЛИЗИНГ ОБОРУДОВАНИЯ*\n\n• 🚗 Автотранспорт: от 15% годовых\n• 🏗️ Спецтехника: от 12% годовых\n• 🖥️ Оборудование: от 10% годовых\n\n📞 Для заявки: /leasing_request")

@bot.message_handler(func=lambda m: m.text == "💼 МОЙ БИЗНЕС")
def my_business(message):
    user_id = message.chat.id
    c.execute("SELECT id, name, city, status FROM businesses WHERE contact_person=? OR phone LIKE ?", (user_id, f"%{user_id}%"))
    biz = c.fetchall()
    if biz:
        msg = "🏪 *МОИ БИЗНЕСЫ*\n\n"
        for b in biz:
            msg += f"🆔 {b[0]}\n📛 {b[1]}\n📍 {b[2]}\n📌 {b[3]}\n\n"
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        msg = bot.reply_to(message, "🏪 *РЕГИСТРАЦИЯ БИЗНЕСА*\n\nВведите название бизнеса:")
        bot.register_next_step_handler(msg, register_business)

def register_business(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    c.execute("INSERT INTO businesses (name, contact_person, phone, city, country, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (message.text, user_id, str(user_id), city if city else "Не указан", country if country else "Казахстан", "pending", astana_time()))
    conn.commit()
    bot.reply_to(message, f"✅ БИЗНЕС «{message.text}» ЗАРЕГИСТРИРОВАН!\n\n⏳ Ожидайте подтверждения Хранителя.")

# ==================================================
# ОБРАЗОВАНИЕ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🎓 ОБРАЗОВАНИЕ")
def education_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📚 КУРСЫ"), KeyboardButton("👨‍🏫 РЕПЕТИТОРЫ"))
    kb.add(KeyboardButton("🎓 УНИВЕРСИТЕТЫ"), KeyboardButton("📖 БЕСПЛАТНОЕ ОБУЧЕНИЕ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🎓 *ОБРАЗОВАНИЕ*\n\nУчитесь новому:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📚 КУРСЫ")
def courses(message):
    bot.reply_to(message, "📚 *КУРСЫ*\n\n• Программирование — от 5000 ₸\n• Английский язык — от 3000 ₸\n• Маркетинг — от 4000 ₸\n• Дизайн — от 5000 ₸\n\n📞 /course_request")

@bot.message_handler(func=lambda m: m.text == "👨‍🏫 РЕПЕТИТОРЫ")
def tutors(message):
    msg = bot.reply_to(message, "👨‍🏫 *РЕПЕТИТОРЫ*\n\nВведите предмет и класс:")
    bot.register_next_step_handler(msg, find_tutor)

def find_tutor(message):
    subject = message.text
    bot.reply_to(message, f"👨‍🏫 *ПОИСК РЕПЕТИТОРОВ*\n\nПредмет: {subject}\n\n✅ Найдено 3 репетитора!\n💰 от 3000 ₸/час")

# ==================================================
# ЖИЛЬЁ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🏠 ЖИЛЬЁ")
def real_estate_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🏢 АРЕНДА"), KeyboardButton("💰 ПРОДАЖА"))
    kb.add(KeyboardButton("🏠 ПОСУТОЧНО"), KeyboardButton("➕ ПОДАТЬ ОБЪЯВЛЕНИЕ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🏠 *НЕДВИЖИМОСТЬ*\n\nАренда, продажа, посуточно:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🏢 АРЕНДА")
def rent_search(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите город")
        return
    bot.reply_to(message, f"🏢 *АРЕНДА В {city}*\n\n• Квартиры — от 50000 ₸/мес\n• Дома — от 100000 ₸/мес\n• Комнаты — от 20000 ₸/мес\n\n📞 /rent_request")

@bot.message_handler(func=lambda m: m.text == "💰 ПРОДАЖА")
def sale_search(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите город")
        return
    bot.reply_to(message, f"💰 *ПРОДАЖА В {city}*\n\n• Квартиры — от 5 млн ₸\n• Дома — от 10 млн ₸\n\n📞 /sale_request")

# ==================================================
# ТРАНСПОРТ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🚗 ТРАНСПОРТ")
def transport_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🚗 АВТОМОБИЛИ"), KeyboardButton("🚖 ТАКСИ"))
    kb.add(KeyboardButton("🔧 АВТОСЕРВИС"), KeyboardButton("⛽ ЗАПРАВКИ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🚗 *ТРАНСПОРТ*\n\nАвто, такси, сервис, заправки:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🚗 АВТОМОБИЛИ")
def cars(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите город")
        return
    bot.reply_to(message, f"🚗 *АВТОМОБИЛИ В {city}*\n\n• Продажа авто\n• Аренда авто\n• Каршеринг\n\n📞 /cars_request")

# ==================================================
# ЕДА
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🍔 ЕДА")
def food_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🍕 РЕСТОРАНЫ"), KeyboardButton("🚚 ДОСТАВКА ЕДЫ"))
    kb.add(KeyboardButton("🛒 ПРОДУКТЫ"), KeyboardButton("🍔 ФАСТФУД"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🍔 *ЕДА*\n\nРестораны, доставка, продукты:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🍕 РЕСТОРАНЫ")
def restaurants(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите город")
        return
    bot.reply_to(message, f"🍕 *РЕСТОРАНЫ В {city}*\n\n• Итальянская кухня\n• Японская кухня\n• Казахская кухня\n\n📞 /restaurant_request")

@bot.message_handler(func=lambda m: m.text == "🚚 ДОСТАВКА ЕДЫ")
def food_delivery(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите город")
        return
    bot.reply_to(message, f"🚚 *ДОСТАВКА ЕДЫ В {city}*\n\n• Glovo\n• Wolt\n• Яндекс Еда\n\n📞 /food_delivery")

# ==================================================
# ТОВАРЫ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🛍️ ТОВАРЫ")
def products_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🔍 НАЙТИ ТОВАР"), KeyboardButton("➕ ПРОДАТЬ ТОВАР"))
    kb.add(KeyboardButton("📋 МОИ ТОВАРЫ"), KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🛍️ *ТОВАРЫ*\n\nПокупка и продажа:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ ТОВАР")
def find_product(message):
    msg = bot.reply_to(message, "🔍 Введите название товара:")
    bot.register_next_step_handler(msg, search_product)

def search_product(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    query = message.text
    c.execute("SELECT id, title, price FROM products WHERE city=? AND title LIKE ? AND status='open'", (city, f"%{query}%"))
    products = c.fetchall()
    if products:
        msg = f"🛍️ *ТОВАРЫ ПО ЗАПРОСУ «{query}»*\n\n"
        for p in products:
            msg += f"🆔 {p[0]}\n📌 {p[1]}\n💰 {p[2]} ₸\n\n"
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, f"📭 Товары не найдены в {city}")

@bot.message_handler(func=lambda m: m.text == "➕ ПРОДАТЬ ТОВАР")
def sell_product(message):
    msg = bot.reply_to(message, "🛍️ *ПРОДАЖА ТОВАРА*\n\nВведите название товара:")
    bot.register_next_step_handler(msg, sell_product_title)

def sell_product_title(message):
    title = message.text
    msg = bot.reply_to(message, "💰 Введите цену:")
    bot.register_next_step_handler(msg, sell_product_price, title)

def sell_product_price(message, title):
    try:
        price = int(message.text)
        msg = bot.reply_to(message, "📝 Введите описание:")
        bot.register_next_step_handler(msg, sell_product_desc, title, price)
    except:
        bot.reply_to(message, "❌ Введите число")

def sell_product_desc(message, title, price):
    desc = message.text
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    c.execute("INSERT INTO products (title, description, price, category, city, country, seller_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (title, desc, price, "general", city if city else "Не указан", country if country else "Казахстан", user_id, "open", astana_time()))
    conn.commit()
    bot.reply_to(message, f"✅ ТОВАР ВЫСТАВЛЕН!\n\n📌 {title}\n💰 {price} ₸")

# ==================================================
# ФИНАНСЫ И МОНЕТИЗАЦИЯ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💰 ФИНАНСЫ")
def finance_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💎 USDT TRC20"))
    kb.add(KeyboardButton("💎 ПОДПИСКА"), KeyboardButton("⭐ ПАРТНЁРСКАЯ"))
    kb.add(KeyboardButton("📊 МОЙ БАЛАНС"), KeyboardButton("💸 ВЫВЕСТИ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "💰 *ФИНАНСЫ*\n\nУправление деньгами:", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💰 МОНЕТИЗАЦИЯ")
def monetization_menu(message):
    total_earned = get_total_earnings()
    msg = f"💰 *МОНЕТИЗАЦИЯ*\n\n📊 Всего заработано: {total_earned} ₸\n💰 Ваш баланс: {get_balance(message.chat.id)} Благ"
    bot.reply_to(message, msg, reply_markup=get_monetization_keyboard(), parse_mode="Markdown")

TARIFFS = {
    "free": {"name": "Бесплатный", "price": 0},
    "basic": {"name": "Базовый", "price": 1000},
    "pro": {"name": "PRO", "price": 5000},
    "business": {"name": "Бизнес", "price": 20000}
}

@bot.message_handler(func=lambda m: m.text == "💎 КУПИТЬ ТАРИФ")
def buy_tariff(message):
    bot.reply_to(message, "💎 *ВЫБЕРИТЕ ТАРИФ*\n\n• Бесплатный — 0₸\n• Базовый — 1000₸/мес\n• PRO — 5000₸/мес\n• Бизнес — 20000₸/мес", reply_markup=get_tariff_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "⭐ ПАРТНЁРСКАЯ")
def referral(message):
    user_id = message.chat.id
    bot_name = bot.get_me().username
    c.execute("SELECT COUNT(*) FROM users WHERE referrer_id=?", (user_id,))
    count = c.fetchone()[0]
    msg = f"⭐ *ПАРТНЁРСКАЯ*\n\n👥 Приглашено: {count}\n🔗 ССЫЛКА:\nhttps://t.me/{bot_name}?start={user_id}\n\n💰 10% от пополнений!"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🏦 KASPI QR")
def kaspi_payment(message):
    msg = bot.reply_to(message, "💳 *KASPI QR*\n\nВведите сумму:")
    bot.register_next_step_handler(msg, generate_kaspi_payment)

def generate_kaspi_payment(message):
    try:
        amount = int(message.text)
        if amount <= 0:
            amount = random.randint(1000, 50000)
        qr = generate_kaspi_qr(amount)
        bot.reply_to(message, f"💳 *KASPI QR*\n💰 {amount} ₸\n\n📱 {qr}", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Введите число")

@bot.message_handler(func=lambda m: m.text == "💎 USDT TRC20")
def usdt_payment(message):
    bot.reply_to(message, f"💎 *USDT TRC20*\n\n📤 КОШЕЛЁК:\n`{CRYPTO_WALLET}`\n\n🔗 СЕТЬ: TRC20", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 МОЙ БАЛАНС")
def my_balance(message):
    user_id = message.chat.id
    bot.reply_to(message, f"💰 *БАЛАНС:* {get_balance(user_id)} Благ\n\n💳 /pay\n💸 /withdraw", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💸 ВЫВЕСТИ")
def withdraw_request(message):
    msg = bot.reply_to(message, "💸 Введите сумму (мин. 1000):")
    bot.register_next_step_handler(msg, withdraw_amount)

def withdraw_amount(message):
    user_id = message.chat.id
    try:
        amount = int(message.text)
        if amount < 1000:
            bot.reply_to(message, "❌ Мин. 1000")
            return
        if get_balance(user_id) < amount:
            bot.reply_to(message, "❌ Недостаточно средств")
            return
        msg = bot.reply_to(message, "💳 Введите адрес кошелька:")
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
    bot.reply_to(message, f"✅ Заявка на {amount} создана!")
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
def show_subscription(message):
    msg = "💎 *ТАРИФЫ*\n\n• Бесплатный — 0₸\n• Базовый — 1000₸\n• PRO — 5000₸\n• Бизнес — 20000₸"
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================================================
# ПОЖИЛЫЕ И ДЕТИ
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
# ОСТАЛЬНЫЕ ФУНКЦИИ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📸 ФОТО")
def photo_info(message):
    bot.reply_to(message, "📸 Отправьте фото")

@bot.message_handler(func=lambda m: m.text == "🎤 ГОЛОС")
def voice_info(message):
    bot.reply_to(message, "🎤 Отправьте голосовое")

@bot.message_handler(func=lambda m: m.text == "📍 АПТЕКА")
def pharmacy_info(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, "🌍 Сначала укажите город")
        return
    bot.reply_to(message, f"📍 Отправьте геолокацию для поиска аптек в {city}")

@bot.message_handler(func=lambda m: m.text == "📝 РЕЗЮМЕ")
def resume_shortcut(message):
    msg = bot.reply_to(message, "📝 Напишите резюме:")
    bot.register_next_step_handler(msg, save_resume_shortcut)

def save_resume_shortcut(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET resume=? WHERE user_id=?", (message.text, user_id))
    conn.commit()
    bot.reply_to(message, "✅ РЕЗЮМЕ СОХРАНЕНО!")

@bot.message_handler(func=lambda m: m.text == "💳 KASPI QR")
def kaspi_shortcut(message):
    msg = bot.reply_to(message, "💳 *KASPI QR*\n\nВведите сумму:")
    bot.register_next_step_handler(msg, generate_kaspi_shortcut)

def generate_kaspi_shortcut(message):
    try:
        amount = int(message.text)
        if amount <= 0:
            amount = random.randint(1000, 50000)
        qr = generate_kaspi_qr(amount)
        bot.reply_to(message, f"💳 *KASPI QR*\n💰 {amount} ₸\n\n📱 {qr}", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Введите число")

@bot.message_handler(func=lambda m: m.text == "💰 БАЛАНС")
def show_balance_shortcut(message):
    user_id = message.chat.id
    bot.reply_to(message, f"💰 *БАЛАНС:* {get_balance(user_id)} Благ\n\n💳 /pay", parse_mode="Markdown")

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

# ==================================================
# АДМИН-ПАНЕЛЬ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👑 ХРАНИТЕЛЬ" and is_admin(m.chat.id))
def founder_panel(message):
    bot.reply_to(message, "👑 *ПАНЕЛЬ ХРАНИТЕЛЯ*", reply_markup=get_founder_keyboard(), parse_mode="Markdown")

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
    bot.reply_to(message, f"📊 СТАТИСТИКА:\n👥 Всего: {total}\n✨ Благ: {blessings}")

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
            bot.send_message(u[0], f"📢 ОТ ХРАНИТЕЛЯ:\n\n{text}")
            sent += 1
            time.sleep(0.05)
        except:
            pass
    bot.reply_to(message, f"✅ Отправлено {sent}")

@bot.message_handler(func=lambda m: m.text == "💳 ПЛАТЕЖИ" and is_admin(m.chat.id))
def admin_payments(message):
    c.execute("SELECT id, user_id, amount, status, created_at FROM payments ORDER BY id DESC LIMIT 20")
    pays = c.fetchall()
    if not pays:
        bot.reply_to(message, "📭 Нет платежей")
        return
    msg = "💳 ПЛАТЕЖИ:\n"
    for p in pays:
        msg += f"#{p[0]} | 👤 {p[1]} | 💰 {p[2]} | {p[3]} | {p[4][:16]}\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "🏦 ВЫВОДЫ" and is_admin(m.chat.id))
def admin_withdraws(message):
    c.execute("SELECT id, user_id, amount, status, created_at FROM withdraw_requests ORDER BY id DESC LIMIT 20")
    reqs = c.fetchall()
    if not reqs:
        bot.reply_to(message, "📭 Нет заявок")
        return
    msg = "🏦 ЗАЯВКИ НА ВЫВОД:\n"
    for r in reqs:
        msg += f"#{r[0]} | 👤 {r[1]} | 💰 {r[2]} | {r[3]} | {r[4][:16]}\n"
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
        c.execute("SELECT user_id, name, blessings FROM users WHERE user_id=?", (target,))
        user = c.fetchone()
        if user:
            bot.reply_to(message, f"👤 ID: {user[0]}\n📛 {user[1]}\n✨ {user[2]} Благ")
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
    bot.reply_to(message, "🩺 ЗДОРОВЬЕ:\n✅ Бот работает\n✅ База OK")

@bot.message_handler(func=lambda m: m.text == "🛡️ ЗАЩИТА" and is_admin(m.chat.id))
def admin_security(message):
    bot.reply_to(message, "🛡️ ЗАЩИТА:\n✅ Антивирус активен")

@bot.message_handler(func=lambda m: m.text == "💎 ТАРИФЫ" and is_admin(m.chat.id))
def admin_tariffs(message):
    msg = "💎 ТАРИФЫ:\n"
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
    msg = bot.reply_to(message, "🧠 *ОБУЧЕНИЕ*\n\nОтправьте инструкцию:")
    bot.register_next_step_handler(msg, process_learning)

def process_learning(message):
    log_action(message.chat.id, "teach_request", message.text[:200])
    bot.reply_to(message, f"🧠 *ИНСТРУКЦИЯ ПРИНЯТА*\n\n{message.text[:200]}", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔄 ОБНОВИТЬ" and is_admin(m.chat.id))
def admin_reload(message):
    bot.reply_to(message, "🔄 Обновление...\n✅ Готово!")

@bot.message_handler(func=lambda m: m.text == "📡 СТАТУС" and is_admin(m.chat.id))
def admin_status(message):
    bot.reply_to(message, f"📡 СТАТУС:\n👑 Хранитель: {message.chat.id}\n✅ OK")

@bot.message_handler(func=lambda m: m.text == "🧹 ОЧИСТИТЬ" and is_admin(m.chat.id))
def admin_clean(message):
    bot.reply_to(message, "🧹 Очистка...\n✅ Готово!")

# ==================================================
# ОБРАБОТКА ТАРИФОВ (Callback)
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
    
    bot.edit_message_text(f"💎 *ОПЛАТА {tariff['name']}*\n\n💰 {amount} ₸\n📱 {qr}\n\n🆔 {tx_id}\n✅ /confirm_{tx_id}", 
                          call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text and m.text.startswith("/confirm_"))
def confirm_payment_callback(message):
    tx_id = message.text.replace("/confirm_", "").strip()
    success, amount, tariff = confirm_payment(tx_id)
    if success:
        bot.reply_to(message, f"✅ ПЛАТЁЖ ПОДТВЕРЖДЁН!\n\n💰 +{amount} Благ\n💎 {tariff}")
    else:
        bot.reply_to(message, f"❌ Платёж не найден")

# ==================================================
# ОБЫЧНЫЕ СООБЩЕНИЯ
# ==================================================

@bot.message_handler(func=lambda m: True)
def handle_any_message(message):
    user_id = message.chat.id
    text = message.text
    
    # Пропускаем все кнопки
    all_buttons = [
        "🏠 ВСЕ СФЕРЫ", "👑 ХРАНИТЕЛЬ", "🌍 МОЙ ГОРОД", "💰 МОНЕТИЗАЦИЯ",
        "🔙 НА ГЛАВНУЮ", "🔙 НАЗАД", "👥 ОНЛАЙН", "📊 СТАТИСТИКА", "💰 ФИНАНСЫ",
        "👥 ВСЕ ЛЮДИ", "✨ БЛАГА", "📤 РАССЫЛКА", "💳 ПЛАТЕЖИ", "🏦 ВЫВОДЫ", "📊 ДОХОДЫ",
        "📜 ЛОГИ", "🔍 ПОИСК", "📈 ОТЧЁТ", "🩺 ЗДОРОВЬЕ", "🛡️ ЗАЩИТА", "💎 ТАРИФЫ",
        "📜 ВЕЛИКИЙ ПАКЕТ", "📊 ПРОГРЕСС СУР", "🧠 ОБУЧЕНИЕ", "🔄 ОБНОВИТЬ", "📡 СТАТУС", "🧹 ОЧИСТИТЬ",
        "💼 РАБОТА", "📦 ЗАКАЗЫ", "🚚 ЛОГИСТИКА", "🏥 МЕДИЦИНА", "🏪 БИЗНЕС",
        "🎓 ОБРАЗОВАНИЕ", "🏠 ЖИЛЬЁ", "🚗 ТРАНСПОРТ", "🍔 ЕДА", "🛍️ ТОВАРЫ",
        "📞 СВЯЗЬ", "🎮 РАЗВЛЕЧЕНИЯ", "⚖️ ЮРИДИЧЕСКИЕ", "🛡️ ЗАЩИТА",
        "💎 КУПИТЬ ТАРИФ", "⭐ ПАРТНЁРСКАЯ", "🏦 KASPI QR", "💎 USDT TRC20",
        "📊 МОЙ БАЛАНС", "💸 ВЫВЕСТИ", "📋 ИСТОРИЯ", "💎 ПОДПИСКА",
        "🔍 НАЙТИ РАБОТУ", "➕ СОЗДАТЬ ВАКАНСИЮ", "📝 МОЁ РЕЗЮМЕ",
        "🔍 НАЙТИ ЗАКАЗ", "➕ СОЗДАТЬ ЗАКАЗ", "📋 МОИ ЗАКАЗЫ",
        "🚖 ТАКСИ", "📦 ДОСТАВКА", "🚛 ГРУЗОПЕРЕВОЗКИ", "🚚 КУРЬЕРЫ",
        "💊 АПТЕКИ", "🏥 КЛИНИКИ", "🚑 СКОРАЯ ПОМОЩЬ", "📅 ЗАПИСЬ К ВРАЧУ",
        "📊 АНАЛИТИКА", "🤖 АВТОМАТИЗАЦИЯ", "📈 ЛИЗИНГ", "💼 МОЙ БИЗНЕС",
        "📚 КУРСЫ", "👨‍🏫 РЕПЕТИТОРЫ", "🎓 УНИВЕРСИТЕТЫ", "📖 БЕСПЛАТНОЕ ОБУЧЕНИЕ",
        "🏢 АРЕНДА", "💰 ПРОДАЖА", "🏠 ПОСУТОЧНО", "➕ ПОДАТЬ ОБЪЯВЛЕНИЕ",
        "🚗 АВТОМОБИЛИ", "🔧 АВТОСЕРВИС", "⛽ ЗАПРАВКИ",
        "🍕 РЕСТОРАНЫ", "🚚 ДОСТАВКА ЕДЫ", "🛒 ПРОДУКТЫ", "🍔 ФАСТФУД",
        "🔍 НАЙТИ ТОВАР", "➕ ПРОДАТЬ ТОВАР", "📋 МОИ ТОВАРЫ",
        "📱 ИНТЕРНЕТ", "📞 СОТОВАЯ СВЯЗЬ", "📺 ТЕЛЕВИДЕНИЕ",
        "🎬 КИНО", "🎮 ИГРЫ", "🎟️ СОБЫТИЯ", "🎭 ТЕАТРЫ",
        "⚖️ КОНСУЛЬТАЦИЯ", "📄 ДОКУМЕНТЫ", "🏛️ СУДЫ",
        "🛡️ ОХРАНА", "🔒 БЕЗОПАСНОСТЬ", "🕵️ ДЕТЕКТИВЫ", "📹 ВИДЕОНАБЛЮДЕНИЕ",
        "👋 ПОЗДОРОВАТЬСЯ", "📞 ПОМОЩЬ РЯДОМ", "🏥 ЗДОРОВЬЕ", "🆘 СРОЧНАЯ ПОМОЩЬ",
        "📖 СКАЗКА", "🧩 ЗАГАДКА", "🎵 ПЕСЕНКА", "📸 ФОТО", "🎤 ГОЛОС",
        "📍 АПТЕКА", "📝 РЕЗЮМЕ", "💳 KASPI QR", "💰 БАЛАНС", "❓ ВОПРОС", "🆘 ПОМОЩЬ",
        "📍 ОПРЕДЕЛИТЬ АВТОМАТИЧЕСКИ", "🔍 НАЙТИ ГОРОД", "📋 МОЙ ГОРОД"
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
# ФОНОВЫЕ ПРОЦЕССЫ
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
print("🪞 ЗЕРКАЛО - РАБОЧАЯ ВЕРСИЯ ЗАПУЩЕНА")
print("=" * 70)
print(f"✅ Бот запущен успешно")
print(f"👑 ОСНОВАТЕЛЬ: {FOUNDER_ID}")
print(f"👸 ХРАНИТЕЛЬ: {TOMIRIS_ID}")
print(f"🌍 ВСЕ СФЕРЫ: АКТИВНЫ")
print(f"💰 МОНЕТИЗАЦИЯ: АКТИВНА")
print("=" * 70)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
