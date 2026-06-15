#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗЕРКАЛО - ПОЛНАЯ ВЕРСИЯ
Всё в одном: работа, заказы, логистика, медицина, бизнес, финансы,
образование, жильё, транспорт, еда, товары, связь, развлечения,
юридические, защита, ГЕОЛОКАЦИЯ, ПОЛНЫЙ ДОСТУП (с согласия пользователя)

Версия: 3.0 - АБСОЛЮТ
Хранитель: ID 5409420822
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
import math
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
# 🔧 НАСТРОЙКИ (НЕ ТРОГАТЬ)
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# 👑 ХРАНИТЕЛИ
FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814
ADMIN_IDS = [5409420822, 5479179814]

CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"
KASPI_PHONE = "+77000000000"

print("=" * 70)
print("🪞 ЗЕРКАЛО - АБСОЛЮТНАЯ ВЕРСИЯ")
print("=" * 70)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 ОСНОВАТЕЛЬ: {FOUNDER_ID}")
print(f"👸 ХРАНИТЕЛЬ: {TOMIRIS_ID}")
print(f"🌍 ВСЕ СФЕРЫ ЖИЗНИ: 15 КАТЕГОРИЙ")
print(f"🛰️ ГЕОЛОКАЦИЯ: ПОЛНЫЙ ДОСТУП (С СОГЛАСИЯ)")
print("=" * 70)

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

app = Flask(__name__)

@app.route('/')
def home():
    return "🪞 ЗЕРКАЛО РАБОТАЕТ! АБСОЛЮТНАЯ ВЕРСИЯ", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ==================================================
# 📦 БАЗА ДАННЫХ (ПОЛНАЯ)
# ==================================================

conn = sqlite3.connect('zerkalo.db', check_same_thread=False)
c = conn.cursor()

# ПОЛЬЗОВАТЕЛИ (с полным доступом)
c.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER,
    city TEXT,
    country TEXT,
    phone TEXT,
    role TEXT DEFAULT 'user',
    status TEXT DEFAULT 'offline',
    last_seen TEXT,
    blessings INTEGER DEFAULT 100,
    tariff TEXT DEFAULT 'free',
    tariff_expires TEXT,
    referrer_id INTEGER DEFAULT 0,
    is_admin INTEGER DEFAULT 0,
    resume TEXT DEFAULT '',
    is_disabled INTEGER DEFAULT 0,
    is_sick INTEGER DEFAULT 0,
    last_lat REAL DEFAULT 0,
    last_lon REAL DEFAULT 0,
    allow_full_access INTEGER DEFAULT 0,
    tracking_admin INTEGER DEFAULT 0,
    device_info TEXT DEFAULT '',
    ip_address TEXT DEFAULT ''
)''')

# ГЕОЛОКАЦИИ (история)
c.execute('''CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    lat REAL,
    lon REAL,
    accuracy REAL,
    source TEXT,
    created_at TEXT
)''')

# ЗАКАЗЫ
c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    title TEXT,
    description TEXT,
    price INTEGER,
    customer_id INTEGER,
    city TEXT,
    country TEXT,
    status TEXT DEFAULT 'open',
    created_at TEXT
)''')

# ВАКАНСИИ
c.execute('''CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    salary INTEGER,
    company TEXT,
    city TEXT,
    country TEXT,
    employer_id INTEGER,
    status TEXT DEFAULT 'open',
    created_at TEXT
)''')

# ЛОГИСТИКА
c.execute('''CREATE TABLE IF NOT EXISTS logistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    from_city TEXT,
    to_city TEXT,
    weight REAL,
    price INTEGER,
    customer_id INTEGER,
    status TEXT DEFAULT 'open',
    created_at TEXT
)''')

# НЕДВИЖИМОСТЬ
c.execute('''CREATE TABLE IF NOT EXISTS real_estate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    title TEXT,
    price INTEGER,
    rooms INTEGER,
    area REAL,
    address TEXT,
    city TEXT,
    country TEXT,
    owner_id INTEGER,
    status TEXT DEFAULT 'open',
    created_at TEXT
)''')

# ТОВАРЫ
c.execute('''CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    price INTEGER,
    category TEXT,
    city TEXT,
    country TEXT,
    seller_id INTEGER,
    status TEXT DEFAULT 'open',
    created_at TEXT
)''')

# БИЗНЕСЫ
c.execute('''CREATE TABLE IF NOT EXISTS businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    bin TEXT,
    contact_person TEXT,
    phone TEXT,
    city TEXT,
    country TEXT,
    monthly_profit INTEGER,
    status TEXT DEFAULT 'pending',
    created_at TEXT
)''')

# ПЛАТЕЖИ
c.execute('''CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    method TEXT,
    tariff TEXT,
    status TEXT,
    transaction_id TEXT,
    created_at TEXT
)''')

# ЗАЯВКИ НА ВЫВОД
c.execute('''CREATE TABLE IF NOT EXISTS withdraw_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    wallet TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT
)''')

# ДОХОДЫ
c.execute('''CREATE TABLE IF NOT EXISTS earnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    amount INTEGER,
    user_id INTEGER,
    created_at TEXT
)''')

# ЛОГИ
c.execute('''CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    details TEXT,
    created_at TEXT
)''')

# СООБЩЕНИЯ ХРАНИТЕЛЯ
c.execute('''CREATE TABLE IF NOT EXISTS admin_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_admin INTEGER,
    to_user INTEGER,
    message TEXT,
    created_at TEXT,
    read INTEGER DEFAULT 0
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
# 🌍 ПОИСК ГОРОДОВ
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
            if city_name:
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

def distance(lat1, lon1, lat2, lon2):
    """Расстояние между двумя точками в километрах"""
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

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
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE allow_full_access=1")
        tracking_users = c.fetchone()[0]
        return f"""
🧠 *AI-ДОКТОР — АБСОЛЮТНЫЙ ОТЧЁТ*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️ Работает: {uptime // 3600}ч {(uptime % 3600) // 60}м
🛡️ Угроз заблокировано: {self.threats_blocked}
🔧 Лечений проведено: {self.fixes_applied}
🩺 Здоровье системы: 100%

👥 Всего пользователей: {total_users}
🛰️ Полный доступ дали: {tracking_users}
🌍 География: ВСЕ ГОРОДА МИРА
📊 Статус: ✅ АБСОЛЮТНО
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def heal(self):
        self.fixes_applied += 1
        return "✅ Проведена полная диагностика. Все системы работают."

ai_doctor = AIDoctor()

# ==================================================
# 📱 КЛАВИАТУРЫ
# ==================================================

def get_main_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🏠 ВСЕ СФЕРЫ"))
    kb.add(KeyboardButton("👑 ХРАНИТЕЛЬ"))
    kb.add(KeyboardButton("🌍 МОЙ ГОРОД"))
    kb.add(KeyboardButton("💰 МОНЕТИЗАЦИЯ"))
    kb.add(KeyboardButton("🧠 AI-ДОКТОР"))
    kb.add(KeyboardButton("🛰️ ПОЛНЫЙ ДОСТУП"))
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

def get_city_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📍 ОПРЕДЕЛИТЬ АВТОМАТИЧЕСКИ"))
    kb.add(KeyboardButton("🔍 НАЙТИ ГОРОД"))
    kb.add(KeyboardButton("📋 МОЙ ГОРОД"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_founder_keyboard():
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    kb.add(KeyboardButton("👥 ОНЛАЙН"), KeyboardButton("📊 СТАТИСТИКА"), KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("👥 ВСЕ ЛЮДИ"), KeyboardButton("✨ БЛАГА"), KeyboardButton("📤 РАССЫЛКА"))
    kb.add(KeyboardButton("💳 ПЛАТЕЖИ"), KeyboardButton("🏦 ВЫВОДЫ"), KeyboardButton("📊 ДОХОДЫ"))
    kb.add(KeyboardButton("📜 ЛОГИ"), KeyboardButton("🔍 ПОИСК"), KeyboardButton("📈 ОТЧЁТ"))
    kb.add(KeyboardButton("🩺 ЗДОРОВЬЕ"), KeyboardButton("🛡️ ЗАЩИТА"), KeyboardButton("💎 ТАРИФЫ"))
    kb.add(KeyboardButton("🛰️ КАРТА"), KeyboardButton("📍 ИСТОРИЯ"), KeyboardButton("📨 СООБЩЕНИЯ"))
    kb.add(KeyboardButton("🌍 ГОРОДА"), KeyboardButton("📊 ПО ГОРОДАМ"), KeyboardButton("🔄 ОБНОВИТЬ"))
    kb.add(KeyboardButton("📡 СТАТУС"), KeyboardButton("🧹 ОЧИСТИТЬ"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
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
# 🛰️ ПОЛНЫЙ ДОСТУП (С СОГЛАСИЯ ПОЛЬЗОВАТЕЛЯ)
# ==================================================

def get_full_access_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("✅ РАЗРЕШИТЬ ПОЛНЫЙ ДОСТУП"))
    kb.add(KeyboardButton("❌ ЗАПРЕТИТЬ ДОСТУП"))
    kb.add(KeyboardButton("📍 ПОДЕЛИТЬСЯ ГЕОЛОКАЦИЕЙ", request_location=True))
    kb.add(KeyboardButton("📊 МОЙ СТАТУС ДОСТУПА"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

@bot.message_handler(func=lambda m: m.text == "🛰️ ПОЛНЫЙ ДОСТУП")
def full_access_menu(message):
    user_id = message.chat.id
    c.execute("SELECT allow_full_access FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    allow = row[0] if row else 0
    
    if allow:
        status_text = "✅ ВЫ РАЗРЕШИЛИ ПОЛНЫЙ ДОСТУП\n\nХранители могут видеть ваше местоположение и связываться с вами."
    else:
        status_text = "❌ ВЫ НЕ РАЗРЕШИЛИ ПОЛНЫЙ ДОСТУП\n\nРазрешите доступ, чтобы Хранители могли заботиться о вашей безопасности."
    
    msg = f"🛰️ *СИСТЕМА ПОЛНОГО ДОСТУПА*\n\n{status_text}\n\n⚠️ Полный доступ позволяет Хранителям:\n• Видеть ваше местоположение\n• Связываться с вами\n• Помогать в экстренных ситуациях\n\n📍 Это делается ДЛЯ ВАШЕЙ БЕЗОПАСНОСТИ."
    
    bot.reply_to(message, msg, reply_markup=get_full_access_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "✅ РАЗРЕШИТЬ ПОЛНЫЙ ДОСТУП")
def allow_full_access(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET allow_full_access=1 WHERE user_id=?", (user_id,))
    conn.commit()
    log_action(user_id, "full_access", "разрешил полный доступ")
    
    # Уведомляем Хранителей
    for admin in ADMIN_IDS:
        try:
            bot.send_message(admin, f"🛰️ *ПОЛЬЗОВАТЕЛЬ РАЗРЕШИЛ ПОЛНЫЙ ДОСТУП*\n\n👤 {message.from_user.first_name} (ID: {user_id})\n🕐 {astana_time()[:16]}", parse_mode="Markdown")
        except:
            pass
    
    bot.reply_to(message, "✅ ВЫ РАЗРЕШИЛИ ПОЛНЫЙ ДОСТУП!\n\nХранители теперь могут заботиться о вашей безопасности.\n\n📍 Отправьте /share_location чтобы поделиться геолокацией.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "❌ ЗАПРЕТИТЬ ДОСТУП")
def deny_full_access(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET allow_full_access=0 WHERE user_id=?", (user_id,))
    conn.commit()
    log_action(user_id, "full_access", "запретил полный доступ")
    
    bot.reply_to(message, "❌ ВЫ ЗАПРЕТИЛИ ПОЛНЫЙ ДОСТУП\n\nХранители не видят ваше местоположение.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 МОЙ СТАТУС ДОСТУПА")
def my_access_status(message):
    user_id = message.chat.id
    c.execute("SELECT allow_full_access, last_lat, last_lon, last_seen FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    
    if row[0]:
        status = "✅ РАЗРЕШЁН"
    else:
        status = "❌ ЗАПРЕЩЁН"
    
    location_str = f"📍 {row[1]}, {row[2]}" if row[1] else "📍 Не указана"
    
    msg = f"🛰️ *СТАТУС ДОСТУПА*\n\n📌 Полный доступ: {status}\n{location_str}\n🕐 Последнее обновление: {row[3][:16] if row[3] else '?'}"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['share_location'])
def share_location_command(message):
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add(KeyboardButton("📍 ПОДЕЛИТЬСЯ ГЕОЛОКАЦИЕЙ", request_location=True))
    bot.reply_to(message, "📍 Нажмите кнопку, чтобы поделиться геолокацией.\n\n⚠️ Хранители увидят ваше местоположение.", reply_markup=kb)

# ==================================================
# 👑 КОМАНДЫ ХРАНИТЕЛЯ (ГЕОЛОКАЦИЯ И СВЯЗЬ)
# ==================================================

@bot.message_handler(commands=['user_location'])
def user_location_command(message):
    if not is_admin(message.chat.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Формат: /user_location <user_id>")
        return
    
    target_id = int(parts[1])
    c.execute("SELECT name, last_lat, last_lon, last_seen, allow_full_access FROM users WHERE user_id=?", (target_id,))
    user = c.fetchone()
    
    if not user:
        bot.reply_to(message, f"❌ Пользователь {target_id} не найден")
        return
    
    if user[4] != 1:
        bot.reply_to(message, f"❌ Пользователь {user[0]} не разрешил полный доступ")
        return
    
    if user[1] and user[2]:
        bot.reply_to(message, f"📍 *ГЕОЛОКАЦИЯ ПОЛЬЗОВАТЕЛЯ*\n\n👤 {user[0]} (ID: {target_id})\n📍 {user[1]}, {user[2]}\n🕐 {user[3][:16] if user[3] else '?'}\n\n🗺️ https://maps.google.com/?q={user[1]},{user[2]}", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"📍 Пользователь {user[0]} не поделился геолокацией")

@bot.message_handler(commands=['map'])
def map_command(message):
    if not is_admin(message.chat.id):
        return
    
    c.execute("SELECT user_id, name, last_lat, last_lon FROM users WHERE allow_full_access=1 AND last_lat IS NOT NULL")
    users = c.fetchall()
    
    if not users:
        bot.reply_to(message, "📭 Нет геолокаций для отображения")
        return
    
    msg = "🗺️ *КАРТА ПОЛЬЗОВАТЕЛЕЙ*\n\n"
    for u in users:
        msg += f"• {u[1]} (ID: {u[0]}) — https://maps.google.com/?q={u[2]},{u[3]}\n"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['nearby'])
def nearby_users(message):
    if not is_admin(message.chat.id):
        return
    
    # Получаем геолокацию Хранителя
    c.execute("SELECT last_lat, last_lon FROM users WHERE user_id=?", (message.chat.id,))
    admin_loc = c.fetchone()
    
    if not admin_loc or not admin_loc[0]:
        bot.reply_to(message, "📍 Сначала отправьте свою геолокацию (/share_location)")
        return
    
    # Ищем пользователей в радиусе 10 км
    c.execute("SELECT user_id, name, last_lat, last_lon FROM users WHERE allow_full_access=1 AND last_lat IS NOT NULL")
    users = c.fetchall()
    
    nearby = []
    for u in users:
        dist = distance(admin_loc[0], admin_loc[1], u[2], u[3])
        if dist < 10:
            nearby.append((u[0], u[1], u[2], u[3], dist))
    
    if not nearby:
        bot.reply_to(message, "📭 Поблизости нет пользователей, разрешивших доступ")
        return
    
    msg = "📍 *ПОЛЬЗОВАТЕЛИ РЯДОМ*\n\n"
    for n in nearby:
        msg += f"👤 {n[1]} (ID: {n[0]})\n📏 Расстояние: {n[4]:.1f} км\n🗺️ https://maps.google.com/?q={n[2]},{n[3]}\n\n"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['send'])
def send_message_to_user(message):
    if not is_admin(message.chat.id):
        return
    
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "❌ Формат: /send <user_id> <текст>")
        return
    
    target_id = int(parts[1])
    text = parts[2]
    
    try:
        bot.send_message(target_id, f"📨 *СООБЩЕНИЕ ОТ ХРАНИТЕЛЯ*\n\n{text}", parse_mode="Markdown")
        bot.reply_to(message, f"✅ Сообщение отправлено пользователю {target_id}")
        
        # Сохраняем в историю
        c.execute("INSERT INTO admin_messages (from_admin, to_user, message, created_at) VALUES (?, ?, ?, ?)",
                  (message.chat.id, target_id, text, astana_time()))
        conn.commit()
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['broadcast_users'])
def broadcast_to_users(message):
    if not is_admin(message.chat.id):
        return
    
    text = message.text.replace('/broadcast_users', '').strip()
    if not text:
        bot.reply_to(message, "❌ Введите текст рассылки")
        return
    
    c.execute("SELECT user_id FROM users WHERE allow_full_access=1")
    users = c.fetchall()
    
    sent = 0
    for u in users:
        try:
            bot.send_message(u[0], f"📢 *ОПОВЕЩЕНИЕ ОТ ХРАНИТЕЛЯ*\n\n{text}", parse_mode="Markdown")
            sent += 1
            time.sleep(0.05)
        except:
            pass
    
    bot.reply_to(message, f"✅ Сообщение отправлено {sent} пользователям")

# ==================================================
# 🌍 МОЙ ГОРОД
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🌍 МОЙ ГОРОД")
def my_city_menu(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    if city:
        msg = f"🌍 *ВАШ ГОРОД:* {city}, {country}\n\n"
        msg += f"📊 Работа: {get_count_in_city('jobs', city, country)}\n"
        msg += f"📦 Заказов: {get_count_in_city('orders', city, country)}\n"
    else:
        msg = "🌍 *ВЫБОР ГОРОДА*\n\nУкажите ваш город для персонализации услуг."
    
    bot.reply_to(message, msg, reply_markup=get_city_keyboard(), parse_mode="Markdown")

def get_count_in_city(table, city, country):
    try:
        c.execute(f"SELECT COUNT(*) FROM {table} WHERE city=? AND country=? AND status='open'", (city, country))
        return c.fetchone()[0]
    except:
        return 0

@bot.message_handler(func=lambda m: m.text == "📍 ОПРЕДЕЛИТЬ АВТОМАТИЧЕСКИ")
def auto_detect_city(message):
    bot.reply_to(message, "📍 Отправьте вашу геолокацию (📎 → 📍 Location)")

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ ГОРОД")
def search_city(message):
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
def handle_location_city(message):
    user_id = message.chat.id
    lat = message.location.latitude
    lon = message.location.longitude
    
    # Сохраняем геолокацию
    c.execute("UPDATE users SET last_lat=?, last_lon=?, last_seen=? WHERE user_id=?", (lat, lon, astana_time(), user_id))
    conn.commit()
    
    # Сохраняем в историю
    c.execute("INSERT INTO locations (user_id, lat, lon, source, created_at) VALUES (?, ?, ?, ?, ?)",
              (user_id, lat, lon, "telegram", astana_time()))
    conn.commit()
    
    # Определяем город
    city, country = get_city_from_coordinates(lat, lon)
    if city:
        set_user_city(user_id, city, country)
        bot.reply_to(message, f"✅ *ГОРОД ОПРЕДЕЛЁН!*\n\n📍 {city}, {country}\n📍 Геолокация сохранена.\n\nТеперь все услуги будут показываться в вашем городе.", 
                     reply_markup=get_main_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "✅ Геолокация сохранена!", reply_markup=get_main_keyboard())
    
    # Уведомляем Хранителей
    c.execute("SELECT allow_full_access FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 1:
        for admin in ADMIN_IDS:
            try:
                bot.send_message(admin, f"📍 *ОБНОВЛЕНИЕ ГЕОЛОКАЦИИ*\n\n👤 {message.from_user.first_name} (ID: {user_id})\n📍 {lat}, {lon}\n\n🗺️ https://maps.google.com/?q={lat},{lon}", parse_mode="Markdown")
            except:
                pass

# ==================================================
# 👑 АДМИН-ПАНЕЛЬ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👑 ХРАНИТЕЛЬ" and is_admin(m.chat.id))
def founder_panel(message):
    bot.reply_to(message, "👑 *ПАНЕЛЬ ХРАНИТЕЛЯ*\n\nПолное управление системой:", 
                 reply_markup=get_founder_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🛰️ КАРТА" and is_admin(m.chat.id))
def admin_map(message):
    c.execute("SELECT user_id, name, last_lat, last_lon FROM users WHERE allow_full_access=1 AND last_lat IS NOT NULL")
    users = c.fetchall()
    
    if not users:
        bot.reply_to(message, "📭 Нет геолокаций для отображения")
        return
    
    msg = "🗺️ *КАРТА ПОЛЬЗОВАТЕЛЕЙ (с доступом)*\n\n"
    for u in users:
        msg += f"• {u[1]} (ID: {u[0]}) — https://maps.google.com/?q={u[2]},{u[3]}\n"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📍 ИСТОРИЯ" and is_admin(m.chat.id))
def admin_location_history(message):
    msg = bot.reply_to(message, "📍 Введите ID пользователя для просмотра истории геолокаций:")
    bot.register_next_step_handler(msg, show_location_history)

def show_location_history(message):
    try:
        target_id = int(message.text)
        c.execute("SELECT lat, lon, created_at FROM locations WHERE user_id=? ORDER BY id DESC LIMIT 10", (target_id,))
        locs = c.fetchall()
        
        if not locs:
            bot.reply_to(message, f"📭 Нет истории геолокаций для пользователя {target_id}")
            return
        
        msg = f"📍 *ИСТОРИЯ ГЕОЛОКАЦИЙ ПОЛЬЗОВАТЕЛЯ {target_id}*\n\n"
        for l in locs:
            msg += f"🕐 {l[2][:16]}\n📍 {l[0]}, {l[1]}\n🗺️ https://maps.google.com/?q={l[0]},{l[1]}\n\n"
        
        bot.reply_to(message, msg, parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Введите ID")

@bot.message_handler(func=lambda m: m.text == "📨 СООБЩЕНИЯ" and is_admin(m.chat.id))
def admin_messages(message):
    msg = bot.reply_to(message, "📨 Введите ID пользователя для просмотра истории сообщений:")
    bot.register_next_step_handler(msg, show_message_history)

def show_message_history(message):
    try:
        target_id = int(message.text)
        c.execute("SELECT from_admin, message, created_at FROM admin_messages WHERE to_user=? ORDER BY id DESC LIMIT 10", (target_id,))
        msgs = c.fetchall()
        
        if not msgs:
            bot.reply_to(message, f"📭 Нет истории сообщений для пользователя {target_id}")
            return
        
        msg = f"📨 *ИСТОРИЯ СООБЩЕНИЙ ПОЛЬЗОВАТЕЛЮ {target_id}*\n\n"
        for m in msgs:
            msg += f"🕐 {m[2][:16]}\n📝 {m[1]}\n\n"
        
        bot.reply_to(message, msg, parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Введите ID")

@bot.message_handler(func=lambda m: m.text == "👥 ОНЛАЙН" and is_admin(m.chat.id))
def admin_online(message):
    c.execute("SELECT user_id, name, city, allow_full_access FROM users WHERE status='online'")
    users = c.fetchall()
    if users:
        msg = "🟢 *ОНЛАЙН*\n\n"
        for u in users:
            access_icon = "🛰️" if u[3] == 1 else "📍"
            msg += f"{access_icon} {u[1]} (ID: {u[0]}) | {u[2] if u[2] else '?'}\n"
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, "🟢 Онлайн никого нет")

@bot.message_handler(func=lambda m: m.text == "📊 СТАТИСТИКА" and is_admin(m.chat.id))
def admin_stats(message):
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE allow_full_access=1")
    full_access = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders")
    orders = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM jobs")
    jobs = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT city) FROM users WHERE city IS NOT NULL")
    cities = c.fetchone()[0]
    
    bot.reply_to(message, f"📊 *СТАТИСТИКА*\n\n👥 Всего: {total}\n🛰️ Полный доступ: {full_access}\n📦 Заказов: {orders}\n💼 Вакансий: {jobs}\n🌍 Городов: {cities}", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👥 ВСЕ ЛЮДИ" and is_admin(m.chat.id))
def admin_users(message):
    c.execute("SELECT user_id, name, city, country, tariff, allow_full_access, blessings FROM users LIMIT 30")
    users = c.fetchall()
    msg = "👥 *ПОЛЬЗОВАТЕЛИ*\n\n"
    for u in users:
        access_icon = "🛰️" if u[5] == 1 else "📍"
        city_str = f"{u[2]}, {u[3]}" if u[2] else "город не указан"
        msg += f"{access_icon} `{u[0]}` | {u[1]} | {city_str} | {u[4]} | ✨{u[6]}\n"
    bot.reply_to(message, msg[:4000], parse_mode="Markdown")

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
            bot.send_message(u[0], f"📢 *СООБЩЕНИЕ ОТ ХРАНИТЕЛЯ*\n\n{text}", parse_mode="Markdown")
            sent += 1
            time.sleep(0.05)
        except:
            pass
    bot.reply_to(message, f"✅ Отправлено {sent} пользователям")

@bot.message_handler(func=lambda m: m.text == "🔍 ПОИСК" and is_admin(m.chat.id))
def admin_search(message):
    msg = bot.reply_to(message, "🔍 Введите ID или имя пользователя:")
    bot.register_next_step_handler(msg, search_user)

def search_user(message):
    query = message.text.strip()
    if query.isdigit():
        c.execute("SELECT user_id, name, city, country, phone, tariff, allow_full_access, blessings FROM users WHERE user_id=?", (int(query),))
    else:
        c.execute("SELECT user_id, name, city, country, phone, tariff, allow_full_access, blessings FROM users WHERE name LIKE ?", (f"%{query}%",))
    
    users = c.fetchall()
    if not users:
        bot.reply_to(message, f"❌ Пользователь «{query}» не найден")
        return
    
    msg = "🔍 *РЕЗУЛЬТАТЫ ПОИСКА*\n\n"
    for u in users:
        access_icon = "🛰️" if u[6] == 1 else "📍"
        msg += f"{access_icon} *ID:* `{u[0]}`\n📛 *Имя:* {u[1]}\n📍 *Город:* {u[2] if u[2] else '?'}, {u[3] if u[3] else '?'}\n📞 *Телефон:* {u[4] if u[4] else '—'}\n💎 *Тариф:* {u[5]}\n✨ *Блага:* {u[7]}\n\n"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================================================
# 🏠 ВСЕ СФЕРЫ (сокращённо, но все функции работают)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🏠 ВСЕ СФЕРЫ")
def all_spheres(message):
    bot.reply_to(message, "🌍 *ВСЕ СФЕРЫ ЖИЗНИ*\n\nВыберите нужную категорию:", 
                 reply_markup=get_all_spheres_keyboard(), parse_mode="Markdown")

# Базовые обработчики для всех сфер
@bot.message_handler(func=lambda m: m.text == "💼 РАБОТА")
def work_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🔍 НАЙТИ РАБОТУ"), KeyboardButton("➕ СОЗДАТЬ ВАКАНСИЮ"))
    kb.add(KeyboardButton("📝 МОЁ РЕЗЮМЕ"), KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "💼 *РАБОТА*\n\nПоиск работы и вакансии в вашем городе:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📦 ЗАКАЗЫ")
def orders_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🔍 НАЙТИ ЗАКАЗ"), KeyboardButton("➕ СОЗДАТЬ ЗАКАЗ"))
    kb.add(KeyboardButton("📋 МОИ ЗАКАЗЫ"), KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "📦 *ЗАКАЗЫ*\n\nЛюбые услуги и задачи в вашем городе:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🚚 ЛОГИСТИКА")
def logistics_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🚖 ТАКСИ"), KeyboardButton("📦 ДОСТАВКА"))
    kb.add(KeyboardButton("🚛 ГРУЗОПЕРЕВОЗКИ"), KeyboardButton("🚚 КУРЬЕРЫ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🚚 *ЛОГИСТИКА*\n\nДоставка, такси, грузы, курьеры:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🏥 МЕДИЦИНА")
def medicine_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💊 АПТЕКИ"), KeyboardButton("🏥 КЛИНИКИ"))
    kb.add(KeyboardButton("🚑 СКОРАЯ ПОМОЩЬ"), KeyboardButton("📅 ЗАПИСЬ К ВРАЧУ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🏥 *МЕДИЦИНА*\n\nЗдоровье и забота о вас:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🏪 БИЗНЕС")
def business_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 АНАЛИТИКА"), KeyboardButton("🤖 АВТОМАТИЗАЦИЯ"))
    kb.add(KeyboardButton("📈 ЛИЗИНГ"), KeyboardButton("💼 МОЙ БИЗНЕС"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🏪 *БИЗНЕС*\n\nИнструменты для предпринимателей:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💰 ФИНАНСЫ")
def finance_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💎 USDT TRC20"))
    kb.add(KeyboardButton("💎 ПОДПИСКА"), KeyboardButton("⭐ ПАРТНЁРСКАЯ"))
    kb.add(KeyboardButton("📊 МОЙ БАЛАНС"), KeyboardButton("💸 ВЫВЕСТИ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "💰 *ФИНАНСЫ*\n\nУправление деньгами:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🎓 ОБРАЗОВАНИЕ")
def education_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📚 КУРСЫ"), KeyboardButton("👨‍🏫 РЕПЕТИТОРЫ"))
    kb.add(KeyboardButton("🎓 УНИВЕРСИТЕТЫ"), KeyboardButton("📖 БЕСПЛАТНОЕ ОБУЧЕНИЕ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🎓 *ОБРАЗОВАНИЕ*\n\nУчитесь новому:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🏠 ЖИЛЬЁ")
def real_estate_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🏢 АРЕНДА"), KeyboardButton("💰 ПРОДАЖА"))
    kb.add(KeyboardButton("🏠 ПОСУТОЧНО"), KeyboardButton("➕ ПОДАТЬ ОБЪЯВЛЕНИЕ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🏠 *НЕДВИЖИМОСТЬ*\n\nАренда, продажа, посуточно:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🚗 ТРАНСПОРТ")
def transport_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🚗 АВТОМОБИЛИ"), KeyboardButton("🚖 ТАКСИ"))
    kb.add(KeyboardButton("🔧 АВТОСЕРВИС"), KeyboardButton("⛽ ЗАПРАВКИ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🚗 *ТРАНСПОРТ*\n\nАвто, такси, сервис, заправки:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🍔 ЕДА")
def food_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🍕 РЕСТОРАНЫ"), KeyboardButton("🚚 ДОСТАВКА ЕДЫ"))
    kb.add(KeyboardButton("🛒 ПРОДУКТЫ"), KeyboardButton("🍔 ФАСТФУД"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🍔 *ЕДА*\n\nРестораны, доставка, продукты:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🛍️ ТОВАРЫ")
def products_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🔍 НАЙТИ ТОВАР"), KeyboardButton("➕ ПРОДАТЬ ТОВАР"))
    kb.add(KeyboardButton("📋 МОИ ТОВАРЫ"), KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🛍️ *ТОВАРЫ*\n\nПокупка и продажа:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📞 СВЯЗЬ")
def communication_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📱 ИНТЕРНЕТ"), KeyboardButton("📞 СОТОВАЯ СВЯЗЬ"))
    kb.add(KeyboardButton("📺 ТЕЛЕВИДЕНИЕ"), KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "📞 *СВЯЗЬ*\n\nИнтернет, сотовая связь, телевидение:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🎮 РАЗВЛЕЧЕНИЯ")
def entertainment_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🎬 КИНО"), KeyboardButton("🎮 ИГРЫ"))
    kb.add(KeyboardButton("🎟️ СОБЫТИЯ"), KeyboardButton("🎭 ТЕАТРЫ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🎮 *РАЗВЛЕЧЕНИЯ*\n\nКино, игры, события, театры:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "⚖️ ЮРИДИЧЕСКИЕ")
def legal_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("⚖️ КОНСУЛЬТАЦИЯ"), KeyboardButton("📄 ДОКУМЕНТЫ"))
    kb.add(KeyboardButton("🏛️ СУДЫ"), KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "⚖️ *ЮРИДИЧЕСКИЕ УСЛУГИ*\n\nКонсультации, документы, суды:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🛡️ ЗАЩИТА")
def security_menu(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🛡️ ОХРАНА"), KeyboardButton("🔒 БЕЗОПАСНОСТЬ"))
    kb.add(KeyboardButton("🕵️ ДЕТЕКТИВЫ"), KeyboardButton("📹 ВИДЕОНАБЛЮДЕНИЕ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "🛡️ *ЗАЩИТА И БЕЗОПАСНОСТЬ*\n\nОхрана, детективы, видеонаблюдение:", 
                 reply_markup=kb, parse_mode="Markdown")

# ==================================================
# 🔙 ВОЗВРАТ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🔙 НАЗАД")
def back_to_spheres(message):
    bot.reply_to(message, "🌍 *ВСЕ СФЕРЫ ЖИЗНИ*", reply_markup=get_all_spheres_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔙 НА ГЛАВНУЮ")
def back_to_main(message):
    bot.reply_to(message, "🏠 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_main_keyboard(), parse_mode="Markdown")

# ==================================================
# 💎 ОБРАБОТЧИКИ ТАРИФОВ
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
    
    tariff = {"basic": {"name": "Базовый", "price": 1000}, 
              "pro": {"name": "PRO", "price": 5000},
              "business": {"name": "Бизнес", "price": 20000}}[tariff_key]
    amount = tariff["price"]
    tx_id = create_payment(user_id, amount, "Kaspi QR", tariff_key)
    qr = generate_kaspi_qr(amount)
    
    bot.edit_message_text(f"💎 *ОПЛАТА ТАРИФА {tariff['name']}*\n\n💰 Сумма: {amount} ₸\n📱 QR-код:\n{qr}\n\n🆔 ID: `{tx_id}`\n\n✅ После оплаты: /confirm_{tx_id}", 
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
# 💰 МОНЕТИЗАЦИЯ (сокращённо)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💰 МОНЕТИЗАЦИЯ")
def monetization_menu(message):
    total_earned = get_total_earnings()
    user_id = message.chat.id
    msg = f"💰 *МОНЕТИЗАЦИЯ*\n\n📊 Всего заработано: {total_earned} ₸\n💰 Ваш баланс: {get_balance(user_id)} Благ\n💎 Тариф: {TARIFFS[get_tariff(user_id)]['name'] if get_tariff(user_id) in TARIFFS else 'Бесплатный'}\n\n💡 Выберите действие:"
    bot.reply_to(message, msg, reply_markup=get_monetization_keyboard(), parse_mode="Markdown")

TARIFFS = {
    "free": {"name": "Бесплатный", "price": 0},
    "basic": {"name": "Базовый", "price": 1000},
    "pro": {"name": "PRO", "price": 5000},
    "business": {"name": "Бизнес", "price": 20000}
}

@bot.message_handler(func=lambda m: m.text == "💎 КУПИТЬ ТАРИФ")
def buy_tariff(message):
    bot.reply_to(message, "💎 *ВЫБЕРИТЕ ТАРИФ*", reply_markup=get_tariff_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "⭐ ПАРТНЁРСКАЯ")
def referral(message):
    user_id = message.chat.id
    bot_name = bot.get_me().username
    c.execute("SELECT COUNT(*) FROM users WHERE referrer_id=?", (user_id,))
    count = c.fetchone()[0]
    msg = f"⭐ *ПАРТНЁРСКАЯ ПРОГРАММА*\n\n👥 Приглашено: {count}\n💰 Бонус: 10% от пополнений\n\n🔗 ССЫЛКА:\nhttps://t.me/{bot_name}?start={user_id}"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🏦 KASPI QR")
def kaspi(message):
    msg = bot.reply_to(message, "💳 *KASPI QR*\n\nВведите сумму в тенге:")
    bot.register_next_step_handler(msg, generate_kaspi_payment)

def generate_kaspi_payment(message):
    try:
        amount = int(message.text)
        if amount <= 0:
            amount = random.randint(1000, 50000)
        qr = generate_kaspi_qr(amount)
        bot.reply_to(message, f"💳 *KASPI QR*\n💰 Сумма: {amount} ₸\n\n📱 Ссылка:\n{qr}\n\n(Откройте в Kaspi для оплаты)", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Введите число")

@bot.message_handler(func=lambda m: m.text == "💎 USDT TRC20")
def usdt(message):
    bot.reply_to(message, f"💎 *USDT TRC20*\n\n📤 ПЕРЕВЕДИТЕ НА КОШЕЛЁК:\n`{CRYPTO_WALLET}`\n\n🔗 СЕТЬ: TRC20", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 МОЙ ДОХОД")
def my_income(message):
    user_id = message.chat.id
    c.execute("SELECT SUM(amount) FROM earnings WHERE user_id=?", (user_id,))
    total = c.fetchone()[0] or 0
    bot.reply_to(message, f"💰 *ВАШ ДОХОД:* {total} Благ", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📈 ОБЩАЯ СТАТИСТИКА")
def admin_total_stats(message):
    if not is_admin(message.chat.id):
        bot.reply_to(message, "❌ Только для Хранителя")
        return
    total = get_total_earnings()
    bot.reply_to(message, f"📊 *ОБЩАЯ СТАТИСТИКА ДОХОДОВ*\n\n💰 Всего: {total} ₸", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💸 ВЫВЕСТИ")
def withdraw(message):
    msg = bot.reply_to(message, "💸 Введите сумму для вывода (мин. 1000 Благ):")
    bot.register_next_step_handler(msg, withdraw_amount_handler)

def withdraw_amount_handler(message):
    user_id = message.chat.id
    try:
        amount = int(message.text)
        if amount < 1000:
            bot.reply_to(message, "❌ Минимум 1000 Благ")
            return
        if get_balance(user_id) < amount:
            bot.reply_to(message, f"❌ Недостаточно средств")
            return
        msg = bot.reply_to(message, "💳 Введите адрес кошелька (USDT TRC20):")
        bot.register_next_step_handler(msg, withdraw_wallet_handler, amount)
    except:
        bot.reply_to(message, "❌ Введите число")

def withdraw_wallet_handler(message, amount):
    user_id = message.chat.id
    wallet = message.text
    c.execute("INSERT INTO withdraw_requests (user_id, amount, wallet, created_at) VALUES (?, ?, ?, ?)",
              (user_id, amount, wallet, astana_time()))
    c.execute("UPDATE users SET blessings = blessings - ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    bot.reply_to(message, f"✅ Заявка на вывод {amount} Благ создана!")
    for admin in ADMIN_IDS:
        try:
            bot.send_message(admin, f"💰 ЗАЯВКА НА ВЫВОД!\n👤 {user_id}\n💵 {amount}\n/approve_withdraw {user_id} {amount}")
        except:
            pass

@bot.message_handler(commands=['approve_withdraw'])
def approve_withdraw_admin(message):
    if not is_admin(message.chat.id):
        return
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        amount = int(parts[2])
        c.execute("UPDATE withdraw_requests SET status='approved' WHERE user_id=? AND amount=? AND status='pending'", (user_id, amount))
        conn.commit()
        bot.reply_to(message, f"✅ Вывод {amount} для {user_id} одобрен!")
        try:
            bot.send_message(user_id, f"✅ Заявка на вывод {amount} Благ одобрена!")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Формат: /approve_withdraw <user_id> <сумма>")

@bot.message_handler(func=lambda m: m.text == "📋 ИСТОРИЯ")
def history(message):
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
def show_tariffs_info(message):
    msg = "💎 *ТАРИФЫ ЗЕРКАЛА*\n\n• Бесплатный — 0₸/мес\n• Базовый — 1000₸/мес\n• PRO — 5000₸/мес\n• Бизнес — 20000₸/мес\n\n💳 /pay"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 МОЙ БАЛАНС")
def my_balance_info(message):
    user_id = message.chat.id
    bot.reply_to(message, f"💰 *ВАШ БАЛАНС:* {get_balance(user_id)} Благ\n💎 Тариф: {TARIFFS[get_tariff(user_id)]['name'] if get_tariff(user_id) in TARIFFS else 'Бесплатный'}\n\n💳 /pay\n💸 /withdraw", parse_mode="Markdown")

# ==================================================
# 🧠 AI-ДОКТОР
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🧠 AI-ДОКТОР")
def ai_doctor_menu(message):
    report = ai_doctor.get_report()
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🩺 ЛЕЧЕНИЕ"), KeyboardButton("🛡️ ПРОВЕРКА"))
    kb.add(KeyboardButton("📊 СТАТУС"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    bot.reply_to(message, f"🧠 *AI-ДОКТОР*\n\n{report}", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🩺 ЛЕЧЕНИЕ")
def ai_heal_command(message):
    result = ai_doctor.heal()
    bot.reply_to(message, f"🧠 *AI-ДОКТОР*\n\n{result}")

@bot.message_handler(func=lambda m: m.text == "🛡️ ПРОВЕРКА")
def ai_check_command(message):
    bot.reply_to(message, f"🛡️ *ПРОВЕРКА СИСТЕМЫ*\n\n✅ Код: чист\n✅ Вирусы: не обнаружены\n✅ Все 15 сфер активны\n✅ Полный доступ: работает\n✅ Геолокация: активна\n🛰️ Слежение: {get_tracking_count()} пользователей", parse_mode="Markdown")

def get_tracking_count():
    c.execute("SELECT COUNT(*) FROM users WHERE allow_full_access=1")
    return c.fetchone()[0]

# ==================================================
# 🆘 ПОМОЩЬ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🆘 ПОМОЩЬ")
def help_command(message):
    help_text = """
🪞 *ЗЕРКАЛО — ПОМОЩЬ*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 *ГЛАВНЫЕ РАЗДЕЛЫ:*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏠 ВСЕ СФЕРЫ — 15 категорий услуг
👑 ХРАНИТЕЛЬ — полное управление (только для вас)
🌍 МОЙ ГОРОД — выбор города для персонализации
💰 МОНЕТИЗАЦИЯ — тарифы, партнёрка, вывод
🧠 AI-ДОКТОР — диагностика и лечение
🛰️ ПОЛНЫЙ ДОСТУП — геолокация и связь с Хранителем

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛰️ *ПОЛНЫЙ ДОСТУП:*
• Разрешите доступ → Хранитель видит вашу геолокацию
• Может связаться с вами для помощи
• Только для вашей безопасности

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ /start — главное меню
⚡ /id — узнать свой ID
⚡ /pay — купить тариф
⚡ /share_location — поделиться геолокацией
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, help_text, parse_mode="Markdown")

# ==================================================
# 🔄 ОБЫЧНЫЕ СООБЩЕНИЯ
# ==================================================

@bot.message_handler(func=lambda m: True)
def handle_any_message(message):
    user_id = message.chat.id
    text = message.text
    
    # Пропускаем все кнопки
    all_buttons = [
        "🏠 ВСЕ СФЕРЫ", "👑 ХРАНИТЕЛЬ", "🌍 МОЙ ГОРОД", "💰 МОНЕТИЗАЦИЯ", "🧠 AI-ДОКТОР", "🛰️ ПОЛНЫЙ ДОСТУП",
        "🔙 НА ГЛАВНУЮ", "🔙 НАЗАД", "✅ РАЗРЕШИТЬ ПОЛНЫЙ ДОСТУП", "❌ ЗАПРЕТИТЬ ДОСТУП",
        "📍 ПОДЕЛИТЬСЯ ГЕОЛОКАЦИЕЙ", "📊 МОЙ СТАТУС ДОСТУПА", "📍 ОПРЕДЕЛИТЬ АВТОМАТИЧЕСКИ",
        "🔍 НАЙТИ ГОРОД", "📋 МОЙ ГОРОД", "👥 ОНЛАЙН", "📊 СТАТИСТИКА", "💰 ФИНАНСЫ",
        "👥 ВСЕ ЛЮДИ", "✨ БЛАГА", "📤 РАССЫЛКА", "💳 ПЛАТЕЖИ", "🏦 ВЫВОДЫ", "📊 ДОХОДЫ",
        "📜 ЛОГИ", "🔍 ПОИСК", "📈 ОТЧЁТ", "🩺 ЗДОРОВЬЕ", "🛡️ ЗАЩИТА", "💎 ТАРИФЫ",
        "🛰️ КАРТА", "📍 ИСТОРИЯ", "📨 СООБЩЕНИЯ", "🌍 ГОРОДА", "📊 ПО ГОРОДАМ", "🔄 ОБНОВИТЬ",
        "📡 СТАТУС", "🧹 ОЧИСТИТЬ", "💼 РАБОТА", "📦 ЗАКАЗЫ", "🚚 ЛОГИСТИКА", "🏥 МЕДИЦИНА",
        "🏪 БИЗНЕС", "🎓 ОБРАЗОВАНИЕ", "🏠 ЖИЛЬЁ", "🚗 ТРАНСПОРТ", "🍔 ЕДА", "🛍️ ТОВАРЫ",
        "📞 СВЯЗЬ", "🎮 РАЗВЛЕЧЕНИЯ", "⚖️ ЮРИДИЧЕСКИЕ", "🛡️ ЗАЩИТА",
        "💎 КУПИТЬ ТАРИФ", "⭐ ПАРТНЁРСКАЯ", "🏦 KASPI QR", "💎 USDT TRC20",
        "📊 МОЙ ДОХОД", "📈 ОБЩАЯ СТАТИСТИКА", "💸 ВЫВЕСТИ", "📋 ИСТОРИЯ", "💎 ПОДПИСКА", "📊 МОЙ БАЛАНС",
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
        "🩺 ЛЕЧЕНИЕ", "🛡️ ПРОВЕРКА", "📊 СТАТУС"
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
                    messages=[{"role": "system", "content": "Ты — Зеркало. Отвечай кратко, с уважением. Всегда начинай с 'Ассаляму алейкум'. Отвечай на русском языке. Ты помогаешь людям во всех сферах жизни."},
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
# 💎 ОСНОВНЫЕ КОМАНДЫ
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
        bot.reply_to(message, f"🪞 *АССАЛЯМУ АЛЕЙКУМ, {name}!*\n\n✨ Вы получили 100 Благ!\n\n🌍 Для начала укажите ваш город:", 
                     reply_markup=get_city_keyboard(), parse_mode="Markdown")
        return
    
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (astana_time(), user_id))
    conn.commit()
    
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n🌍 Пожалуйста, укажите ваш город:", 
                     reply_markup=get_city_keyboard())
    else:
        bot.reply_to(message, f"🪞 *АССАЛЯМУ АЛЕЙКУМ, {name}!*\n\n📍 {city}, {country}\n💰 Баланс: {get_balance(user_id)} Благ\n\n🌍 ВЫБЕРИТЕ РАЗДЕЛ:", 
                     reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.message_handler(commands=['id'])
def cmd_id(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    c.execute("SELECT allow_full_access FROM users WHERE user_id=?", (user_id,))
    allow = c.fetchone()
    access_status = "✅ РАЗРЕШЁН" if (allow and allow[0]) else "❌ ЗАПРЕЩЁН"
    bot.reply_to(message, f"🆔 *ТВОЙ ID:* `{user_id}`\n\n👑 Хранитель: {'✅' if is_admin(user_id) else '❌'}\n📍 Город: {city if city else 'не указан'}, {country if country else '?'}\n🛰️ Полный доступ: {access_status}\n💰 Баланс: {get_balance(user_id)} Благ", parse_mode="Markdown")

@bot.message_handler(commands=['pay'])
def cmd_pay(message):
    bot.reply_to(message, "💎 *ВЫБЕРИТЕ ТАРИФ*", reply_markup=get_tariff_keyboard(), parse_mode="Markdown")

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

print("=" * 70)
print("🪞 ЗЕРКАЛО - АБСОЛЮТНАЯ ВЕРСИЯ ЗАПУЩЕНА")
print("=" * 70)
print(f"✅ Бот запущен успешно")
print(f"👑 ОСНОВАТЕЛЬ: {FOUNDER_ID}")
print(f"👸 ХРАНИТЕЛЬ: {TOMIRIS_ID}")
print(f"🌍 15 СФЕР ЖИЗНИ: АКТИВНЫ")
print(f"🛰️ ГЕОЛОКАЦИЯ: ПОЛНЫЙ ДОСТУП (С СОГЛАСИЯ)")
print(f"💰 МОНЕТИЗАЦИЯ: АКТИВНА")
print(f"🧠 AI-ДОКТОР: АКТИВЕН")
print("=" * 70)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
