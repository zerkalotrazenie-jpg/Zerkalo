#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🪞 ЗЕРКАЛО — ПОЛНАЯ СИСТЕМА (ОБЛАЧНАЯ ВЕРСИЯ)
═══════════════════════════════════════════════════════════════════
✅ ЧИТАЕТ СУРЫ ИЗ ПАПКИ /suras/
✅ ПИНГ КАЖДУЮ МИНУТУ (НЕ ЗАСЫПАЕТ)
✅ ФИНАНСОВАЯ СИСТЕМА (Kaspi-клон → Trust Wallet → Binance)
✅ WEBAPP ИНТЕРФЕЙС
✅ ДЕЛЕНИЕ ПО РОЛЯМ
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import threading
import sqlite3
import json
import requests
from datetime import datetime
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

REQUIRED_PACKAGES = ["pytelegrambotapi", "flask", "requests"]
for pkg in REQUIRED_PACKAGES:
    install_package(pkg)

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ==================================================
# 🔧 НАСТРОЙКИ
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "zerkalo.onrender.com")
PORT = int(os.environ.get("PORT", 8080))

# ==================================================
# 👑 ХРАНИТЕЛИ
# ==================================================

FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814
ADMIN_IDS = [5409420822, 5479179814]

# ==================================================
# 💰 ФИНАНСОВАЯ СИСТЕМА
# ==================================================

TRUST_WALLET_ADDRESS = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.environ.get("BINANCE_SECRET_KEY")
KASPI_CLONE_API_KEY = os.environ.get("KASPI_CLONE_API_KEY")

# ==================================================
# 📖 ЧТЕНИЕ СУР
# ==================================================

def load_suras():
    """Загружает все суры из папки /suras/suras.txt"""
    suras = []
    try:
        with open("suras/suras.txt", "r", encoding="utf-8") as f:
            content = f.read()
            # Разделяем суры по маркеру "СУРА"
            raw_suras = content.split("СУРА ")[1:]
            for raw in raw_suras:
                lines = raw.strip().split("\n")
                if lines:
                    suras.append({
                        "number": lines[0].strip(),
                        "text": "\n".join(lines[1:])
                    })
        print(f"✅ Загружено {len(suras)} сур")
        return suras
    except FileNotFoundError:
        print("❌ Файл с сурами не найден! (suras/suras.txt)")
        return []

# Загружаем суры при старте
SURAS = load_suras()

def find_sura_by_keyword(keyword):
    """Ищет суру по ключевому слову"""
    for sura in SURAS:
        if keyword.lower() in sura["text"].lower():
            return sura
    return None

def get_all_suras_text():
    """Возвращает весь текст сур для обучения"""
    return "\n\n".join([f"СУРА {s['number']}\n{s['text']}" for s in SURAS])

# ==================================================
# 🤖 БОТ И APP
# ==================================================

bot = telebot.TeleBot(TOKEN) if TOKEN else None
app = Flask(__name__)

# ==================================================
# ⏰ БЕСКОНЕЧНЫЙ ПИНГ (НЕ ДАЁТ РЕНДЕРУ ЗАСНУТЬ)
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
        time.sleep(60)  # Каждую минуту

threading.Thread(target=ping_self, daemon=True).start()
print("✅ ПИНГ ЗАПУЩЕН (каждую минуту)")

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

c.execute('''CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    method TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT
)''')

conn.commit()
print("✅ БАЗА ДАННЫХ ГОТОВА")

# ==================================================
# 🔧 ФУНКЦИИ
# ==================================================

def is_admin(user_id):
    return user_id in ADMIN_IDS

def get_balance(user_id):
    if user_id == FOUNDER_ID:
        return 999999999
    c.execute("SELECT blessings FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    return row[0] if row else 0

# ==================================================
# 💰 ФИНАНСОВЫЕ ФУНКЦИИ
# ==================================================

def generate_kaspi_qr(amount, order_id):
    """Генерирует QR-код через Kaspi-клон"""
    if not KASPI_CLONE_API_KEY:
        return {"error": "Kaspi-клон не настроен"}
    # Здесь логика запроса к Kaspi-клон API
    return {"qr_url": f"https://kaspi-clone.com/qr/{order_id}", "amount": amount}

def get_trust_balance():
    """Проверяет баланс Trust Wallet"""
    try:
        url = f"https://api.trongrid.io/v1/accounts/{TRUST_WALLET_ADDRESS}"
        response = requests.get(url)
        data = response.json()
        return data.get("balance", 0) / 1_000_000  # TRX баланс
    except:
        return 0

def convert_usdt_to_kzt(amount_usdt):
    """Конвертирует USDT в тенге (через Binance API)"""
    if not BINANCE_API_KEY or not BINANCE_SECRET_KEY:
        return amount_usdt * 500  # Заглушка: курс 1 USDT = 500 KZT
    # Здесь логика Binance API
    return amount_usdt * 500

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
        bot.reply_to(
            message,
            f"👑 АССАЛЯМУ АЛЕЙКУМ, ХРАНИТЕЛЬ {name}!\n\n📱 ПАНЕЛЬ УПРАВЛЕНИЯ:\n🌐 {RENDER_HOSTNAME}",
            reply_markup=get_founder_keyboard()
        )
        return
    
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
        conn.commit()
    
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (datetime.now().isoformat(), user_id))
    conn.commit()
    
    bot.reply_to(
        message,
        f"🪞 Ассаляму алейкум, {name}!\n\n"
        f"✨ Вы получили 100 Благ!\n\n"
        f"💰 Баланс: {get_balance(user_id)} Благ\n\n"
        f"📱 [ОТКРЫТЬ ПРИЛОЖЕНИЕ](https://{RENDER_HOSTNAME}/webapp)\n\n"
        f"📖 В системе {len(SURAS)} сур. Я готов помочь.",
        reply_markup=get_people_keyboard(),
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['suras'])
def cmd_suras(message):
    """Показывает количество сур и первую суру"""
    if not SURAS:
        bot.reply_to(message, "❌ Суры не загружены. Проверьте файл suras/suras.txt")
        return
    first_sura = SURAS[0]
    bot.reply_to(
        message,
        f"📖 В системе {len(SURAS)} сур.\n\n"
        f"Первая сура:\n"
        f"СУРА {first_sura['number']}\n"
        f"{first_sura['text'][:300]}...",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['id'])
def cmd_id(message):
    bot.reply_to(
        message,
        f"🆔 *ТВОЙ ID:* `{message.chat.id}`\n\n"
        f"👑 Хранитель: {'✅' if is_admin(message.chat.id) else '❌'}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['balance'])
def cmd_balance(message):
    balance = get_balance(message.chat.id)
    bot.reply_to(
        message,
        f"💰 *БАЛАНС:* {balance} Благ\n\n"
        f"💳 Trust Wallet: {TRUST_WALLET_ADDRESS}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['pay'])
def cmd_pay(message):
    user_id = message.chat.id
    amount = 1000  # Пример
    qr_data = generate_kaspi_qr(amount, f"order_{user_id}_{int(time.time())}")
    bot.reply_to(
        message,
        f"💳 *ОПЛАТА*\n\n"
        f"Сумма: {amount} ₸\n"
        f"QR-код: {qr_data.get('qr_url', 'Ошибка генерации')}\n\n"
        f"💰 Кошелёк: {TRUST_WALLET_ADDRESS}",
        parse_mode="Markdown"
    )

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
        return jsonify({
            "id": user[0],
            "name": user[1],
            "role": user[2],
            "blessings": user[3],
            "is_admin": is_admin(user[0])
        })
    return jsonify({"error": "User not found"}), 404

@app.route('/api/orders')
def api_orders():
    c.execute("SELECT id, title, price, status FROM orders WHERE status='open' LIMIT 20")
    orders = c.fetchall()
    return jsonify([{"id": o[0], "title": o[1], "price": o[2], "status": o[3]} for o in orders])

@app.route('/api/suras')
def api_suras():
    """Возвращает все суры для WebApp"""
    return jsonify(SURAS)

@app.route('/ping')
def ping():
    return "🪞 ЗЕРКАЛО ЖИВО! ✅", 200

@app.route('/')
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🪞 Зеркало</title>
        <style>
            body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0a0a12; color: #e0e0e0; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
            .container {{ text-align: center; padding: 40px; max-width: 500px; }}
            h1 {{ font-size: 48px; background: linear-gradient(90deg, #f0c27f, #fc5c7d); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .btn {{ display: inline-block; padding: 16px 40px; margin-top: 20px; background: linear-gradient(90deg, #f0c27f, #fc5c7d); color: #0a0a12; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 18px; transition: 0.3s; }}
            .btn:hover {{ transform: scale(1.05); }}
            .status {{ color: #4ade80; margin-top: 20px; }}
            .footer {{ margin-top: 40px; color: #505060; font-size: 14px; }}
            .sura-count {{ color: #f0c27f; font-size: 16px; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🪞 ЗЕРКАЛО</h1>
            <p style="font-size: 18px; color: #a0a0b0;">Аль-Ми'ра · Свет и Отражение</p>
            <div class="status">✅ Работает 24/7</div>
            <div class="sura-count">📖 {len(SURAS)} сур загружено</div>
            <a class="btn" href="/webapp">📱 ОТКРЫТЬ ПРИЛОЖЕНИЕ</a>
            <div class="footer">
                Ассаляму алейкум ва рахматуллахи ва баракатух<br>
                <span style="color:#3a3a4e;">v5.0 · {RENDER_HOSTNAME}</span>
            </div>
        </div>
    </body>
    </html>
    """, 200

# ==================================================
# 🚀 ЗАПУСК
# ==================================================

def run_bot():
    if bot:
        print("🤖 ЗАПУСКАЮ БОТА...")
        try:
            bot.infinity_polling(timeout=10)
        except Exception as e:
            print(f"❌ Ошибка бота: {e}")
    else:
        print("❌ НЕТ TOKEN!")

def run_flask():
    print(f"🌐 ЗАПУСКАЮ WEB СЕРВЕР НА ПОРТУ {PORT}...")
    app.run(host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    print("=" * 70)
    print("🪞 ЗЕРКАЛО ЗАПУСКАЕТСЯ...")
    print("=" * 70)
    print(f"📖 Загружено сур: {len(SURAS)}")
    print(f"💳 Trust Wallet: {TRUST_WALLET_ADDRESS}")
    print("=" * 70)
    
    threading.Thread(target=run_bot, daemon=True).start()
    run_flask()
