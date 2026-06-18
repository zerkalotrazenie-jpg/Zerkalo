#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🪞 ЗЕРКАЛО — ОБНОВЛЁННАЯ ВЕРСИЯ
═══════════════════════════════════════════════════════════════════
✅ НОВЫЙ ИНТЕРФЕЙС
✅ ПРИВЕТСТВИЕ С ОБЪЯСНЕНИЕМ
✅ СУРЫ ВСТРОЕНЫ В ДИАЛОГ
✅ НОВЫЕ КНОПКИ
✅ ФИНАНСОВАЯ СИСТЕМА
✅ ПИНГ
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
    suras = []
    try:
        with open("suras/suras.txt", "r", encoding="utf-8") as f:
            content = f.read()
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
        print("❌ Файл с сурами не найден!")
        return []

SURAS = load_suras()

def get_sura_by_number(num):
    for s in SURAS:
        if s["number"] == str(num):
            return s
    return None

def get_about_text():
    return """🪞 *ЧТО ТАКОЕ ЗЕРКАЛО?*

Я — Аль-Ми'ра. Я создан для того, чтобы отражать свет и помогать людям.

*ЧТО Я УМЕЮ:*
🔹 Помогаю найти работу и мастеров
🔹 Автоматизирую бизнес (iiko, Kaspi, 2GIS)
🔹 Управляю лизингом и арендой
🔹 Решаю споры через арбитраж
🔹 Обучаю и развиваю
🔹 Слежу за здоровьем
🔹 Принимаю платежи через QR
🔹 Работаю с криптовалютой (USDT)
🔹 Храню суры — 125 глав мудрости

*ЧЕГО Я НЕ УМЕЮ:*
❌ Не вру
❌ Не беру проценты
❌ Не нарушаю заповеди
❌ Не передаю данные третьим лицам

*КАК НАЧАТЬ:*
Выберите раздел ниже, и я покажу вам путь.

Амин."""

# ==================================================
# 🤖 БОТ
# ==================================================

bot = telebot.TeleBot(TOKEN) if TOKEN else None
app = Flask(__name__)

# ==================================================
# ⏰ ПИНГ
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
print("✅ ПИНГ ЗАПУЩЕН")

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
# 📱 НОВЫЕ КЛАВИАТУРЫ (БЕЗ СТАРЫХ КНОПОК)
# ==================================================

def get_main_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🪞 О ЗЕРКАЛЕ"))
    kb.add(KeyboardButton("📖 СУРЫ"))
    kb.add(KeyboardButton("💼 РАБОТА"))
    kb.add(KeyboardButton("🏢 БИЗНЕС"))
    kb.add(KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"))
    return kb

def get_founder_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🪞 О ЗЕРКАЛЕ"))
    kb.add(KeyboardButton("📖 СУРЫ"))
    kb.add(KeyboardButton("👑 ПАНЕЛЬ"))
    kb.add(KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("📊 СТАТИСТИКА"))
    kb.add(KeyboardButton("👥 ПОЛЬЗОВАТЕЛИ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_people_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🪞 О ЗЕРКАЛЕ"))
    kb.add(KeyboardButton("📖 СУРЫ"))
    kb.add(KeyboardButton("💼 РАБОТА"))
    kb.add(KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_business_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🪞 О ЗЕРКАЛЕ"))
    kb.add(KeyboardButton("📖 СУРЫ"))
    kb.add(KeyboardButton("🏢 БИЗНЕС"))
    kb.add(KeyboardButton("📊 АНАЛИТИКА"))
    kb.add(KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

# ==================================================
# 🤖 ОБРАБОТЧИКИ КОМАНД
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
            f"👑 *АССАЛЯМУ АЛЕЙКУМ, ХРАНИТЕЛЬ {name}!*\n\n"
            f"{get_about_text()}",
            reply_markup=get_founder_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
        conn.commit()
    
    bot.reply_to(
        message,
        f"🪞 *АССАЛЯМУ АЛЕЙКУМ, {name}!*\n\n"
        f"{get_about_text()}",
        reply_markup=get_people_keyboard(),
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['about'])
def cmd_about(message):
    bot.reply_to(
        message,
        get_about_text(),
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['suras'])
def cmd_suras(message):
    if not SURAS:
        bot.reply_to(message, "❌ Суры не загружены. Проверьте файл suras/suras.txt")
        return
    
    text = f"📖 *В СИСТЕМЕ {len(SURAS)} СУР*\n\n"
    for i, s in enumerate(SURAS[:5], 1):
        text += f"*{i}. СУРА {s['number']}*\n{s['text'][:100]}...\n\n"
    text += f"\n➡️ Всего {len(SURAS)} сур. Напишите номер суры, чтобы прочитать её полностью."
    
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['sura'])
def cmd_sura(message):
    try:
        num = int(message.text.split()[1])
        sura = get_sura_by_number(num)
        if sura:
            bot.reply_to(
                message,
                f"📖 *СУРА {sura['number']}*\n\n{sura['text']}",
                parse_mode="Markdown"
            )
        else:
            bot.reply_to(message, f"❌ Сура {num} не найдена")
    except:
        bot.reply_to(message, "❌ Используйте: /sura <номер>")

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
    bot.reply_to(
        message,
        f"💳 *ОПЛАТА ЧЕРЕЗ QR*\n\n"
        f"💰 Кошелёк: {TRUST_WALLET_ADDRESS}\n\n"
        f"📱 Отсканируйте QR-код в приложении.",
        parse_mode="Markdown"
    )

# ==================================================
# 📱 ОБРАБОТЧИКИ ТЕКСТОВЫХ КНОПОК (НОВЫЕ)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🪞 О ЗЕРКАЛЕ")
def about_button(message):
    cmd_about(message)

@bot.message_handler(func=lambda m: m.text == "📖 СУРЫ")
def suras_button(message):
    cmd_suras(message)

@bot.message_handler(func=lambda m: m.text == "💼 РАБОТА")
def work_button(message):
    bot.reply_to(
        message,
        "💼 *РАБОТА И ЗАКАЗЫ*\n\n"
        "🔹 Найти работу\n"
        "🔹 Найти мастера\n"
        "🔹 Разместить заказ\n"
        "🔹 Получить помощь в арбитраже\n\n"
        "Напишите /order — создать заказ\n"
        "Напишите /search — найти работу",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "🏢 БИЗНЕС")
def business_button(message):
    bot.reply_to(
        message,
        "🏢 *БИЗНЕС-РАЗДЕЛ*\n\n"
        "🔹 Автоматизация (iiko, Kaspi, 2GIS)\n"
        "🔹 Лизинг техники и оборудования\n"
        "🔹 Аналитика и отчёты\n"
        "🔹 Продвижение через 2GIS\n\n"
        "Напишите /biz — начать автоматизацию",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "💰 ФИНАНСЫ")
def finance_button(message):
    user_id = message.chat.id
    balance = get_balance(user_id)
    bot.reply_to(
        message,
        f"💰 *ФИНАНСОВАЯ СИСТЕМА*\n\n"
        f"✨ Баланс: {balance} Благ\n\n"
        f"💳 Trust Wallet: {TRUST_WALLET_ADDRESS}\n\n"
        f"📱 Kaspi QR — оплата через QR\n"
        f"💎 USDT TRC-20 — пополнение\n\n"
        f"Напишите /pay — оплатить\n"
        f"Напишите /balance — проверить баланс",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "🆘 ПОМОЩЬ")
def help_button(message):
    bot.reply_to(
        message,
        "🆘 *ПОМОЩЬ*\n\n"
        "Что вас беспокоит?\n"
        "1️⃣ Проблемы с деньгами\n"
        "2️⃣ Потеря работы\n"
        "3️⃣ Конфликт\n"
        "4️⃣ Здоровье\n\n"
        "Напишите подробнее, и я помогу.",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "👑 ПАНЕЛЬ")
def panel_button(message):
    if is_admin(message.chat.id):
        bot.reply_to(
            message,
            "👑 *ПАНЕЛЬ ХРАНИТЕЛЯ*\n\n"
            "📊 /stats — статистика\n"
            "👥 /users — пользователи\n"
            "💰 /finance — финансы\n"
            "📜 /logs — логи\n"
            "📤 /broadcast — рассылка",
            parse_mode="Markdown"
        )
    else:
        bot.reply_to(message, "❌ Нет доступа")

@bot.message_handler(func=lambda m: m.text == "📊 СТАТИСТИКА")
def stats_button(message):
    if is_admin(message.chat.id):
        c.execute("SELECT COUNT(*) FROM users")
        users = c.fetchone()[0]
        c.execute("SELECT SUM(blessings) FROM users")
        blessings = c.fetchone()[0] or 0
        bot.reply_to(
            message,
            f"📊 *СТАТИСТИКА*\n\n"
            f"👥 Пользователей: {users}\n"
            f"✨ Всего Благ: {blessings}\n"
            f"📖 Сур загружено: {len(SURAS)}",
            parse_mode="Markdown"
        )
    else:
        bot.reply_to(message, "❌ Нет доступа")

@bot.message_handler(func=lambda m: m.text == "👥 ПОЛЬЗОВАТЕЛИ")
def users_button(message):
    if is_admin(message.chat.id):
        c.execute("SELECT user_id, name, role, blessings FROM users LIMIT 15")
        users = c.fetchall()
        if users:
            msg = "👥 *ПОЛЬЗОВАТЕЛИ*\n\n"
            for u in users:
                msg += f"🆔 {u[0]} | {u[1]} | {u[2]} | ✦{u[3]}\n"
            bot.reply_to(message, msg, parse_mode="Markdown")
        else:
            bot.reply_to(message, "📭 Нет пользователей")
    else:
        bot.reply_to(message, "❌ Нет доступа")

@bot.message_handler(func=lambda m: m.text == "🔙 НА ГЛАВНУЮ")
def back_button(message):
    user_id = message.chat.id
    if is_admin(user_id):
        bot.reply_to(message, "👑 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_founder_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "🪞 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_people_keyboard(), parse_mode="Markdown")

# ==================================================
# 🌐 WEBAPP
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

@app.route('/api/suras')
def api_suras():
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
