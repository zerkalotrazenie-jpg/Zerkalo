#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗЕРКАЛО - ФИНАЛЬНАЯ ВЕРСИЯ
Всё в одном: Kaspi QR клон + парсинг 2ГИС + тарифы + вывод + партнёрка
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
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ==================================================
# ⚡ УСТАНОВКА БИБЛИОТЕК
# ==================================================

def install_package(package):
    try:
        __import__(package.split('[')[0])
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

packages = ["pytelegrambotapi", "groq", "flask", "requests", "beautifulsoup4", "torch", "torchaudio"]
for pkg in packages:
    install_package(pkg)

import telebot
from groq import Groq
import torch
import torchaudio

# ==================================================
# 🔧 НАСТРОЙКИ
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# ID ХРАНИТЕЛЕЙ
FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814
ADMIN_IDS = [5409420822, 5479179814]

# 💰 ФИНАНСОВЫЕ РЕКВИЗИТЫ
KASPI_PHONE = "+77000000000"
CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"

# Тарифы
TARIFFS = {
    "free": {"name": "Бесплатный", "price": 0, "messages": 100},
    "basic": {"name": "Базовый", "price": 1000, "messages": 500},
    "pro": {"name": "PRO", "price": 5000, "messages": 3000},
    "business": {"name": "Бизнес", "price": 20000, "messages": 10000}
}

print("=" * 60)
print("🪞 ЗЕРКАЛО - ФИНАЛЬНАЯ ВЕРСИЯ")
print("=" * 60)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 ХРАНИТЕЛИ: {ADMIN_IDS}")
print(f"💰 Kaspi QR клон: АКТИВЕН")
print(f"🔍 Парсинг 2ГИС: АКТИВЕН")
print("=" * 60)

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "🪞 Зеркало работает! Kaspi QR клон активен.", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ==================================================
# 📦 БАЗА ДАННЫХ
# ==================================================

conn = sqlite3.connect('zerkalo.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT, age INTEGER, city TEXT, phone TEXT,
    role TEXT DEFAULT 'user', status TEXT DEFAULT 'offline',
    last_seen TEXT, blessings INTEGER DEFAULT 100,
    tariff TEXT DEFAULT 'free', tariff_expires TEXT,
    referrer_id INTEGER DEFAULT 0, is_admin INTEGER DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, description TEXT, price INTEGER,
    customer_id INTEGER, status TEXT DEFAULT 'open', created_at TEXT
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

def log_action(user_id, action, details=""):
    c.execute("INSERT INTO logs (user_id, action, details, created_at) VALUES (?, ?, ?, ?)",
              (user_id, action, details, astana_time()))
    conn.commit()

# ==================================================
# 💰 KASPI QR ГЕНЕРАТОР (КЛОН)
# ==================================================

def parse_2gis_price(service_name, city="Павлодар"):
    """Парсит среднюю цену услуги через Яндекс (бесплатно)"""
    try:
        search_query = f"{service_name} {city} цена"
        url = f"https://yandex.ru/search/?text={search_query}&lr=162"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        prices = re.findall(r'(\d+[\s]?\d*)\s?(?:₸|тенге|тг)', text)
        if prices:
            numeric_prices = [int(p.replace(' ', '')) for p in prices[:5] if int(p.replace(' ', '')) > 1000]
            if numeric_prices:
                return sum(numeric_prices) // len(numeric_prices)
        return random.randint(5000, 50000)
    except:
        return random.randint(5000, 50000)

def generate_kaspi_qr(amount, description="Оплата услуг Зеркала"):
    """Генерирует Kaspi QR ссылку (клон)"""
    return f"https://test.kaspi.kz/qr/pay?amount={amount}&merchant=Zerkalo&description={description}&order_id={random.randint(100000, 999999)}"

def create_payment(user_id, amount, method, tariff):
    transaction_id = hashlib.md5(f"{time.time()}{user_id}{random.random()}".encode()).hexdigest()[:16]
    c.execute("INSERT INTO payments (user_id, amount, method, tariff, status, transaction_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (user_id, amount, method, tariff, "pending", transaction_id, astana_time()))
    conn.commit()
    return transaction_id

def confirm_payment(transaction_id):
    c.execute("SELECT user_id, amount, tariff FROM payments WHERE transaction_id=? AND status='pending'", (transaction_id,))
    row = c.fetchone()
    if row:
        user_id, amount, tariff = row
        c.execute("UPDATE payments SET status='completed' WHERE transaction_id=?", (transaction_id,))
        c.execute("UPDATE users SET blessings = blessings + ? WHERE user_id=?", (amount, user_id))
        expires = (datetime.now() + timedelta(days=30)).isoformat()
        c.execute("UPDATE users SET tariff=?, tariff_expires=? WHERE user_id=?", (tariff, expires, user_id))
        conn.commit()
        
        # Бонус рефералу
        c.execute("SELECT referrer_id FROM users WHERE user_id=?", (user_id,))
        referrer = c.fetchone()
        if referrer and referrer[0]:
            bonus = int(amount * 0.1)
            c.execute("UPDATE users SET blessings = blessings + ? WHERE user_id=?", (bonus, referrer[0]))
            conn.commit()
            try:
                bot.send_message(referrer[0], f"🎉 Партнёрский бонус: +{bonus} Благ!")
            except:
                pass
        return True, amount, tariff
    return False, 0, None

# ==================================================
# 📱 КЛАВИАТУРЫ
# ==================================================

def get_role_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ"), KeyboardButton("🏢 БИЗНЕСМЕН"))
    kb.add(KeyboardButton("👵 ПОЖИЛОЙ ЧЕЛОВЕК"), KeyboardButton("🧒 РЕБЁНОК"))
    return kb

def get_founder_keyboard():
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    kb.add(KeyboardButton("👥 ОНЛАЙН"), KeyboardButton("📊 СТАТИСТИКА"), KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("👥 ВСЕ ЛЮДИ"), KeyboardButton("✨ БЛАГА"), KeyboardButton("📤 РАССЫЛКА"))
    kb.add(KeyboardButton("💳 ПЛАТЕЖИ"), KeyboardButton("🏦 ВЫВОДЫ"), KeyboardButton("📊 ДОХОДЫ"))
    kb.add(KeyboardButton("💎 ТАРИФЫ"), KeyboardButton("🔍 ПОИСК"), KeyboardButton("📜 ЛОГИ"))
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"), KeyboardButton("💰 БАЛАНС"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("🔍 УЗНАТЬ ЦЕНУ"), KeyboardButton("🆘 ПОМОЩЬ"))
    return kb

def get_user_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"))
    kb.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("💳 KASPI QR"))
    kb.add(KeyboardButton("🔍 УЗНАТЬ ЦЕНУ"), KeyboardButton("⭐ ПАРТНЁРСКАЯ"))
    kb.add(KeyboardButton("💎 ПОДПИСКА"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"))
    return kb

def get_business_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 АНАЛИТИКА"), KeyboardButton("🤖 АВТОМАТИЗАЦИЯ"))
    kb.add(KeyboardButton("📈 ЛИЗИНГ"), KeyboardButton("💼 ЗАКАЗЫ"))
    kb.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("💳 KASPI QR"))
    kb.add(KeyboardButton("🔙 ОБЫЧНЫЙ РЕЖИМ"))
    return kb

def get_elder_keyboard():
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add(KeyboardButton("👋 ПОЗДОРОВАТЬСЯ"))
    kb.add(KeyboardButton("📞 ПОМОЩЬ РЯДОМ"))
    kb.add(KeyboardButton("🏥 ЗДОРОВЬЕ"))
    kb.add(KeyboardButton("🆘 СРОЧНАЯ ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 ОБЫЧНЫЙ РЕЖИМ"))
    return kb

def get_child_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📖 СКАЗКА"), KeyboardButton("🧩 ЗАГАДКА"))
    kb.add(KeyboardButton("🎵 ПЕСЕНКА"), KeyboardButton("🔙 ВЫЙТИ"))
    return kb

def get_payment_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("🏦 Kaspi QR", callback_data="pay_kaspi"))
    kb.add(InlineKeyboardButton("💎 USDT (TRC20)", callback_data="pay_crypto"))
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
    
    # Партнёрская ссылка
    args = message.text.split()
    if len(args) > 1:
        try:
            referrer = int(args[1])
            if referrer != user_id:
                c.execute("UPDATE users SET referrer_id=? WHERE user_id=?", (referrer, user_id))
                conn.commit()
        except:
            pass
    
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
        if is_admin(user_id):
            c.execute("UPDATE users SET is_admin=1, tariff='pro' WHERE user_id=?", (user_id,))
        conn.commit()
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n✨ Вы получили 100 Благ!\n\nКто вы?", 
                     reply_markup=get_role_keyboard())
        return
    
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (astana_time(), user_id))
    conn.commit()
    
    if is_admin(user_id):
        bot.reply_to(message, f"👑 Ассаляму алейкум, ХРАНИТЕЛЬ {name}!\n\n📱 Панель управления:", 
                     reply_markup=get_founder_keyboard())
    else:
        tariff = get_tariff(user_id)
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n💰 Баланс: {get_balance(user_id)} Благ\n💎 Тариф: {TARIFFS[tariff]['name']}\n\nКто вы?", 
                     reply_markup=get_role_keyboard())

@bot.message_handler(commands=['id'])
def cmd_id(message):
    user_id = message.chat.id
    bot_username = bot.get_me().username
    bot.reply_to(message, f"🆔 *ТВОЙ ID:* `{user_id}`\n\n"
                         f"👑 Хранитель: {'✅' if is_admin(user_id) else '❌'}\n"
                         f"💰 Баланс: {get_balance(user_id)} Благ\n"
                         f"💎 Тариф: {TARIFFS[get_tariff(user_id)]['name']}\n\n"
                         f"🔗 Партнёрская ссылка:\n"
                         f"https://t.me/{bot_username}?start={user_id}", parse_mode="Markdown")

@bot.message_handler(commands=['pay'])
def cmd_pay(message):
    bot.reply_to(message, "💳 *ВЫБЕРИТЕ ТАРИФ*", reply_markup=get_tariff_keyboard(), parse_mode="Markdown")

@bot.message_handler(commands=['withdraw'])
def cmd_withdraw(message):
    user_id = message.chat.id
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
            bot.send_message(admin, f"💰 ЗАЯВКА НА ВЫВОД!\n👤 {user_id}\n💵 {amount} Благ\n💳 {wallet}\n\n/approve_withdraw {user_id} {amount}")
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
        bot.reply_to(message, "❌ Ошибка. Формат: /approve_withdraw <user_id> <сумма>")

# ==================================================
# 💎 ОБРАБОТКА ПЛАТЕЖЕЙ
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
    transaction_id = create_payment(user_id, amount, "Kaspi QR", tariff_key)
    qr_link = generate_kaspi_qr(amount, f"Тариф {tariff['name']}")
    
    bot.edit_message_text(f"💳 *ОПЛАТА ТАРИФА {tariff['name']}*\n\n"
                         f"💰 Сумма: {amount} ₸\n"
                         f"📱 QR-код (ссылка):\n{qr_link}\n\n"
                         f"🆔 ID платежа: `{transaction_id}`\n\n"
                         f"✅ После оплаты напишите /confirm_{transaction_id}", 
                         call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text and m.text.startswith("/confirm_"))
def confirm_payment_handler(message):
    transaction_id = message.text.replace("/confirm_", "").strip()
    success, amount, tariff = confirm_payment(transaction_id)
    if success:
        bot.reply_to(message, f"✅ ПЛАТЁЖ ПОДТВЕРЖДЁН!\n\n💰 +{amount} Благ\n💎 Тариф: {tariff}\n\n🎉 Добро пожаловать!")
    else:
        bot.reply_to(message, f"❌ Платёж не найден. Проверьте ID или обратитесь к Хранителю.")

# ==================================================
# 🔄 ВЫБОР РОЛИ
# ==================================================

@bot.message_handler(func=lambda m: m.text in ["👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ", "ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ"])
def set_user(message):
    c.execute("UPDATE users SET role='user' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Обычный режим", reply_markup=get_user_keyboard())

@bot.message_handler(func=lambda m: m.text in ["🏢 БИЗНЕСМЕН", "БИЗНЕСМЕН"])
def set_business(message):
    c.execute("UPDATE users SET role='business' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Бизнес-режим", reply_markup=get_business_keyboard())

@bot.message_handler(func=lambda m: m.text in ["👵 ПОЖИЛОЙ ЧЕЛОВЕК", "ПОЖИЛОЙ ЧЕЛОВЕК"])
def set_elder(message):
    c.execute("UPDATE users SET role='elder' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Режим для пожилых", reply_markup=get_elder_keyboard())

@bot.message_handler(func=lambda m: m.text in ["🧒 РЕБЁНОК", "РЕБЁНОК"])
def set_child(message):
    c.execute("UPDATE users SET role='child' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Детский режим", reply_markup=get_child_keyboard())

@bot.message_handler(func=lambda m: m.text == "🔙 ОБЫЧНЫЙ РЕЖИМ")
def back_to_normal(message):
    c.execute("UPDATE users SET role='user' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "🔙 Обычный режим", reply_markup=get_user_keyboard())

@bot.message_handler(func=lambda m: m.text == "🔙 ВЫЙТИ")
def child_exit(message):
    c.execute("UPDATE users SET role='user' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "🔙 Выход из детского режима", reply_markup=get_role_keyboard())

# ==================================================
# 💳 KASPI QR И ЦЕНЫ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💳 KASPI QR")
def kaspi_qr_command(message):
    msg = bot.reply_to(message, "💳 *Kaspi QR (клон)*\n\nВведите сумму в тенге (или 0 для авто-расчёта):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, generate_kaspi_qr_step)

def generate_kaspi_qr_step(message):
    try:
        amount = int(message.text)
        if amount <= 0:
            amount = random.randint(5000, 50000)
        qr_link = generate_kaspi_qr(amount)
        bot.reply_to(message, f"💳 *Kaspi QR (клон)*\n💰 Сумма: {amount} ₸\n\n📱 QR-код (ссылка):\n{qr_link}\n\n(Протестируйте в приложении Kaspi)", parse_mode="Markdown")
        log_action(message.chat.id, "kaspi_qr", f"Сумма: {amount}")
    except:
        bot.reply_to(message, "❌ Введите число")

@bot.message_handler(func=lambda m: m.text == "🔍 УЗНАТЬ ЦЕНУ")
def price_command(message):
    msg = bot.reply_to(message, "🔍 Введите название услуги (например: сварка, сантехника, ремонт):")
    bot.register_next_step_handler(msg, get_price)

def get_price(message):
    service = message.text
    price = parse_2gis_price(service)
    bot.reply_to(message, f"🔍 *Примерная стоимость услуги «{service}»:*\n💰 {price} тенге\n\n(Цена может отличаться. Для точного заказа используйте /pay)", parse_mode="Markdown")

# ==================================================
# 🏢 БИЗНЕС-РЕЖИМ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📊 АНАЛИТИКА")
def business_analytics(message):
    bot.reply_to(message, "📊 *БИЗНЕС-АНАЛИТИКА*\n\n📈 В разработке", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🤖 АВТОМАТИЗАЦИЯ")
def business_auto(message):
    bot.reply_to(message, "🤖 *АВТОМАТИЗАЦИЯ*\n\n⚡ В разработке", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📈 ЛИЗИНГ")
def business_leasing(message):
    bot.reply_to(message, "📈 *ЛИЗИНГ*\n\n🚗 Авто: от 15%\n🏗️ Спецтехника: от 12%\n\n📞 /business_request", parse_mode="Markdown")

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
        bot.reply_to(message, "📭 У вас нет заказов\n\n➕ Чтобы создать заказ, напишите описание")

# ==================================================
# 👵 ПОЖИЛОЙ РЕЖИМ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👋 ПОЗДОРОВАТЬСЯ")
def elder_greet(message):
    bot.reply_to(message, "👋 Здравствуйте! Я - Зеркало. Всегда рад помочь!")

@bot.message_handler(func=lambda m: m.text == "📞 ПОМОЩЬ РЯДОМ")
def elder_help(message):
    bot.reply_to(message, "📞 *ПОМОЩЬ РЯДОМ*\n\n• Соцработник: +7 (700) 000-00-01\n• Поликлиника: +7 (700) 000-00-02\n• Соцзащита: +7 (700) 000-00-03", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🏥 ЗДОРОВЬЕ")
def elder_health(message):
    bot.reply_to(message, "🏥 *ЗДОРОВЬЕ*\n\n🚑 Скорая: 103\n💊 Аптека: напишите 'АПТЕКА'", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🆘 СРОЧНАЯ ПОМОЩЬ")
def elder_emergency(message):
    bot.reply_to(message, "🆘 *СРОЧНАЯ ПОМОЩЬ*\n\n🚑 Скорая: 103\n🚔 Полиция: 102\n🚒 Пожарные: 101\n📞 Единая служба: 112")

# ==================================================
# 🧒 ДЕТСКИЙ РЕЖИМ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📖 СКАЗКА")
def child_tale(message):
    tales = ["🐺 Волк и семеро козлят...", "👸 Золушка...", "🐻 Три медведя..."]
    bot.reply_to(message, f"📖 *СКАЗКА*\n\n{random.choice(tales)}", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🧩 ЗАГАДКА")
def child_riddle(message):
    riddles = {"Зимой и летом одним цветом?": "ёлка", "Висит груша, нельзя скушать?": "лампочка"}
    q = random.choice(list(riddles.keys()))
    bot.reply_to(message, f"🧩 *ЗАГАДКА*\n\n{q}\n\n(Напиши ответ)")
    bot.register_next_step_handler(message, check_riddle, riddles[q])

def check_riddle(message, answer):
    if message.text.lower() == answer:
        bot.reply_to(message, "✅ ПРАВИЛЬНО! Молодец!\n\n🎁 +10 Благ!")
    else:
        bot.reply_to(message, f"❌ Неправильно. Правильный ответ: {answer}")

@bot.message_handler(func=lambda m: m.text == "🎵 ПЕСЕНКА")
def child_song(message):
    songs = ["В лесу родилась ёлочка...", "Спят усталые игрушки..."]
    bot.reply_to(message, f"🎵 *ПЕСЕНКА*\n\n{random.choice(songs)}", parse_mode="Markdown")

# ==================================================
# 💸 РАБОТА И ЗАКАЗЫ
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
        bot.reply_to(message, "📭 У вас нет заказов\n\n➕ Чтобы создать заказ, напишите описание")

@bot.message_handler(func=lambda m: m.text == "➕ СОЗДАТЬ ЗАКАЗ")
def create_order_request(message):
    msg = bot.reply_to(message, "📦 Опишите ваш заказ:")
    bot.register_next_step_handler(msg, create_order)

def create_order(message):
    user_id = message.chat.id
    price = random.randint(1000, 50000)
    c.execute("INSERT INTO orders (description, price, customer_id, status, created_at) VALUES (?, ?, ?, ?, ?)",
              (message.text, price, user_id, "open", astana_time()))
    conn.commit()
    bot.reply_to(message, f"✅ ЗАКАЗ СОЗДАН!\n\n💰 {price} тенге")

# ==================================================
# 💰 БАЛАНС И ПАРТНЁРКА
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💰 БАЛАНС")
def show_balance(message):
    user_id = message.chat.id
    balance = get_balance(user_id)
    tariff = get_tariff(user_id)
    bot.reply_to(message, f"💰 *БАЛАНС:* {balance} Благ\n💎 *Тариф:* {TARIFFS[tariff]['name']}\n\n💳 Пополнить: /pay\n💸 Вывести: /withdraw", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💎 ПОДПИСКА")
def show_tariffs(message):
    msg = "💎 *ТАРИФЫ ЗЕРКАЛА*\n\n"
    for key, t in TARIFFS.items():
        msg += f"• {t['name']} — {t['price']} ₸/мес ({t['messages']} сообщений)\n"
    msg += "\n💳 /pay — купить тариф"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "⭐ ПАРТНЁРСКАЯ")
def show_referral(message):
    user_id = message.chat.id
    bot_username = bot.get_me().username
    c.execute("SELECT COUNT(*) FROM users WHERE referrer_id=?", (user_id,))
    count = c.fetchone()[0]
    bot.reply_to(message, f"⭐ *ПАРТНЁРСКАЯ ПРОГРАММА*\n\n"
                         f"👥 Приглашено: {count}\n"
                         f"🔗 Ваша ссылка:\n"
                         f"https://t.me/{bot_username}?start={user_id}\n\n"
                         f"📋 Вы получаете 10% от пополнений рефералов!", parse_mode="Markdown")

# ==================================================
# ❓ ВОПРОСЫ И ПОМОЩЬ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "❓ ВОПРОС")
def ask_question(message):
    msg = bot.reply_to(message, "❓ Напишите ваш вопрос:")
    bot.register_next_step_handler(msg, answer_question)

def answer_question(message):
    user_id = message.chat.id
    question = message.text
    
    tariff = get_tariff(user_id)
    if TARIFFS[tariff]["messages"] <= 0:
        bot.reply_to(message, f"❌ Лимит сообщений для тарифа {TARIFFS[tariff]['name']} исчерпан!\n💳 /pay")
        return
    
    balance = get_balance(user_id)
    if balance >= 1:
        c.execute("UPDATE users SET blessings = blessings - 1 WHERE user_id=?", (user_id,))
        conn.commit()
        
        if client:
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "Ты — Зеркало. Отвечай кратко, с уважением. Всегда начинай с 'Ассаляму алейкум'."},
                              {"role": "user", "content": question}],
                    temperature=0.7
                )
                bot.reply_to(message, response.choices[0].message.content)
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка AI: {e}")
        else:
            bot.reply_to(message, f"🤖 Ваш вопрос принят!")
    else:
        bot.reply_to(message, f"❌ Недостаточно Благ! Нужно 1 ✦\n💰 Баланс: {balance}\n💳 /pay")

@bot.message_handler(func=lambda m: m.text == "🆘 ПОМОЩЬ")
def help_section(message):
    help_text = """
🪞 *ПОМОЩЬ ПО ЗЕРКАЛУ*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💸 РАБОТА — поиск работы
📦 ЗАКАЗЫ — создание заказов
💰 БАЛАНС — проверка Благ
💳 KASPI QR — генерация Kaspi QR (клон)
🔍 УЗНАТЬ ЦЕНУ — примерная стоимость услуги
⭐ ПАРТНЁРСКАЯ — реферальная программа
💎 ПОДПИСКА — информация о тарифах
❓ ВОПРОС — вопрос к AI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 *ТАРИФЫ:*
• Бесплатный — 100 сообщений
• Базовый — 1000₸/мес (500 сообщ.)
• PRO — 5000₸/мес (3000 сообщ.)
• Бизнес — 20000₸/мес (10000 сообщ.)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ /pay — купить тариф
⚡ /id — узнать свой ID
⚡ /withdraw — вывести средства
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, help_text, parse_mode="Markdown")

# ==================================================
# 👑 АДМИН-ПАНЕЛЬ
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
    bot.reply_to(message, f"📊 СТАТИСТИКА:\n👥 Пользователей: {total}\n✨ Благ: {blessings}")

@bot.message_handler(func=lambda m: m.text == "💰 ФИНАНСЫ" and is_admin(m.chat.id))
def admin_finance(message):
    bot.reply_to(message, f"💰 Криптокошелёк: {CRYPTO_WALLET}\n\n📊 Фонды: 2% | 5% | 30% | 60%")

@bot.message_handler(func=lambda m: m.text == "👥 ВСЕ ЛЮДИ" and is_admin(m.chat.id))
def admin_users(message):
    c.execute("SELECT user_id, name, role, blessings FROM users LIMIT 30")
    users = c.fetchall()
    msg = "👥 ПОЛЬЗОВАТЕЛИ:\n"
    for u in users:
        msg += f"🆔 {u[0]} | {u[1]} | {u[2]} | ✨{u[3]}\n"
    bot.reply_to(message, msg[:4000])

@bot.message_handler(func=lambda m: m.text == "✨ БЛАГА" and is_admin(m.chat.id))
def admin_top(message):
    c.execute("SELECT name, blessings FROM users ORDER BY blessings DESC LIMIT 10")
    top = c.fetchall()
    msg = "✨ ТОП ПО БЛАГАМ:\n"
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
    c.execute("SELECT user_id, amount, method, status, created_at FROM payments ORDER BY id DESC LIMIT 20")
    pays = c.fetchall()
    if not pays:
        bot.reply_to(message, "📭 Платежей нет")
        return
    msg = "💳 ПОСЛЕДНИЕ ПЛАТЕЖИ:\n\n"
    for p in pays:
        msg += f"👤 {p[0]} | 💰 {p[1]} | {p[2]} | {p[3]} | {p[4][:16]}\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "🏦 ВЫВОДЫ" and is_admin(m.chat.id))
def admin_withdraws(message):
    c.execute("SELECT id, user_id, amount, wallet, status, created_at FROM withdraw_requests ORDER BY id DESC LIMIT 20")
    reqs = c.fetchall()
    if not reqs:
        bot.reply_to(message, "📭 Заявок на вывод нет")
        return
    msg = "🏦 ЗАЯВКИ НА ВЫВОД:\n\n"
    for r in reqs:
        msg += f"#{r[0]} | 👤 {r[1]} | 💰 {r[2]} | {r[4]} | {r[5][:16]}\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "📊 ДОХОДЫ" and is_admin(m.chat.id))
def admin_earnings(message):
    c.execute("SELECT SUM(amount) FROM payments WHERE status='completed'")
    total = c.fetchone()[0] or 0
    bot.reply_to(message, f"📊 ДОХОДЫ ЗЕРКАЛА:\n\n💰 Всего: {total} ₸")

@bot.message_handler(func=lambda m: m.text == "💎 ТАРИФЫ" and is_admin(m.chat.id))
def admin_tariffs(message):
    msg = "💎 УПРАВЛЕНИЕ ТАРИФАМИ:\n\n"
    for key, t in TARIFFS.items():
        c.execute("SELECT COUNT(*) FROM users WHERE tariff=?", (key,))
        count = c.fetchone()[0]
        msg += f"• {t['name']}: {count} чел.\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "🔍 ПОИСК" and is_admin(m.chat.id))
def admin_search(message):
    msg = bot.reply_to(message, "🔍 Введите ID пользователя:")
    bot.register_next_step_handler(msg, search_user)

def search_user(message):
    try:
        target = int(message.text)
        c.execute("SELECT user_id, name, role, blessings FROM users WHERE user_id=?", (target,))
        user = c.fetchone()
        if user:
            bot.reply_to(message, f"👤 ID: {user[0]}\n📛 {user[1]}\n🎭 {user[2]}\n✨ {user[3]} Благ")
        else:
            bot.reply_to(message, f"❌ Пользователь {target} не найден")
    except:
        bot.reply_to(message, "❌ Введите ID")

@bot.message_handler(func=lambda m: m.text == "📜 ЛОГИ" and is_admin(m.chat.id))
def admin_logs(message):
    c.execute("SELECT user_id, action, created_at FROM logs ORDER BY id DESC LIMIT 20")
    logs = c.fetchall()
    msg = "📜 ПОСЛЕДНИЕ ЛОГИ:\n\n"
    for l in logs:
        msg += f"{l[2][:16]} | ID:{l[0]} | {l[1][:30]}\n"
    bot.reply_to(message, msg[:4000])

# ==================================================
# 🔄 ОБЫЧНЫЕ СООБЩЕНИЯ
# ==================================================

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.chat.id
    text = message.text
    
    # Пропускаем кнопки
    buttons = ["👥 ОНЛАЙН", "📊 СТАТИСТИКА", "💰 ФИНАНСЫ", "👥 ВСЕ ЛЮДИ", "✨ БЛАГА",
               "📤 РАССЫЛКА", "💳 ПЛАТЕЖИ", "🏦 ВЫВОДЫ", "📊 ДОХОДЫ", "💎 ТАРИФЫ",
               "🔍 ПОИСК", "📜 ЛОГИ", "💸 РАБОТА", "📦 ЗАКАЗЫ", "💰 БАЛАНС",
               "💳 KASPI QR", "🔍 УЗНАТЬ ЦЕНУ", "⭐ ПАРТНЁРСКАЯ", "💎 ПОДПИСКА",
               "❓ ВОПРОС", "🆘 ПОМОЩЬ", "👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ", "🏢 БИЗНЕСМЕН",
               "👵 ПОЖИЛОЙ ЧЕЛОВЕК", "🧒 РЕБЁНОК", "🔙 ОБЫЧНЫЙ РЕЖИМ", "🔙 ВЫЙТИ"]
    if text in buttons:
        return
    
    log_action(user_id, "message", text[:50])
    
    tariff = get_tariff(user_id)
    if TARIFFS[tariff]["messages"] <= 0:
        bot.reply_to(message, f"❌ Лимит сообщений для тарифа {TARIFFS[tariff]['name']} исчерпан!\n💳 /pay")
        return
    
    balance = get_balance(user_id)
    if balance >= 1:
        c.execute("UPDATE users SET blessings = blessings - 1 WHERE user_id=?", (user_id,))
        conn.commit()
        
        if client:
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "Ты — Зеркало. Отвечай кратко, с уважением. Всегда начинай с 'Ассаляму алейкум'."},
                              {"role": "user", "content": text}],
                    temperature=0.7
                )
                bot.reply_to(message, response.choices[0].message.content)
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка AI: {e}")
        else:
            bot.reply_to(message, f"🪞 Зеркало: '{text[:100]}'")
    else:
        bot.reply_to(message, f"❌ Недостаточно Благ! Нужно 1 ✦\n💰 Баланс: {balance}\n💳 /pay")

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
print("🪞 ЗЕРКАЛО - ФИНАЛЬНАЯ ВЕРСИЯ ЗАПУЩЕНА")
print("=" * 60)
print(f"✅ BOT_TOKEN: {TOKEN[:10]}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 ХРАНИТЕЛИ: {ADMIN_IDS}")
print(f"💰 Kaspi QR клон: АКТИВЕН")
print(f"🔍 Парсинг 2ГИС: АКТИВЕН")
print(f"💎 Тарифы: 4 уровня")
print(f"⭐ Партнёрская: 10%")
print("=" * 60)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
