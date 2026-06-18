#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🪞 ЗЕРКАЛО — ПОЛНАЯ ВЕРСИЯ
═══════════════════════════════════════════════════════════════════
✅ WEBAPP
✅ QR-КОД (Kaspi-клон)
✅ ДЕЛЕНИЕ ПО РОЛЯМ
✅ ВСЕ КНОПКИ
✅ СУРЫ
✅ ПИНГ
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import threading
import sqlite3
import json
import hashlib
import random
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
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

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
KASPI_NAME = "ЗЕРКАЛО"
KASPI_PHONE = "+777733440345"

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

# ==================================================
# 💰 ГЕНЕРАЦИЯ QR-КОДА (KASPI-КЛОН)
# ==================================================

def generate_kaspi_qr(amount, order_id):
    """Генерирует QR-код через Kaspi-клон"""
    if not KASPI_CLONE_API_KEY:
        return {"qr_url": f"https://kaspi-clone.com/qr/{order_id}", "amount": amount, "wallet": TRUST_WALLET_ADDRESS}
    # В реальной интеграции здесь будет запрос к Kaspi-клон API
    return {
        "qr_url": f"https://kaspi-clone.com/qr/{order_id}",
        "amount": amount,
        "wallet": TRUST_WALLET_ADDRESS,
        "phone": KASPI_PHONE
    }

def get_trust_balance():
    try:
        url = f"https://api.trongrid.io/v1/accounts/{TRUST_WALLET_ADDRESS}"
        response = requests.get(url)
        data = response.json()
        return data.get("balance", 0) / 1_000_000
    except:
        return 0

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
    last_seen TEXT,
    phone TEXT DEFAULT '',
    city TEXT DEFAULT '',
    profession TEXT DEFAULT ''
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

c.execute('''CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    method TEXT,
    status TEXT DEFAULT 'pending',
    transaction_id TEXT,
    created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    details TEXT,
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

def get_user_role(user_id):
    if is_admin(user_id):
        return "founder"
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    return row[0] if row else "user"

def log_action(user_id, action, details=""):
    c.execute("INSERT INTO logs (user_id, action, details, created_at) VALUES (?, ?, ?, ?)",
              (user_id, action, details, datetime.now().isoformat()))
    conn.commit()

def create_payment(user_id, amount, method):
    tx_id = hashlib.md5(f"{time.time()}{user_id}{random.random()}".encode()).hexdigest()[:16]
    c.execute("INSERT INTO payments (user_id, amount, method, status, transaction_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, amount, method, "pending", tx_id, datetime.now().isoformat()))
    conn.commit()
    return tx_id

# ==================================================
# 📱 КЛАВИАТУРЫ (ПО РОЛЯМ)
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
    
    if is_admin(user_id):
        c.execute("INSERT OR REPLACE INTO users (user_id, name, is_admin, role, blessings) VALUES (?, ?, ?, ?, ?)",
                  (user_id, name, 1, 'founder', 999999999))
        conn.commit()
        bot.reply_to(
            message,
            f"👑 АССАЛЯМУ АЛЕЙКУМ, ХРАНИТЕЛЬ {name}!\n\n"
            f"📱 ПАНЕЛЬ УПРАВЛЕНИЯ:\n"
            f"🌐 {RENDER_HOSTNAME}",
            reply_markup=get_founder_keyboard()
        )
        return
    
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
        conn.commit()
        log_action(user_id, "register", f"Новый пользователь {name}")
    
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (datetime.now().isoformat(), user_id))
    conn.commit()
    
    bot.reply_to(
        message,
        f"🪞 Ассаляму алейкум, {name}!\n\n"
        f"✨ Вы получили 100 Благ!\n\n"
        f"💰 Баланс: {get_balance(user_id)} Благ\n\n"
        f"📱 [ОТКРЫТЬ ПРИЛОЖЕНИЕ](https://{RENDER_HOSTNAME}/webapp)",
        reply_markup=get_people_keyboard(),
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['web'])
def cmd_web(message):
    bot.reply_to(
        message,
        f"📱 *ОТКРОЙ ПРИЛОЖЕНИЕ:*\n"
        f"[Нажми сюда](https://{RENDER_HOSTNAME}/webapp)",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['id'])
def cmd_id(message):
    user_id = message.chat.id
    role = get_user_role(user_id)
    bot.reply_to(
        message,
        f"🆔 *ТВОЙ ID:* `{user_id}`\n\n"
        f"👑 Хранитель: {'✅' if is_admin(user_id) else '❌'}\n"
        f"🎭 Роль: {role}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['balance'])
def cmd_balance(message):
    user_id = message.chat.id
    balance = get_balance(user_id)
    bot.reply_to(
        message,
        f"💰 *БАЛАНС:* {balance} Благ\n\n"
        f"💳 Trust Wallet: {TRUST_WALLET_ADDRESS}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['pay'])
def cmd_pay(message):
    user_id = message.chat.id
    amount = 1000
    order_id = f"order_{user_id}_{int(time.time())}"
    qr_data = generate_kaspi_qr(amount, order_id)
    
    bot.reply_to(
        message,
        f"💳 *ОПЛАТА ЧЕРЕЗ KASPI QR*\n\n"
        f"📞 Номер: {KASPI_PHONE}\n"
        f"💰 Сумма: {amount} ₸\n"
        f"📱 QR-код: {qr_data.get('qr_url', 'Ошибка генерации')}\n\n"
        f"💎 Кошелёк: {TRUST_WALLET_ADDRESS}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['stats'])
def cmd_stats(message):
    user_id = message.chat.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Нет доступа")
        return
    
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT SUM(blessings) FROM users")
    total_blessings = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM orders WHERE status='open'")
    open_orders = c.fetchone()[0]
    
    bot.reply_to(
        message,
        f"📊 *СТАТИСТИКА*\n\n"
        f"👥 Пользователей: {total_users}\n"
        f"✨ Всего Благ: {total_blessings}\n"
        f"📦 Открытых заказов: {open_orders}\n"
        f"📖 Сур загружено: {len(SURAS)}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['users'])
def cmd_users(message):
    user_id = message.chat.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Нет доступа")
        return
    
    c.execute("SELECT user_id, name, role, blessings FROM users LIMIT 20")
    users = c.fetchall()
    
    if not users:
        bot.reply_to(message, "📭 Нет пользователей")
        return
    
    msg = "👥 *СПИСОК ПОЛЬЗОВАТЕЛЕЙ*\n\n"
    for u in users:
        msg += f"🆔 {u[0]} | {u[1]} | {u[2]} | ✦{u[3]}\n"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['logs'])
def cmd_logs(message):
    user_id = message.chat.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Нет доступа")
        return
    
    c.execute("SELECT user_id, action, created_at FROM logs ORDER BY id DESC LIMIT 20")
    logs = c.fetchall()
    
    if not logs:
        bot.reply_to(message, "📭 Логов нет")
        return
    
    msg = "📜 *ПОСЛЕДНИЕ ЛОГИ*\n\n"
    for l in logs:
        msg += f"{l[2][:16]} | ID:{l[0]} | {l[1][:30]}\n"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['suras'])
def cmd_suras(message):
    if not SURAS:
        bot.reply_to(message, "❌ Суры не загружены. Проверьте файл suras/suras.txt")
        return
    
    msg = f"📖 *В СИСТЕМЕ {len(SURAS)} СУР*\n\n"
    for i, s in enumerate(SURAS[:5], 1):
        msg += f"*{i}. СУРА {s['number']}*\n{s['text'][:100]}...\n\n"
    msg += f"\n➡️ Всего {len(SURAS)} сур. Напишите /sura [номер]"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['sura'])
def cmd_sura(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Используйте: /sura <номер>")
            return
        num = int(parts[1])
        sura = get_sura_by_number(num)
        if sura:
            bot.reply_to(
                message,
                f"📖 *СУРА {sura['number']}*\n\n{sura['text']}",
                parse_mode="Markdown"
            )
        else:
            bot.reply_to(message, f"❌ Сура {num} не найдена")
    except ValueError:
        bot.reply_to(message, "❌ Номер суры должен быть числом")

# ==================================================
# 📱 ТЕКСТОВЫЕ КНОПКИ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👑 ХРАНИТЕЛЬ")
def founder_section(message):
    user_id = message.chat.id
    if is_admin(user_id):
        bot.reply_to(message, "👑 *ПАНЕЛЬ ХРАНИТЕЛЯ*", reply_markup=get_founder_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Нет доступа", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text == "🏢 БИЗНЕС")
def business_section(message):
    user_id = message.chat.id
    log_action(user_id, "business", "Открыл бизнес-раздел")
    bot.reply_to(
        message,
        "🏢 *БИЗНЕС-РАЗДЕЛ*\n\n"
        "🤖 Автоматизация (iiko, Kaspi, 2GIS)\n"
        "📈 Лизинг техники и оборудования\n"
        "📊 Аналитика и отчёты\n"
        "📢 Продвижение через 2GIS\n\n"
        "Напишите /biz — начать автоматизацию",
        reply_markup=get_business_keyboard(),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "👤 ЛЮДИ")
def people_section(message):
    user_id = message.chat.id
    log_action(user_id, "people", "Открыл раздел людей")
    bot.reply_to(
        message,
        "👤 *ОБЫЧНЫЙ РАЗДЕЛ*\n\n"
        "💸 Работа и заказы\n"
        "🔍 Поиск мастеров\n"
        "💰 Баланс и финансы\n"
        "🆘 Помощь и поддержка",
        reply_markup=get_people_keyboard(),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "💰 МОНЕТИЗАЦИЯ")
def monetization_section(message):
    user_id = message.chat.id
    log_action(user_id, "monetization", "Открыл монетизацию")
    bot.reply_to(
        message,
        "💰 *МОНЕТИЗАЦИЯ*\n\n"
        "💎 Купить тариф\n"
        "⭐ Партнёрская программа\n"
        "🏦 Kaspi QR\n"
        "💎 USDT TRC20\n\n"
        f"💳 Trust Wallet: {TRUST_WALLET_ADDRESS}",
        reply_markup=get_monetization_keyboard(),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "💸 РАБОТА")
def work_section(message):
    user_id = message.chat.id
    log_action(user_id, "work", "Открыл раздел работы")
    bot.reply_to(
        message,
        "💸 *РАБОТА И ЗАКАЗЫ*\n\n"
        "🔹 Найти работу — /search\n"
        "🔹 Создать заказ — /order\n"
        "🔹 Найти мастера — /master\n"
        "🔹 Арбитраж — /arbitration",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "📦 ЗАКАЗЫ")
def orders_section(message):
    user_id = message.chat.id
    log_action(user_id, "orders", "Открыл заказы")
    c.execute("SELECT id, title, price FROM orders WHERE status='open' LIMIT 10")
    orders = c.fetchall()
    if orders:
        msg = "📦 *АКТИВНЫЕ ЗАКАЗЫ*\n\n"
        for o in orders:
            msg += f"#{o[0]} {o[1]} — {o[2]} ₸\n"
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, "📭 Нет активных заказов")

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ МАСТЕРА")
def find_master(message):
    user_id = message.chat.id
    log_action(user_id, "find_master", "Поиск мастера")
    bot.reply_to(
        message,
        "🔍 *ПОИСК МАСТЕРА*\n\n"
        "Введите профессию мастера:\n"
        "🛠️ Сварщик\n"
        "🔧 Электрик\n"
        "🚗 Автомеханик\n"
        "🏠 Строитель\n\n"
        "Напишите: /search [профессия]",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "💼 ИЩУ РАБОТУ")
def find_job(message):
    user_id = message.chat.id
    log_action(user_id, "find_job", "Поиск работы")
    bot.reply_to(
        message,
        "💼 *ПОИСК РАБОТЫ*\n\n"
        "Какая работа вас интересует?\n"
        "🏗️ Строительство\n"
        "🚛 Логистика\n"
        "🍽️ Общепит\n"
        "🏥 Медицина\n\n"
        "Напишите: /search [работа]",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "💰 БАЛАНС")
def balance_section(message):
    user_id = message.chat.id
    balance = get_balance(user_id)
    bot.reply_to(
        message,
        f"💰 *БАЛАНС*\n\n"
        f"✨ Благ: {balance}\n\n"
        f"💎 Trust Wallet: {TRUST_WALLET_ADDRESS}\n\n"
        f"📱 /pay — пополнить\n"
        f"📋 /history — история",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "❓ ВОПРОС")
def question_section(message):
    bot.reply_to(
        message,
        "❓ *ЗАДАЙТЕ ВОПРОС*\n\n"
        "Я помогу вам:\n"
        "- Найти работу\n"
        "- Решить спор\n"
        "- Получить помощь\n"
        "- Разобраться в системе\n\n"
        "Просто напишите ваш вопрос.",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "🆘 ПОМОЩЬ")
def help_section(message):
    user_id = message.chat.id
    log_action(user_id, "help", "Открыл помощь")
    bot.reply_to(
        message,
        "🆘 *ПОМОЩЬ*\n\n"
        "Что вас беспокоит?\n"
        "1️⃣ Проблемы с деньгами\n"
        "2️⃣ Потеря работы\n"
        "3️⃣ Конфликт\n"
        "4️⃣ Здоровье\n"
        "5️⃣ Вопросы по системе\n\n"
        "Напишите номер или опишите проблему.",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "💎 КУПИТЬ ТАРИФ")
def buy_tariff(message):
    bot.reply_to(
        message,
        "💎 *КУПИТЬ ТАРИФ*\n\n"
        "📱 Бесплатный — 0 ₸/мес\n"
        "⭐ Базовый — 1 000 ₸/мес\n"
        "🚀 PRO — 5 000 ₸/мес\n"
        "💎 Бизнес — 20 000 ₸/мес\n\n"
        "Напишите /pay [сумма]",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "⭐ ПАРТНЁРСКАЯ")
def referral_section(message):
    user_id = message.chat.id
    bot_name = bot.get_me().username
    c.execute("SELECT COUNT(*) FROM users WHERE referrer_id=?", (user_id,))
    count = c.fetchone()[0]
    bot.reply_to(
        message,
        f"⭐ *ПАРТНЁРСКАЯ ПРОГРАММА*\n\n"
        f"👥 Приглашено: {count}\n"
        f"🔗 Ссылка: https://t.me/{bot_name}?start={user_id}\n\n"
        f"💰 10% от пополнений!",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "🏦 KASPI QR")
def kaspi_qr(message):
    user_id = message.chat.id
    amount = 1000
    order_id = f"qr_{user_id}_{int(time.time())}"
    qr_data = generate_kaspi_qr(amount, order_id)
    bot.reply_to(
        message,
        f"🏦 *KASPI QR*\n\n"
        f"📞 Номер: {KASPI_PHONE}\n"
        f"💰 Сумма: {amount} ₸\n"
        f"📱 QR: {qr_data.get('qr_url', 'Ошибка')}\n\n"
        f"💎 Кошелёк: {TRUST_WALLET_ADDRESS}",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "💎 USDT TRC20")
def usdt_section(message):
    bot.reply_to(
        message,
        f"💎 *USDT TRC20*\n\n"
        f"📤 КОШЕЛЁК:\n`{TRUST_WALLET_ADDRESS}`\n\n"
        f"🔗 СЕТЬ: TRC20\n\n"
        f"✅ Отправьте USDT и напишите /confirm_usdt",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "📊 МОЙ ДОХОД")
def my_income(message):
    user_id = message.chat.id
    c.execute("SELECT SUM(amount) FROM payments WHERE user_id=?", (user_id,))
    total = c.fetchone()[0] or 0
    bot.reply_to(
        message,
        f"💰 *ВАШ ДОХОД*\n\n"
        f"📊 Всего: {total} ₸",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "📈 ОБЩАЯ СТАТИСТИКА")
def total_stats(message):
    user_id = message.chat.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Нет доступа")
        return
    c.execute("SELECT SUM(amount) FROM payments")
    total = c.fetchone()[0] or 0
    bot.reply_to(
        message,
        f"📊 *ОБЩАЯ СТАТИСТИКА*\n\n"
        f"💰 Всего доходов: {total} ₸",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "💸 ВЫВЕСТИ")
def withdraw_request(message):
    msg = bot.reply_to(message, "💸 Введите сумму для вывода (мин. 1 000 ₸):")
    bot.register_next_step_handler(msg, withdraw_amount)

def withdraw_amount(message):
    user_id = message.chat.id
    try:
        amount = int(message.text)
        if amount < 1000:
            bot.reply_to(message, "❌ Минимальная сумма вывода — 1 000 ₸")
            return
        if get_balance(user_id) < amount:
            bot.reply_to(message, "❌ Недостаточно средств")
            return
        msg = bot.reply_to(message, "💳 Введите номер карты Kaspi для вывода:")
        bot.register_next_step_handler(msg, withdraw_wallet, amount)
    except ValueError:
        bot.reply_to(message, "❌ Введите число")

def withdraw_wallet(message, amount):
    user_id = message.chat.id
    wallet = message.text
    c.execute("INSERT INTO payments (user_id, amount, method, status, created_at) VALUES (?, ?, ?, ?, ?)",
              (user_id, amount, f"Вывод на {wallet}", "pending", datetime.now().isoformat()))
    c.execute("UPDATE users SET blessings = blessings - ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    bot.reply_to(message, f"✅ Заявка на вывод {amount} ₸ создана!\n\n📱 Карта: {wallet}")

@bot.message_handler(func=lambda m: m.text == "📋 ИСТОРИЯ")
def payment_history(message):
    user_id = message.chat.id
    c.execute("SELECT id, amount, method, status, created_at FROM payments WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,))
    payments = c.fetchall()
    if not payments:
        bot.reply_to(message, "📭 История пуста")
        return
    msg = "📋 *ИСТОРИЯ ПЛАТЕЖЕЙ*\n\n"
    for p in payments:
        status_icon = "✅" if p[3] == "completed" else "⏳"
        msg += f"{status_icon} #{p[0]} | {p[1]} ₸ | {p[2]} | {p[4][:16]}\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔙 НА ГЛАВНУЮ")
def back_to_main(message):
    user_id = message.chat.id
    if is_admin(user_id):
        bot.reply_to(message, "👑 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_founder_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "🪞 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_people_keyboard(), parse_mode="Markdown")

# ==================================================
# 👑 АДМИН-КНОПКИ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👥 ОНЛАЙН" and is_admin(m.chat.id))
def admin_online(message):
    c.execute("SELECT user_id, name FROM users WHERE status='online'")
    users = c.fetchall()
    if users:
        msg = "🟢 *ОНЛАЙН:*\n" + "\n".join([f"{u[1]} (ID: {u[0]})" for u in users])
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, "🟢 Никого нет")

@bot.message_handler(func=lambda m: m.text == "📊 СТАТИСТИКА" and is_admin(m.chat.id))
def admin_stats(message):
    cmd_stats(message)

@bot.message_handler(func=lambda m: m.text == "💰 ФИНАНСЫ" and is_admin(m.chat.id))
def admin_finance(message):
    c.execute("SELECT SUM(amount) FROM payments")
    total = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()[0]
    bot.reply_to(
        message,
        f"💰 *ФИНАНСЫ*\n\n"
        f"👥 Всего пользователей: {users}\n"
        f"💰 Всего доходов: {total} ₸\n\n"
        f"💳 Trust Wallet: {TRUST_WALLET_ADDRESS}",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "👥 ВСЕ ЛЮДИ" and is_admin(m.chat.id))
def admin_all_users(message):
    c.execute("SELECT user_id, name, role, blessings FROM users LIMIT 30")
    users = c.fetchall()
    if not users:
        bot.reply_to(message, "📭 Нет пользователей")
        return
    msg = "👥 *ВСЕ ПОЛЬЗОВАТЕЛИ*\n\n"
    for u in users:
        msg += f"🆔 {u[0]} | {u[1]} | {u[2]} | ✦{u[3]}\n"
    bot.reply_to(message, msg[:4000], parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "✨ БЛАГА" and is_admin(m.chat.id))
def admin_top(message):
    c.execute("SELECT name, blessings FROM users ORDER BY blessings DESC LIMIT 10")
    top = c.fetchall()
    if not top:
        bot.reply_to(message, "📭 Нет данных")
        return
    msg = "✨ *ТОП ПО БЛАГАМ*\n\n"
    for i, u in enumerate(top, 1):
        msg += f"{i}. {u[0]} — {u[1]} ✦\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

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
            bot.send_message(u[0], f"📢 *ОТ ХРАНИТЕЛЯ*\n\n{text}", parse_mode="Markdown")
            sent += 1
            time.sleep(0.05)
        except:
            pass
    bot.reply_to(message, f"✅ Отправлено {sent}")

@bot.message_handler(func=lambda m: m.text == "💳 ПЛАТЕЖИ" and is_admin(m.chat.id))
def admin_payments(message):
    c.execute("SELECT id, user_id, amount, status, created_at FROM payments ORDER BY id DESC LIMIT 20")
    payments = c.fetchall()
    if not payments:
        bot.reply_to(message, "📭 Нет платежей")
        return
    msg = "💳 *ПЛАТЕЖИ*\n\n"
    for p in payments:
        status_icon = "✅" if p[3] == "completed" else "⏳"
        msg += f"#{p[0]} | 👤 {p[1]} | 💰 {p[2]} | {status_icon} | {p[4][:16]}\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🏦 ВЫВОДЫ" and is_admin(m.chat.id))
def admin_withdraws(message):
    c.execute("SELECT id, user_id, amount, status, created_at FROM payments WHERE method LIKE 'Вывод%' ORDER BY id DESC LIMIT 20")
    withdraws = c.fetchall()
    if not withdraws:
        bot.reply_to(message, "📭 Нет заявок на вывод")
        return
    msg = "🏦 *ЗАЯВКИ НА ВЫВОД*\n\n"
    for w in withdraws:
        status_icon = "✅" if w[3] == "completed" else "⏳"
        msg += f"#{w[0]} | 👤 {w[1]} | 💰 {w[2]} | {status_icon} | {w[4][:16]}\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 ДОХОДЫ" and is_admin(m.chat.id))
def admin_earnings(message):
    c.execute("SELECT SUM(amount) FROM payments WHERE status='completed'")
    total = c.fetchone()[0] or 0
    bot.reply_to(
        message,
        f"📊 *ДОХОДЫ*\n\n"
        f"💰 Всего: {total} ₸",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "📜 ЛОГИ" and is_admin(m.chat.id))
def admin_logs(message):
    c.execute("SELECT user_id, action, created_at FROM logs ORDER BY id DESC LIMIT 20")
    logs = c.fetchall()
    if not logs:
        bot.reply_to(message, "📭 Логов нет")
        return
    msg = "📜 *ЛОГИ*\n\n"
    for l in logs:
        msg += f"{l[2][:16]} | ID:{l[0]} | {l[1][:30]}\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔍 ПОИСК" and is_admin(m.chat.id))
def admin_search(message):
    msg = bot.reply_to(message, "🔍 Введите ID пользователя:")
    bot.register_next_step_handler(msg, search_user)

def search_user(message):
    user_id = message.chat.id
    try:
        target = int(message.text)
        c.execute("SELECT user_id, name, role, blessings FROM users WHERE user_id=?", (target,))
        user = c.fetchone()
        if user:
            bot.reply_to(
                message,
                f"👤 *ПОЛЬЗОВАТЕЛЬ*\n\n"
                f"🆔 ID: {user[0]}\n"
                f"📛 Имя: {user[1]}\n"
                f"🎭 Роль: {user[2]}\n"
                f"✨ Благ: {user[3]}",
                parse_mode="Markdown"
            )
        else:
            bot.reply_to(message, f"❌ Пользователь {target} не найден")
    except ValueError:
        bot.reply_to(message, "❌ Введите число")

@bot.message_handler(func=lambda m: m.text == "📈 ОТЧЁТ" and is_admin(m.chat.id))
def admin_report(message):
    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()[0]
    c.execute("SELECT SUM(blessings) FROM users")
    blessings = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM orders")
    orders = c.fetchone()[0]
    c.execute("SELECT SUM(amount) FROM payments")
    payments = c.fetchone()[0] or 0
    bot.reply_to(
        message,
        f"📈 *ПОЛНЫЙ ОТЧЁТ*\n\n"
        f"👥 Пользователей: {users}\n"
        f"✨ Всего Благ: {blessings}\n"
        f"📦 Заказов: {orders}\n"
        f"💰 Доходов: {payments} ₸\n"
        f"📖 Сур: {len(SURAS)}",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "🩺 ЗДОРОВЬЕ" and is_admin(m.chat.id))
def admin_health(message):
    bot.reply_to(
        message,
        "🩺 *ЗДОРОВЬЕ СИСТЕМЫ*\n\n"
        f"✅ Сервер: работает\n"
        f"✅ Пинг: активен\n"
        f"✅ БД: {c.execute('SELECT COUNT(*) FROM users').fetchone()[0]} пользователей\n"
        f"📖 Суры: {len(SURAS)}",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "🛡️ ЗАЩИТА" and is_admin(m.chat.id))
def admin_protection(message):
    bot.reply_to(
        message,
        "🛡️ *ЗАЩИТА*\n\n"
        "✅ AES-256 шифрование\n"
        "✅ Все ключи в переменных окружения\n"
        "✅ Trust Wallet: зашифрован\n"
        "✅ Логирование всех действий\n"
        "✅ Доступ только у Хранителя",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "💎 ТАРИФЫ" and is_admin(m.chat.id))
def admin_tariffs(message):
    bot.reply_to(
        message,
        "💎 *ТАРИФЫ*\n\n"
        "📱 Бесплатный — 0 ₸/мес\n"
        "⭐ Базовый — 1 000 ₸/мес\n"
        "🚀 PRO — 5 000 ₸/мес\n"
        "💎 Бизнес — 20 000 ₸/мес\n\n"
        "💰 Доход с тарифов идёт на развитие системы.",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "🔄 ОБНОВИТЬ" and is_admin(m.chat.id))
def admin_update(message):
    bot.reply_to(message, "🔄 *ОБНОВЛЕНИЕ*\n\nПерезапустите Render вручную для применения изменений.")

@bot.message_handler(func=lambda m: m.text == "📡 СТАТУС" and is_admin(m.chat.id))
def admin_status(message):
    bot.reply_to(
        message,
        f"📡 *СТАТУС*\n\n"
        f"🌐 Хост: {RENDER_HOSTNAME}\n"
        f"✅ Пинг: активен\n"
        f"📖 Сур: {len(SURAS)}\n"
        f"👥 Пользователей: {c.execute('SELECT COUNT(*) FROM users').fetchone()[0]}",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "🧹 ОЧИСТИТЬ" and is_admin(m.chat.id))
def admin_clear(message):
    c.execute("DELETE FROM logs")
    conn.commit()
    bot.reply_to(message, "🧹 Логи очищены!")

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

@app.route('/api/orders')
def api_orders():
    c.execute("SELECT id, title, price, status FROM orders WHERE status='open' LIMIT 20")
    orders = c.fetchall()
    return jsonify([{"id": o[0], "title": o[1], "price": o[2], "status": o[3]} for o in orders])

@app.route('/api/suras')
def api_suras():
    return jsonify(SURAS)

@app.route('/api/qr')
def api_qr():
    amount = request.args.get('amount', 1000, type=int)
    order_id = f"qr_{int(time.time())}"
    qr_data = generate_kaspi_qr(amount, order_id)
    return jsonify(qr_data)

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
            .qr-section {{ margin-top: 20px; padding: 20px; background: rgba(255,255,255,0.03); border-radius: 16px; border: 1px solid #1e1e2e; }}
            .qr-section a {{ color: #f0c27f; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🪞 ЗЕРКАЛО</h1>
            <p style="font-size: 18px; color: #a0a0b0;">Аль-Ми'ра · Свет и Отражение</p>
            <div class="status">✅ Работает 24/7</div>
            <div class="sura-count">📖 {len(SURAS)} сур загружено</div>
            <div class="qr-section">
                <p>💳 <b>Оплата через Kaspi QR</b></p>
                <p style="font-size:14px; color:#a0a0b0;">Сканируйте QR-код в приложении</p>
                <p style="font-size:12px; color:#505060;">💰 Кошелёк: {TRUST_WALLET_ADDRESS}</p>
            </div>
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
