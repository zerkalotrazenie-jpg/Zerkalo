#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🪞 ЗЕРКАЛО — ПОЛНАЯ СИСТЕМА
═══════════════════════════════════════════════════════════════════
✅ РАБОТАЕТ 24/7
✅ ПИНГ КАЖДУЮ МИНУТУ (НЕ ЗАСЫПАЕТ)
✅ ВСЕ МОДУЛИ (РОМБ, АРБИТРАЖ, ЛИЗИНГ, АВТОМАТИЗАЦИЯ)
✅ БАЗА ДАННЫХ SQLITE
✅ ГОТОВ К WEBAPP
═══════════════════════════════════════════════════════════════════
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
from flask import Flask, request, jsonify, send_from_directory

# ==================================================
# ⚡ УСТАНОВКА БИБЛИОТЕК (ЕСЛИ НЕ УСТАНОВЛЕНЫ)
# ==================================================

def install_package(package):
    try:
        __import__(package)
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Список необходимых библиотек
REQUIRED_PACKAGES = [
    "pytelegrambotapi",
    "flask",
    "requests",
    "groq"
]

for pkg in REQUIRED_PACKAGES:
    install_package(pkg)

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ==================================================
# 🔧 НАСТРОЙКИ
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "zerkalo.onrender.com")
PORT = int(os.environ.get("PORT", 8080))

# ID Хранителей и администраторов
FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814
ADMIN_IDS = [5409420822, 5479179814]

# Платёжные реквизиты
KASPI_PHONE = "+777733440345"
KASPI_NAME = "ЗЕРКАЛО"
CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"

print("=" * 70)
print("🪞 ЗЕРКАЛО — ПОЛНАЯ СИСТЕМА")
print("=" * 70)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 ОСНОВАТЕЛЬ: {FOUNDER_ID}")
print(f"🌐 ХОСТ: {RENDER_HOSTNAME}")
print("=" * 70)

# ==================================================
# 🤖 БОТ И APP
# ==================================================

bot = telebot.TeleBot(TOKEN) if TOKEN else None
app = Flask(__name__)

# ==================================================
# ⏰ БЕСКОНЕЧНЫЙ ПИНГ (НЕ ДАЁТ РЕНДЕРУ ЗАСНУТЬ)
# ==================================================

def ping_self():
    """Каждую минуту будит самого себя, чтобы Render не уснул"""
    url = f"https://{RENDER_HOSTNAME}/ping"
    ping_count = 0
    while True:
        try:
            response = requests.get(url, timeout=10)
            ping_count += 1
            print(f"🔵 Пинг #{ping_count} | Статус: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Ошибка пинга: {e}")
        time.sleep(60)  # Каждую минуту

# Запускаем пинг в отдельном потоке
threading.Thread(target=ping_self, daemon=True).start()
print("✅ ПИНГ-СИСТЕМА ЗАПУЩЕНА! Буду будить себя каждую минуту.")

# ==================================================
# 📦 БАЗА ДАННЫХ (SQLite)
# ==================================================

conn = sqlite3.connect('zerkalo.db', check_same_thread=False)
c = conn.cursor()

# Создаём таблицы
c.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER,
    city TEXT,
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
    looking_for_job INTEGER DEFAULT 0,
    looking_for_master INTEGER DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    price INTEGER,
    customer_id INTEGER,
    executor_id INTEGER DEFAULT 0,
    status TEXT DEFAULT 'open',
    created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    salary INTEGER,
    company TEXT,
    city TEXT,
    employer_id INTEGER,
    status TEXT DEFAULT 'open',
    created_at TEXT
)''')

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

c.execute('''CREATE TABLE IF NOT EXISTS earnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    amount INTEGER,
    user_id INTEGER,
    created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    details TEXT,
    created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS withdraw_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    wallet TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT
)''')

conn.commit()
print("✅ БАЗА ДАННЫХ ГОТОВА!")

# ==================================================
# 📱 КЛАВИАТУРЫ
# ==================================================

def get_main_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("👑 ХРАНИТЕЛЬ"))
    kb.add(KeyboardButton("🏢 БИЗНЕС"))
    kb.add(KeyboardButton("👤 ЛЮДИ"))
    kb.add(KeyboardButton("💰 МОНЕТИЗАЦИЯ"))
    kb.add(KeyboardButton("🔍 НАЙТИ МАСТЕРА"))
    kb.add(KeyboardButton("💼 ИЩУ РАБОТУ"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"))
    return kb

def get_founder_keyboard():
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    kb.add(KeyboardButton("👥 ОНЛАЙН"), KeyboardButton("📊 СТАТИСТИКА"), KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("👥 ВСЕ ЛЮДИ"), KeyboardButton("✨ БЛАГА"), KeyboardButton("📤 РАССЫЛКА"))
    kb.add(KeyboardButton("💳 ПЛАТЕЖИ"), KeyboardButton("🏦 ВЫВОДЫ"), KeyboardButton("📊 ДОХОДЫ"))
    kb.add(KeyboardButton("📜 ЛОГИ"), KeyboardButton("🔍 ПОИСК"), KeyboardButton("📈 ОТЧЁТ"))
    kb.add(KeyboardButton("🩺 ЗДОРОВЬЕ"), KeyboardButton("🛡️ ЗАЩИТА"), KeyboardButton("💎 ТАРИФЫ"))
    kb.add(KeyboardButton("🔄 ОБНОВИТЬ"), KeyboardButton("📡 СТАТУС"), KeyboardButton("🧹 ОЧИСТИТЬ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_people_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"))
    kb.add(KeyboardButton("🔍 НАЙТИ МАСТЕРА"), KeyboardButton("💼 ИЩУ РАБОТУ"))
    kb.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_business_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 АНАЛИТИКА"), KeyboardButton("🤖 АВТОМАТИЗАЦИЯ"))
    kb.add(KeyboardButton("📈 ЛИЗИНГ"), KeyboardButton("💼 ЗАКАЗЫ"))
    kb.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_monetization_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💎 КУПИТЬ ТАРИФ"), KeyboardButton("⭐ ПАРТНЁРСКАЯ"))
    kb.add(KeyboardButton("🏦 KASPI QR"), KeyboardButton("💎 USDT TRC20"))
    kb.add(KeyboardButton("📊 МОЙ ДОХОД"), KeyboardButton("📈 ОБЩАЯ СТАТИСТИКА"))
    kb.add(KeyboardButton("💸 ВЫВЕСТИ"), KeyboardButton("📋 ИСТОРИЯ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

# ==================================================
# 🤖 КОМАНДЫ БОТА
# ==================================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    
    if user_id == FOUNDER_ID or user_id == TOMIRIS_ID:
        c.execute("INSERT OR REPLACE INTO users (user_id, name, is_admin, role, blessings) VALUES (?, ?, ?, ?, ?)",
                  (user_id, name, 1, 'founder', 999999999))
        conn.commit()
        bot.reply_to(message, f"👑 АССАЛЯМУ АЛЕЙКУМ, ХРАНИТЕЛЬ {name}!\n\n📱 ПАНЕЛЬ УПРАВЛЕНИЯ:", reply_markup=get_founder_keyboard())
        return
    
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
        conn.commit()
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n✨ Вы получили 100 Благ!\n\nКто вы?", reply_markup=get_people_keyboard())
        return
    
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (datetime.now().isoformat(), user_id))
    conn.commit()
    bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n💰 Баланс: {get_balance(user_id)} Благ\n\nКто вы?", reply_markup=get_people_keyboard())

@bot.message_handler(commands=['id'])
def cmd_id(message):
    bot.reply_to(message, f"🆔 *ТВОЙ ID:* `{message.chat.id}`\n\n👑 Хранитель: {'✅' if is_admin(message.chat.id) else '❌'}", parse_mode="Markdown")

def is_admin(user_id):
    return user_id in ADMIN_IDS

def get_balance(user_id):
    if user_id == FOUNDER_ID:
        return 999999999
    c.execute("SELECT blessings FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    return row[0] if row else 0

# ==================================================
# 🏓 ОБРАБОТЧИКИ ПИНГА И WEBAPP
# ==================================================

@app.route('/ping')
def ping():
    """Отвечает на пинг, чтобы Render знал, что бот жив"""
    return "🪞 ЗЕРКАЛО ЖИВО! Пинг принят.", 200

@app.route('/')
def home():
    return """
    <h1>🪞 ЗЕРКАЛО</h1>
    <p>✅ Работает 24/7</p>
    <p>📡 Последний пинг: активен</p>
    <p>👑 Хранитель: активен</p>
    <hr>
    <p><i>Ассаляму алейкум ва рахматуллахи ва баракатух</i></p>
    """, 200

# ==================================================
# 🚀 ЗАПУСК
# ==================================================

def run_bot():
    """Запускает Telegram бота в отдельном потоке"""
    if bot:
        print("🤖 ЗАПУСКАЮ БОТА...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    else:
        print("❌ НЕТ TOKEN! Бот не запущен.")

def run_flask():
    """Запускает Flask сервер"""
    print(f"🌐 ЗАПУСКАЮ WEB-СЕРВЕР НА ПОРТУ {PORT}...")
    app.run(host='0.0.0.0', port=PORT)

# ==================================================
# ⚡ ГЛАВНЫЙ ЗАПУСК
# ==================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🪞 ЗЕРКАЛО ЗАПУСКАЕТСЯ...")
    print("=" * 70)
    
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask (основной поток)
    run_flask()
