#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🪞 ЗЕРКАЛО — ПОЛНАЯ СИСТЕМА
═══════════════════════════════════════════════════════════════════
✅ РАБОТАЕТ 24/7
✅ ПИНГ КАЖДУЮ МИНУТУ
✅ ВСЕ МОДУЛИ
✅ WEBAPP ИНТЕРФЕЙС
✅ ДЕЛЕНИЕ ПО РОЛЯМ
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
# ⚡ УСТАНОВКА БИБЛИОТЕК
# ==================================================

def install_package(package):
    try:
        __import__(package)
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

REQUIRED_PACKAGES = ["pytelegrambotapi", "flask", "requests"]
for pkg in REQUIRED_PACKAGES:
    install_package(pkg)

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ==================================================
# 🔧 НАСТРОЙКИ
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "zerkalo.onrender.com")
PORT = int(os.environ.get("PORT", 8080))

# ID Хранителей
FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814
ADMIN_IDS = [5409420822, 5479179814]

# Реквизиты
KASPI_PHONE = "+777733440345"
KASPI_NAME = "ЗЕРКАЛО"
CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"

print("=" * 70)
print("🪞 ЗЕРКАЛО — ПОЛНАЯ СИСТЕМА")
print("=" * 70)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"👑 ОСНОВАТЕЛЬ: {FOUNDER_ID}")
print(f"🌐 ХОСТ: {RENDER_HOSTNAME}")
print("=" * 70)

# ==================================================
# 🤖 БОТ И APP
# ==================================================

bot = telebot.TeleBot(TOKEN) if TOKEN else None
app = Flask(__name__)

# ==================================================
# ⏰ БЕСКОНЕЧНЫЙ ПИНГ
# ==================================================

def ping_self():
    url = f"https://{RENDER_HOSTNAME}/ping"
    count = 0
    while True:
        try:
            r = requests.get(url, timeout=10)
            count += 1
            print(f"🔵 Пинг #{count} | {r.status_code}")
        except:
            pass
        time.sleep(60)

threading.Thread(target=ping_self, daemon=True).start()
print("✅ ПИНГ ЗАПУЩЕН!")

# ==================================================
# 📦 БАЗА ДАННЫХ
# ==================================================

conn = sqlite3.connect('zerkalo.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    role TEXT DEFAULT 'user',
    blessings INTEGER DEFAULT 100,
    is_admin INTEGER DEFAULT 0,
    last_seen TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    price INTEGER,
    status TEXT DEFAULT 'open',
    created_at TEXT
)''')

conn.commit()
print("✅ БАЗА ДАННЫХ ГОТОВА!")

# ==================================================
# 📱 КЛАВИАТУРЫ
# ==================================================

def get_main_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("👑 ХРАНИТЕЛЬ"), KeyboardButton("🏢 БИЗНЕС"))
    kb.add(KeyboardButton("👤 ЛЮДИ"), KeyboardButton("💰 МОНЕТИЗАЦИЯ"))
    kb.add(KeyboardButton("🔍 НАЙТИ МАСТЕРА"), KeyboardButton("💼 ИЩУ РАБОТУ"))
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

def is_admin(user_id):
    return user_id in ADMIN_IDS

def get_balance(user_id):
    if user_id == FOUNDER_ID:
        return 999999999
    c.execute("SELECT blessings FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    return row[0] if row else 0

# ==================================================
# 🤖 КОМАНДЫ БОТА
# ==================================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    
    if is_admin(user_id):
        c.execute("INSERT OR REPLACE INTO users (user_id, name, is_admin, role, blessings) VALUES (?, ?, ?, ?, ?)",
                  (user_id, name, 1, 'founder', 999999999))
        conn.commit()
        bot.reply_to(message, f"👑 АССАЛЯМУ АЛЕЙКУМ, ХРАНИТЕЛЬ {name}!\n\n📱 ПАНЕЛЬ УПРАВЛЕНИЯ:", reply_markup=get_founder_keyboard())
        return
    
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
        conn.commit()
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n✨ Вы получили 100 Благ!\n\n📱 Откройте приложение: [Открыть](https://{RENDER_HOSTNAME}/webapp)", reply_markup=get_people_keyboard(), parse_mode="Markdown")
        return
    
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (datetime.now().isoformat(), user_id))
    conn.commit()
    bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n💰 Баланс: {get_balance(user_id)} Благ\n\n📱 [Открыть приложение](https://{RENDER_HOSTNAME}/webapp)", reply_markup=get_people_keyboard(), parse_mode="Markdown")

@bot.message_handler(commands=['id'])
def cmd_id(message):
    bot.reply_to(message, f"🆔 *ТВОЙ ID:* `{message.chat.id}`\n\n👑 Хранитель: {'✅' if is_admin(message.chat.id) else '❌'}", parse_mode="Markdown")

@bot.message_handler(commands=['web'])
def cmd_web(message):
    bot.reply_to(message, f"📱 *ОТКРОЙ ПРИЛОЖЕНИЕ:*\n[Нажми сюда](https://{RENDER_HOSTNAME}/webapp)", parse_mode="Markdown")

# ==================================================
# 🌐 WEBAPP МАРШРУТЫ
# ==================================================

@app.route('/webapp')
def webapp():
    return send_from_directory('webapp', 'index.html')

@app.route('/webapp/<path:filename>')
def webapp_files(filename):
    return send_from_directory('webapp', filename)

@app.route('/api/user/<int:user_id>')
def api_user(user_id):
    c.execute("SELECT user_id, name, role, blessings FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    if user:
        return jsonify({"id": user[0], "name": user[1], "role": user[2], "blessings": user[3]})
    return jsonify({"error": "User not found"}), 404

@app.route('/api/orders')
def api_orders():
    c.execute("SELECT id, title, price, status FROM orders WHERE status='open' LIMIT 20")
    orders = c.fetchall()
    return jsonify([{"id": o[0], "title": o[1], "price": o[2], "status": o[3]} for o in orders])

@app.route('/ping')
def ping():
    return "🪞 ЗЕРКАЛО ЖИВО!", 200

@app.route('/')
def home():
    return """
    <h1>🪞 ЗЕРКАЛО</h1>
    <p>✅ Работает 24/7</p>
    <p>📡 Пинг активен</p>
    <p>👑 Хранитель: активен</p>
    <hr>
    <p><a href="/webapp">📱 Открыть приложение</a></p>
    <p><i>Ассаляму алейкум ва рахматуллахи ва баракатух</i></p>
    """, 200

# ==================================================
# 🚀 ЗАПУСК
# ==================================================

def run_bot():
    if bot:
        print("🤖 ЗАПУСКАЮ БОТА...")
        bot.infinity_polling(timeout=10)
    else:
        print("❌ НЕТ TOKEN!")

def run_flask():
    print(f"🌐 ЗАПУСКАЮ WEB-СЕРВЕР НА ПОРТУ {PORT}...")
    app.run(host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    print("=" * 70)
    print("🪞 ЗЕРКАЛО ЗАПУСКАЕТСЯ...")
    print("=" * 70)
    
    threading.Thread(target=run_bot, daemon=True).start()
    run_flask()
