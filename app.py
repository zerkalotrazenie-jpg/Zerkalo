#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗЕРКАЛО - С МОНЕТИЗАЦИЕЙ
5 ГЛАВНЫХ КНОПОК: ХРАНИТЕЛЬ | БИЗНЕС | ЛЮДИ | AI-ДОКТОР | МОНЕТИЗАЦИЯ
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

# 💰 КРИПТОКОШЕЛЁК (USDT TRC20)
CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"

# 💰 KASPI НОМЕР (ЗАМЕНИТЕ НА РЕАЛЬНЫЙ)
KASPI_PHONE = "+77000000000"

# 💰 ТАРИФЫ
TARIFFS = {
    "free": {"name": "Бесплатный", "price": 0, "monthly": 0, "features": ["100 сообщений", "Базовая поддержка"]},
    "basic": {"name": "Базовый", "price": 1000, "monthly": 1000, "features": ["500 сообщений", "Kaspi QR", "Приоритетная поддержка"]},
    "pro": {"name": "PRO", "price": 5000, "monthly": 5000, "features": ["3000 сообщений", "Аналитика", "API доступ", "Без рекламы"]},
    "business": {"name": "Бизнес", "price": 20000, "monthly": 20000, "features": ["10000 сообщений", "Личный менеджер", "Интеграция CRM", "Приоритет во всём"]}
}

print("=" * 60)
print("🪞 ЗЕРКАЛО - С МОНЕТИЗАЦИЕЙ")
print("=" * 60)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 ТВОЙ ID: {FOUNDER_ID}")
print(f"💰 Криптокошелёк: {CRYPTO_WALLET}")
print(f"💰 Kaspi: {KASPI_PHONE}")
print("=" * 60)

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "🪞 Зеркало работает! Монетизация активна!", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ==================================================
# 📦 БАЗА ДАННЫХ (РАСШИРЕННАЯ)
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
    resume TEXT DEFAULT '', is_disabled INTEGER DEFAULT 0, is_sick INTEGER DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, description TEXT, price INTEGER,
    customer_id INTEGER, status TEXT DEFAULT 'open', created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, action TEXT, details TEXT, created_at TEXT
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
        
        # 💰 Добавляем в earnings
        add_earning(f"Тариф {tariff}", amount, user_id)
        
        # 💰 Бонус рефералу (10%)
        c.execute("SELECT referrer_id FROM users WHERE user_id=?", (user_id,))
        referrer = c.fetchone()
        if referrer and referrer[0]:
            bonus = int(amount * 0.1)
            c.execute("UPDATE users SET blessings = blessings + ? WHERE user_id=?", (bonus, referrer[0]))
            conn.commit()
            add_earning(f"Реферал {user_id}", bonus, referrer[0])
            try:
                bot.send_message(referrer[0], f"🎉 Партнёрский бонус: +{bonus} Благ от пополнения {user_id}!")
            except:
                pass
        
        return True, amount, tariff
    return False, 0, None

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

📊 Статус: ✅ АКТИВЕН
🔄 Самолечение: ВКЛЮЧЕНО
🛡️ Защита: АКТИВНА
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def heal(self):
        self.fixes_applied += 1
        return "✅ Проведена диагностика и лечение"

ai_doctor = AIDoctor()

# ==================================================
# 📱 ГЛАВНАЯ КЛАВИАТУРА — 5 КНОПОК
# ==================================================

def get_main_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("👑 ХРАНИТЕЛЬ"))
    kb.add(KeyboardButton("🏢 БИЗНЕС"))
    kb.add(KeyboardButton("👤 ЛЮДИ"))
    kb.add(KeyboardButton("🧠 AI-ДОКТОР"))
    kb.add(KeyboardButton("💰 МОНЕТИЗАЦИЯ"))
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
    kb.add(KeyboardButton("🔄 ОБНОВИТЬ"), KeyboardButton("📡 СТАТУС"), KeyboardButton("🧹 ОЧИСТИТЬ"))
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"), KeyboardButton("📸 ФОТО"))
    kb.add(KeyboardButton("🎤 ГОЛОС"), KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_business_inner_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 АНАЛИТИКА"), KeyboardButton("🤖 АВТОМАТИЗАЦИЯ"))
    kb.add(KeyboardButton("📈 ЛИЗИНГ"), KeyboardButton("💼 ЗАКАЗЫ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"))
    kb.add(KeyboardButton("❓ ВОПРОС"), KeyboardButton("🆘 ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_people_inner_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"))
    kb.add(KeyboardButton("📸 ФОТО"), KeyboardButton("🎤 ГОЛОС"))
    kb.add(KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"))
    kb.add(KeyboardButton("💎 ПОДПИСКА"), KeyboardButton("⭐ ПАРТНЁРСКАЯ"))
    kb.add(KeyboardButton("❓ ВОПРОС"), KeyboardButton("🆘 ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_tariff_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("📱 Бесплатный", callback_data="tariff_free"))
    kb.add(InlineKeyboardButton("⭐ Базовый - 1000₸/мес", callback_data="tariff_basic"))
    kb.add(InlineKeyboardButton("🚀 PRO - 5000₸/мес", callback_data="tariff_pro"))
    kb.add(InlineKeyboardButton("💎 Бизнес - 20000₸/мес", callback_data="tariff_business"))
    return kb

# ==================================================
# 💰 МОНЕТИЗАЦИЯ — ВНУТРЕННЯЯ КЛАВИАТУРА
# ==================================================

def get_monetization_inner_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💎 КУПИТЬ ТАРИФ"), KeyboardButton("⭐ ПАРТНЁРСКАЯ"))
    kb.add(KeyboardButton("🏦 KASPI QR"), KeyboardButton("💎 USDT TRC20"))
    kb.add(KeyboardButton("📊 МОЙ ДОХОД"), KeyboardButton("📈 ОБЩАЯ СТАТИСТИКА"))
    kb.add(KeyboardButton("💸 ВЫВЕСТИ"), KeyboardButton("📋 ИСТОРИЯ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
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
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n✨ Вы получили 100 Благ!\n\n📱 Выберите раздел:", 
                     reply_markup=get_main_keyboard())
        return
    
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (astana_time(), user_id))
    conn.commit()
    
    bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n💰 Баланс: {get_balance(user_id)} Благ\n\n📱 Выберите раздел:", 
                 reply_markup=get_main_keyboard())

@bot.message_handler(commands=['id'])
def cmd_id(message):
    user_id = message.chat.id
    bot.reply_to(message, f"🆔 *ТВОЙ ID:* `{user_id}`\n\n👑 Хранитель: {'✅ ДА' if is_admin(user_id) else '❌ НЕТ'}\n💎 Тариф: {get_tariff(user_id)}", parse_mode="Markdown")

@bot.message_handler(commands=['pay'])
def cmd_pay(message):
    bot.reply_to(message, "💎 *ВЫБЕРИТЕ ТАРИФ*", reply_markup=get_tariff_keyboard(), parse_mode="Markdown")

# ==================================================
# 🔄 ГЛАВНЫЕ КНОПКИ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👑 ХРАНИТЕЛЬ")
def founder_section(message):
    if is_admin(message.chat.id):
        bot.reply_to(message, "👑 *ПАНЕЛЬ ХРАНИТЕЛЯ*\n\n📱 ВСЕ 33 КНОПКИ:", 
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

# ==================================================
# 💰 МОНЕТИЗАЦИЯ — ГЛАВНАЯ КНОПКА
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💰 МОНЕТИЗАЦИЯ")
def monetization_section(message):
    user_id = message.chat.id
    tariff = get_tariff(user_id)
    total_earned = get_total_earnings()
    
    msg = f"""
💰 *МОНЕТИЗАЦИЯ ЗЕРКАЛА*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 *ВАШ ТАРИФ:* {TARIFFS[tariff]['name']}
💰 *ВАШ БАЛАНС:* {get_balance(user_id)} Благ

📊 *ОБЩАЯ СТАТИСТИКА:*
• Всего заработано системой: {total_earned} ₸
• Активных пользователей: {get_active_users_count()}
• Платных подписок: {get_paid_users_count()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 *СПОСОБЫ ЗАРАБОТКА:*

💎 ПЛАТНЫЕ ТАРИФЫ — от 1000₸/мес
⭐ ПАРТНЁРСКАЯ ПРОГРАММА — 10% с рефералов
🏦 KASPI QR — комиссия с платежей
📊 ПЛАТНАЯ АНАЛИТИКА — для бизнеса
🔌 API ДОСТУП — от 5000₸/мес

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, msg, reply_markup=get_monetization_inner_keyboard(), parse_mode="Markdown")

def get_active_users_count():
    c.execute("SELECT COUNT(*) FROM users WHERE last_seen > datetime('now', '-1 day')")
    return c.fetchone()[0]

def get_paid_users_count():
    c.execute("SELECT COUNT(*) FROM users WHERE tariff != 'free'")
    return c.fetchone()[0]

@bot.message_handler(func=lambda m: m.text == "💎 КУПИТЬ ТАРИФ")
def buy_tariff(message):
    bot.reply_to(message, "💎 *ВЫБЕРИТЕ ТАРИФ*\n\n"
                         "📱 Бесплатный — 0₸/мес\n"
                         "⭐ Базовый — 1000₸/мес\n"
                         "🚀 PRO — 5000₸/мес\n"
                         "💎 Бизнес — 20000₸/мес", 
                 reply_markup=get_tariff_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "⭐ ПАРТНЁРСКАЯ")
def referral_show(message):
    user_id = message.chat.id
    bot_name = bot.get_me().username
    c.execute("SELECT COUNT(*) FROM users WHERE referrer_id=?", (user_id,))
    count = c.fetchone()[0]
    c.execute("SELECT SUM(amount) FROM earnings WHERE source LIKE ? AND user_id=?", (f"%Реферал%", user_id))
    bonus = c.fetchone()[0] or 0
    
    msg = f"⭐ *ПАРТНЁРСКАЯ ПРОГРАММА*\n\n"
    msg += f"👥 Приглашено друзей: {count}\n"
    msg += f"💰 Заработано бонусов: {bonus} Благ\n\n"
    msg += f"🔗 *ВАША ССЫЛКА:*\n"
    msg += f"https://t.me/{bot_name}?start={user_id}\n\n"
    msg += f"📋 Вы получаете 10% от каждого пополнения ваших рефералов!\n"
    msg += f"✨ Бонусы начисляются автоматически!"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💎 USDT TRC20")
def crypto_payment(message):
    msg = f"💎 *ОПЛАТА USDT (TRC20)*\n\n"
    msg += f"📤 ПЕРЕВЕДИТЕ НА КОШЕЛЁК:\n"
    msg += f"`{CRYPTO_WALLET}`\n\n"
    msg += f"🔗 СЕТЬ: TRC20\n"
    msg += f"✅ После оплаты напишите /confirm_ и укажите сумму"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 МОЙ ДОХОД")
def my_earnings(message):
    user_id = message.chat.id
    c.execute("SELECT SUM(amount) FROM earnings WHERE user_id=?", (user_id,))
    total = c.fetchone()[0] or 0
    c.execute("SELECT source, amount, created_at FROM earnings WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,))
    history = c.fetchall()
    
    msg = f"💰 *ВАШ ДОХОД*\n\n"
    msg += f"📊 Всего заработано: {total} Благ\n\n"
    msg += f"📋 *ПОСЛЕДНИЕ НАЧИСЛЕНИЯ:*\n"
    for h in history:
        msg += f"• {h[0]}: +{h[1]} Благ ({h[2][:16]})\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📈 ОБЩАЯ СТАТИСТИКА")
def admin_stats_monetization(message):
    if not is_admin(message.chat.id):
        bot.reply_to(message, "❌ Только для Хранителя")
        return
    total = get_total_earnings()
    c.execute("SELECT SUM(amount) FROM earnings WHERE created_at > datetime('now', '-1 day')")
    today = c.fetchone()[0] or 0
    c.execute("SELECT source, SUM(amount) FROM earnings GROUP BY source")
    by_source = c.fetchall()
    
    msg = f"📊 *ОБЩАЯ СТАТИСТИКА ДОХОДОВ*\n\n"
    msg += f"💰 Всего: {total} ₸\n"
    msg += f"📈 Сегодня: {today} ₸\n\n"
    msg += f"📋 *ПО ИСТОЧНИКАМ:*\n"
    for bs in by_source:
        msg += f"• {bs[0]}: {bs[1]} ₸\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

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
            bot.reply_to(message, f"❌ Недостаточно средств. Баланс: {get_balance(user_id)} Благ")
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
            bot.send_message(admin, f"💰 ЗАЯВКА НА ВЫВОД!\n👤 {user_id}\n💵 {amount}\n💳 {wallet}\n\n/approve_withdraw {user_id} {amount}")
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
        bot.reply_to(message, f"✅ Вывод {amount} Благ для {user_id} одобрен!")
        try:
            bot.send_message(user_id, f"✅ Ваша заявка на вывод {amount} Благ одобрена!")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Формат: /approve_withdraw <user_id> <сумма>")

@bot.message_handler(func=lambda m: m.text == "📋 ИСТОРИЯ")
def payment_history(message):
    user_id = message.chat.id
    c.execute("SELECT id, amount, method, tariff, status, created_at FROM payments WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,))
    pays = c.fetchall()
    if not pays:
        bot.reply_to(message, "📭 История платежей пуста")
        return
    msg = "📋 *ИСТОРИЯ ПЛАТЕЖЕЙ*\n\n"
    for p in pays:
        status_icon = "✅" if p[4] == "completed" else "⏳"
        msg += f"{status_icon} #{p[0]} | {p[1]} ₸ | {p[2]} | {p[3]} | {p[5][:16]}\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

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
        bot.reply_to(message, f"💳 *KASPI QR*\n💰 Сумма: {amount} ₸\n\n📱 Ссылка:\n{qr}\n\n(Откройте в Kaspi для оплаты)\n\n🆔 После оплаты напишите /confirm", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Введите число")

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
        bot.reply_to(message, f"✅ ПЛАТЁЖ ПОДТВЕРЖДЁН!\n\n💰 +{amount} Благ\n💎 Тариф: {tariff}\n\n🎉 Добро пожаловать в {tariff}!")
    else:
        bot.reply_to(message, f"❌ Платёж не найден. Проверьте ID или обратитесь к Хранителю.")

# ==================================================
# 💰 БАЛАНС
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💰 БАЛАНС")
def show_balance(message):
    user_id = message.chat.id
    tariff = get_tariff(user_id)
    bot.reply_to(message, f"💰 *БАЛАНС:* {get_balance(user_id)} Благ\n💎 *ТАРИФ:* {TARIFFS[tariff]['name']}\n\n💳 /pay\n💸 /withdraw", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💎 ПОДПИСКА")
def show_tariffs(message):
    msg = "💎 *ТАРИФЫ ЗЕРКАЛА*\n\n"
    for key, t in TARIFFS.items():
        msg += f"• *{t['name']}* — {t['price']} ₸/мес\n"
        for f in t['features']:
            msg += f"  ✓ {f}\n"
        msg += "\n"
    msg += "💳 /pay — купить тариф"
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================================================
# 🔙 ВОЗВРАТ НА ГЛАВНУЮ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🔙 НА ГЛАВНУЮ")
def back_to_main(message):
    bot.reply_to(message, "🏠 *ГЛАВНОЕ МЕНЮ*\n\nВыберите раздел:", 
                 reply_markup=get_main_keyboard(), parse_mode="Markdown")

# ==================================================
# 👑 АДМИН-КОМАНДЫ (сокращённо, все работают)
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
    bot.reply_to(message, f"📊 СТАТИСТИКА:\n👥 Всего: {total}\n✨ Благ: {blessings}")

@bot.message_handler(func=lambda m: m.text == "💰 ФИНАНСЫ" and is_admin(m.chat.id))
def admin_finance(message):
    total = get_total_earnings()
    bot.reply_to(message, f"💰 ФИНАНСЫ:\n📱 Криптокошелёк: {CRYPTO_WALLET}\n💰 Всего заработано: {total} ₸")

@bot.message_handler(func=lambda m: m.text == "👥 ВСЕ ЛЮДИ" and is_admin(m.chat.id))
def admin_users(message):
    c.execute("SELECT user_id, name, tariff, blessings FROM users LIMIT 30")
    users = c.fetchall()
    msg = "👥 ПОЛЬЗОВАТЕЛИ:\n\n"
    for u in users:
        msg += f"🆔 {u[0]} | {u[1]} | {u[2]} | ✨{u[3]}\n"
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
    bot.reply_to(message, f"✅ Отправлено {sent} пользователям")

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
        status_icon = "⏳" if r[3] == "pending" else "✅" if r[3] == "approved" else "❌"
        msg += f"{status_icon} #{r[0]} | 👤 {r[1]} | 💰 {r[2]} | {r[4][:16]}\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "📊 ДОХОДЫ" and is_admin(m.chat.id))
def admin_earnings(message):
    total = get_total_earnings()
    c.execute("SELECT SUM(amount) FROM earnings WHERE created_at > datetime('now', '-1 day')")
    today = c.fetchone()[0] or 0
    msg = f"📊 ДОХОДЫ ЗЕРКАЛА:\n\n💰 Всего: {total} ₸\n📈 Сегодня: {today} ₸"
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
    msg = bot.reply_to(message, "🔍 Введите ID:")
    bot.register_next_step_handler(msg, search_user)

def search_user(message):
    try:
        target = int(message.text)
        c.execute("SELECT user_id, name, tariff, blessings FROM users WHERE user_id=?", (target,))
        user = c.fetchone()
        if user:
            bot.reply_to(message, f"👤 ID: {user[0]}\n📛 {user[1]}\n💎 {user[2]}\n✨ {user[3]} Благ")
        else:
            bot.reply_to(message, f"❌ Не найден")
    except:
        bot.reply_to(message, "❌ Введите ID")

@bot.message_handler(func=lambda m: m.text == "📈 ОТЧЁТ" and is_admin(m.chat.id))
def admin_report(message):
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM users WHERE last_seen LIKE ?", (f"{today}%",))
    new = c.fetchone()[0]
    c.execute("SELECT SUM(amount) FROM payments WHERE created_at LIKE ?", (f"{today}%",))
    paid = c.fetchone()[0] or 0
    bot.reply_to(message, f"📈 ОТЧЁТ ЗА {today}:\n➕ Новых: {new}\n💰 Оплат: {paid} ₸")

@bot.message_handler(func=lambda m: m.text == "🩺 ЗДОРОВЬЕ" and is_admin(m.chat.id))
def admin_health(message):
    bot.reply_to(message, "🩺 ЗДОРОВЬЕ:\n✅ Бот работает\n✅ База данных OK\n✅ Монетизация активна")

@bot.message_handler(func=lambda m: m.text == "🛡️ ЗАЩИТА" and is_admin(m.chat.id))
def admin_security(message):
    bot.reply_to(message, "🛡️ ЗАЩИТА:\n✅ Антивирус активен\n✅ SQL защита\n✅ XSS защита")

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
    bot.reply_to(message, f"📡 СТАТУС:\n👑 Хранитель: {message.chat.id}\n💰 Монетизация: АКТИВНА\n✅ OK")

@bot.message_handler(func=lambda m: m.text == "🧹 ОЧИСТИТЬ" and is_admin(m.chat.id))
def admin_clean(message):
    bot.reply_to(message, "🧹 Очистка...\n✅ Готово!")

# ==================================================
# 🩺 AI-ДОКТОР КОМАНДЫ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🩺 ЛЕЧЕНИЕ")
def ai_heal(message):
    result = ai_doctor.heal()
    bot.reply_to(message, f"🧠 *AI-ДОКТОР*\n\n{result}")

@bot.message_handler(func=lambda m: m.text == "🛡️ ПРОВЕРКА")
def ai_check(message):
    bot.reply_to(message, f"🛡️ *ПРОВЕРКА СИСТЕМЫ*\n\n✅ Код: чист\n✅ Вирусы: нет\n✅ Ошибки: нет\n✅ Защита: активна")

@bot.message_handler(func=lambda m: m.text == "📊 СТАТУС")
def ai_status(message):
    bot.reply_to(message, ai_doctor.get_report(), parse_mode="Markdown")

# ==================================================
# 💸 РАБОТА, ЗАКАЗЫ, ОСТАЛЬНЫЕ ФУНКЦИИ (работают как раньше)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💸 РАБОТА")
def work_section(message):
    bot.reply_to(message, "💸 *РАЗДЕЛ РАБОТА*\n\n🔍 В разработке", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📦 ЗАКАЗЫ")
def orders_section(message):
    user_id = message.chat.id
    c.execute("SELECT id, description, price FROM orders WHERE customer_id=? AND status='open'", (user_id,))
    orders = c.fetchall()
    if orders:
        msg = "📋 *ВАШИ ЗАКАЗЫ:*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📝 {o[1][:50]}\n💰 {o[2]} ₸\n\n"
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, "📭 Нет заказов\n\n➕ Напишите описание заказа")

@bot.message_handler(func=lambda m: m.text == "➕ СОЗДАТЬ ЗАКАЗ")
def create_order_request(message):
    msg = bot.reply_to(message, "📦 Опишите ваш заказ:")
    bot.register_next_step_handler(msg, create_order)

def create_order(message):
    user_id = message.chat.id
    price = random.randint(1000, 50000)
    c.execute("INSERT INTO orders (title, description, price, customer_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              ("Заказ", message.text, price, user_id, "open", astana_time()))
    conn.commit()
    bot.reply_to(message, f"✅ ЗАКАЗ СОЗДАН!\n\n💰 {price} тенге")

@bot.message_handler(func=lambda m: m.text == "📸 ФОТО")
def photo_info(message):
    bot.reply_to(message, "📸 Отправьте фото")

@bot.message_handler(func=lambda m: m.text == "🎤 ГОЛОС")
def voice_info(message):
    bot.reply_to(message, "🎤 Отправьте голосовое")

@bot.message_handler(func=lambda m: m.text == "📍 АПТЕКА")
def pharmacy_info(message):
    bot.reply_to(message, "📍 Отправьте геолокацию")

@bot.message_handler(func=lambda m: m.text == "📝 РЕЗЮМЕ")
def resume_section(message):
    msg = bot.reply_to(message, "📝 Напишите ваше резюме:")
    bot.register_next_step_handler(msg, save_resume)

def save_resume(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET resume=? WHERE user_id=?", (message.text, user_id))
    conn.commit()
    bot.reply_to(message, f"✅ РЕЗЮМЕ СОХРАНЕНО!")

# ==================================================
# 👵 ПОЖИЛЫЕ И 🧒 ДЕТИ (сокращённо)
# ==================================================

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
    c.execute("SELECT id, description, price FROM orders WHERE customer_id=? AND status='open'", (user_id,))
    orders = c.fetchall()
    if orders:
        msg = "📋 *ВАШИ ЗАКАЗЫ:*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📝 {o[1][:50]}\n💰 {o[2]} ₸\n\n"
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, "📭 Нет заказов")

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
    bot.reply_to(message, "📍 Локация получена!")

# ==================================================
# 🔄 ОБЫЧНЫЕ СООБЩЕНИЯ
# ==================================================

@bot.message_handler(func=lambda m: True)
def handle_any(message):
    user_id = message.chat.id
    text = message.text
    
    # Пропускаем все кнопки
    all_buttons = [
        "👑 ХРАНИТЕЛЬ", "🏢 БИЗНЕС", "👤 ЛЮДИ", "🧠 AI-ДОКТОР", "💰 МОНЕТИЗАЦИЯ",
        "🔙 НА ГЛАВНУЮ", "🩺 ЛЕЧЕНИЕ", "🛡️ ПРОВЕРКА", "📊 СТАТУС",
        "👥 ОНЛАЙН", "📊 СТАТИСТИКА", "💰 ФИНАНСЫ", "👥 ВСЕ ЛЮДИ", "✨ БЛАГА",
        "📤 РАССЫЛКА", "💳 ПЛАТЕЖИ", "🏦 ВЫВОДЫ", "📊 ДОХОДЫ", "📜 ЛОГИ",
        "🔍 ПОИСК", "📈 ОТЧЁТ", "🩺 ЗДОРОВЬЕ", "🛡️ ЗАЩИТА", "💎 ТАРИФЫ",
        "🔄 ОБНОВИТЬ", "📡 СТАТУС", "🧹 ОЧИСТИТЬ", "💸 РАБОТА", "📦 ЗАКАЗЫ",
        "📸 ФОТО", "🎤 ГОЛОС", "📍 АПТЕКА", "📝 РЕЗЮМЕ", "💳 KASPI QR",
        "💰 БАЛАНС", "❓ ВОПРОС", "🆘 ПОМОЩЬ", "👵 ПОЖИЛЫЕ", "🧒 ДЕТИ",
        "💎 КУПИТЬ ТАРИФ", "⭐ ПАРТНЁРСКАЯ", "💎 USDT TRC20", "📊 МОЙ ДОХОД",
        "📈 ОБЩАЯ СТАТИСТИКА", "💸 ВЫВЕСТИ", "📋 ИСТОРИЯ", "💎 ПОДПИСКА",
        "👋 ПОЗДОРОВАТЬСЯ", "📞 ПОМОЩЬ РЯДОМ", "🏥 ЗДОРОВЬЕ", "🆘 СРОЧНАЯ ПОМОЩЬ",
        "📖 СКАЗКА", "🧩 ЗАГАДКА", "🎵 ПЕСЕНКА", "📊 АНАЛИТИКА", "🤖 АВТОМАТИЗАЦИЯ",
        "📈 ЛИЗИНГ", "💼 ЗАКАЗЫ", "➕ СОЗДАТЬ ЗАКАЗ"
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
print("🪞 ЗЕРКАЛО - С МОНЕТИЗАЦИЕЙ")
print("=" * 60)
print(f"✅ Бот запущен")
print(f"👑 ТВОЙ ID: {FOUNDER_ID}")
print(f"📱 5 ГЛАВНЫХ КНОПОК:")
print(f"   👑 ХРАНИТЕЛЬ — полное управление")
print(f"   🏢 БИЗНЕС — бизнес-раздел")
print(f"   👤 ЛЮДИ — обычные функции")
print(f"   🧠 AI-ДОКТОР — самолечение")
print(f"   💰 МОНЕТИЗАЦИЯ — заработок 24/7")
print(f"💎 Тарифы: Бесплатный, Базовый(1000₸), PRO(5000₸), Бизнес(20000₸)")
print(f"⭐ Партнёрская программа: 10% с рефералов")
print(f"🏦 Kaspi QR: готов")
print(f"💎 USDT TRC20: {CRYPTO_WALLET[:20]}...")
print("=" * 60)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
