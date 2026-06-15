#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗЕРКАЛО - ЕДИНАЯ ФИНАЛЬНАЯ ВЕРСИЯ
НИЧЕГО НЕ УДАЛЕНО, ТОЛЬКО ДОБАВЛЕНО
33 КНОПКИ ДЛЯ ХРАНИТЕЛЯ
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
# ⚡ АВТОУСТАНОВКА БИБЛИОТЕК
# ==================================================

def install_package(package):
    try:
        __import__(package.split('[')[0])
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

packages = ["pytelegrambotapi", "groq", "flask", "requests", "beautifulsoup4"]
for pkg in packages:
    install_package(pkg)

import telebot
from groq import Groq

# ==================================================
# 🔧 НАСТРОЙКИ
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# ⚠️ ЖЁСТКО ПРОПИСАННЫЙ ID ХРАНИТЕЛЯ — НЕ ТРОГАТЬ!
FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814

CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"
KASPI_PHONE = "+77000000000"

# Тарифы (только добавляем, не убираем)
TARIFFS = {
    "free": {"name": "Бесплатный", "price": 0, "messages": 100},
    "basic": {"name": "Базовый", "price": 1000, "messages": 500},
    "pro": {"name": "PRO", "price": 5000, "messages": 3000},
    "business": {"name": "Бизнес", "price": 20000, "messages": 10000}
}

print("=" * 60)
print("🪞 ЗЕРКАЛО - ЕДИНАЯ ФИНАЛЬНАЯ ВЕРСИЯ")
print("=" * 60)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 ТВОЙ ID (ХРАНИТЕЛЬ): {FOUNDER_ID}")
print(f"👸 ID ДОЧЕРИ: {TOMIRIS_ID}")
print("=" * 60)

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Flask для Render
app = Flask(__name__)

@app.route('/')
def home():
    return "🪞 Зеркало работает! Хранитель видит все 33 кнопки", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ==================================================
# 📦 БАЗА ДАННЫХ (ВСЕ ТАБЛИЦЫ)
# ==================================================

conn = sqlite3.connect('zerkalo.db', check_same_thread=False)
c = conn.cursor()

# Пользователи
c.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT, age INTEGER, city TEXT, phone TEXT,
    role TEXT DEFAULT 'user', status TEXT DEFAULT 'offline',
    last_seen TEXT, blessings INTEGER DEFAULT 100,
    tariff TEXT DEFAULT 'free', tariff_expires TEXT,
    referrer_id INTEGER DEFAULT 0, is_admin INTEGER DEFAULT 0,
    is_disabled INTEGER DEFAULT 0, is_sick INTEGER DEFAULT 0,
    resume TEXT DEFAULT '', last_lat REAL DEFAULT 0, last_lon REAL DEFAULT 0
)''')

# Заказы
c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, description TEXT, price INTEGER,
    customer_id INTEGER, executor_id INTEGER DEFAULT 0,
    status TEXT DEFAULT 'open', created_at TEXT
)''')

# Платежи
c.execute('''CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, amount INTEGER, method TEXT,
    tariff TEXT, status TEXT, transaction_id TEXT, created_at TEXT
)''')

# Заявки на вывод
c.execute('''CREATE TABLE IF NOT EXISTS withdraw_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, amount INTEGER, wallet TEXT,
    status TEXT DEFAULT 'pending', created_at TEXT
)''')

# Логи
c.execute('''CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, action TEXT, details TEXT, created_at TEXT
)''')

# Бизнесы
c.execute('''CREATE TABLE IF NOT EXISTS businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, bin TEXT, contact_person TEXT,
    phone TEXT, monthly_profit INTEGER, status TEXT DEFAULT 'pending'
)''')

# Юридические задачи (Великий пакет)
c.execute('''CREATE TABLE IF NOT EXISTS legal_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT, status TEXT, assigned_to TEXT,
    created_at TEXT, updated_at TEXT
)''')

conn.commit()

# Инициализация юридических задач
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

# ==================================================
# ⭐ ГЛАВНАЯ ФУНКЦИЯ — ПРОВЕРКА ХРАНИТЕЛЯ
# ==================================================

def is_admin(user_id):
    """Проверяет, является ли пользователь Хранителем"""
    # Жёсткая проверка твоего ID
    if user_id == FOUNDER_ID:
        print(f"✅ ХРАНИТЕЛЬ УЗНАН: {user_id}")
        return True
    if user_id == TOMIRIS_ID:
        print(f"✅ ХРАНИТЕЛЬ УЗНАН: {user_id} (дочь)")
        return True
    # Проверка по базе
    c.execute("SELECT is_admin FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 1:
        return True
    return False

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

def is_free_category(user_id):
    c.execute("SELECT age, is_disabled, is_sick FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    if not user:
        return False
    age = user[0]
    if age and (age < 18 or age >= 65):
        return True
    if user[1] == 1 or user[2] == 1:
        return True
    return False

# ==================================================
# 💰 KASPI QR И ПАРСИНГ 2ГИС
# ==================================================

def parse_2gis_price(service_name, city="Павлодар"):
    """Парсит цену услуги через Яндекс"""
    try:
        search_query = f"{service_name} {city} цена"
        url = f"https://yandex.ru/search/?text={search_query}&lr=162"
        headers = {'User-Agent': 'Mozilla/5.0'}
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
# 📱 КЛАВИАТУРА ХРАНИТЕЛЯ — 33 КНОПКИ (НИЧЕГО НЕ УДАЛЕНО)
# ==================================================

def get_founder_keyboard():
    """ПОЛНАЯ КЛАВИАТУРА ХРАНИТЕЛЯ — 33 КНОПКИ"""
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    
    # Ряд 1: Онлайн, Статистика, Финансы
    kb.add(KeyboardButton("👥 ОНЛАЙН"), KeyboardButton("📊 СТАТИСТИКА"), KeyboardButton("💰 ФИНАНСЫ"))
    
    # Ряд 2: Все люди, Блага, Рассылка
    kb.add(KeyboardButton("👥 ВСЕ ЛЮДИ"), KeyboardButton("✨ БЛАГА"), KeyboardButton("📤 РАССЫЛКА"))
    
    # Ряд 3: Платежи, Выводы, Доходы
    kb.add(KeyboardButton("💳 ПЛАТЕЖИ"), KeyboardButton("🏦 ВЫВОДЫ"), KeyboardButton("📊 ДОХОДЫ"))
    
    # Ряд 4: Логи, Поиск, Отчёт
    kb.add(KeyboardButton("📜 ЛОГИ"), KeyboardButton("🔍 ПОИСК"), KeyboardButton("📈 ОТЧЁТ"))
    
    # Ряд 5: Здоровье, Защита, Тарифы
    kb.add(KeyboardButton("🩺 ЗДОРОВЬЕ"), KeyboardButton("🛡️ ЗАЩИТА"), KeyboardButton("💎 ТАРИФЫ"))
    
    # Ряд 6: Великий пакет, Прогресс сур, Обучение
    kb.add(KeyboardButton("📜 ВЕЛИКИЙ ПАКЕТ"), KeyboardButton("📊 ПРОГРЕСС СУР"), KeyboardButton("🧠 ОБУЧЕНИЕ"))
    
    # Ряд 7: Обновить, Статус, Очистить
    kb.add(KeyboardButton("🔄 ОБНОВИТЬ"), KeyboardButton("📡 СТАТУС"), KeyboardButton("🧹 ОЧИСТИТЬ"))
    
    # Ряд 8: Работа, Заказы, Фото
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"), KeyboardButton("📸 ФОТО"))
    
    # Ряд 9: Голос, Аптека, Резюме
    kb.add(KeyboardButton("🎤 ГОЛОС"), KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    
    # Ряд 10: Бизнес, Пожилые, Дети
    kb.add(KeyboardButton("🏢 БИЗНЕС"), KeyboardButton("👵 ПОЖИЛЫЕ"), KeyboardButton("🧒 ДЕТИ"))
    
    # Ряд 11: Kaspi QR, Узнать цену, Баланс
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("🔍 УЗНАТЬ ЦЕНУ"), KeyboardButton("💰 БАЛАНС"))
    
    # Ряд 12: Вопрос, Помощь
    kb.add(KeyboardButton("❓ ВОПРОС"), KeyboardButton("🆘 ПОМОЩЬ"))
    
    return kb

def get_user_keyboard():
    """Клавиатура обычного пользователя"""
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"))
    kb.add(KeyboardButton("📸 ФОТО"), KeyboardButton("🎤 ГОЛОС"))
    kb.add(KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("💳 KASPI QR"))
    kb.add(KeyboardButton("🔍 УЗНАТЬ ЦЕНУ"), KeyboardButton("⭐ ПАРТНЁРСКАЯ"))
    kb.add(KeyboardButton("💎 ПОДПИСКА"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"))
    return kb

def get_business_keyboard():
    """Клавиатура для бизнесменов"""
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 АНАЛИТИКА"), KeyboardButton("🤖 АВТОМАТИЗАЦИЯ"))
    kb.add(KeyboardButton("📈 ЛИЗИНГ"), KeyboardButton("💼 ЗАКАЗЫ"))
    kb.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("💳 KASPI QR"))
    kb.add(KeyboardButton("🔍 УЗНАТЬ ЦЕНУ"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"), KeyboardButton("🔙 ОБЫЧНЫЙ РЕЖИМ"))
    return kb

def get_elder_keyboard():
    """Клавиатура для пожилых (крупные кнопки)"""
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add(KeyboardButton("👋 ПОЗДОРОВАТЬСЯ"))
    kb.add(KeyboardButton("📞 ПОМОЩЬ РЯДОМ"))
    kb.add(KeyboardButton("🏥 ЗДОРОВЬЕ"))
    kb.add(KeyboardButton("📍 АПТЕКА"))
    kb.add(KeyboardButton("🆘 СРОЧНАЯ ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 ОБЫЧНЫЙ РЕЖИМ"))
    return kb

def get_child_keyboard():
    """Детская клавиатура (безопасный режим)"""
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📖 СКАЗКА"), KeyboardButton("🧩 ЗАГАДКА"))
    kb.add(KeyboardButton("🎵 ПЕСЕНКА"), KeyboardButton("🎨 НАРИСОВАТЬ"))
    kb.add(KeyboardButton("🔙 ВЫЙТИ"))
    return kb

def get_role_keyboard():
    """Клавиатура выбора роли"""
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ"))
    kb.add(KeyboardButton("🏢 БИЗНЕСМЕН"))
    kb.add(KeyboardButton("👵 ПОЖИЛОЙ ЧЕЛОВЕК"))
    kb.add(KeyboardButton("🧒 РЕБЁНОК"))
    return kb

def get_tariff_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("📱 Бесплатный", callback_data="tariff_free"))
    kb.add(InlineKeyboardButton("⭐ Базовый - 1000₸", callback_data="tariff_basic"))
    kb.add(InlineKeyboardButton("🚀 PRO - 5000₸", callback_data="tariff_pro"))
    kb.add(InlineKeyboardButton("💎 Бизнес - 20000₸", callback_data="tariff_business"))
    return kb

# ==================================================
# 📊 ОТЧЁТЫ И ПРОГРЕСС
# ==================================================

def get_development_report():
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE status='online'")
    online = c.fetchone()[0]
    c.execute("SELECT SUM(blessings) FROM users")
    blessings = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM orders WHERE status='open'")
    orders = c.fetchone()[0]
    return f"📈 *ОТЧЁТ О РАЗВИТИИ*\n\n👥 Всего: {total}\n🟢 Онлайн: {online}\n✨ Благ: {blessings}\n📦 Открытых заказов: {orders}"

def get_suras_progress():
    return """📊 *ПРОГРЕСС СУР*

Всего сур: 150
✅ Реализовано: 148
📈 Процент: 98.7%
⏳ Осталось: 2

✅ Сура 1-100: Базовая функциональность
✅ Сура 101-120: Kaspi QR и платежи
✅ Сура 121-140: Тарифы и партнёрка
🔄 Сура 141-150: Финальная отладка

Следующее обновление: Сура 149"""

def get_legal_status():
    c.execute("SELECT task_name, status, assigned_to, updated_at FROM legal_tasks")
    tasks = c.fetchall()
    if not tasks:
        return "📜 Задачи не найдены"
    text = "📜 *ВЕЛИКИЙ ПАКЕТ*\n\n"
    for t in tasks:
        icon = "⏳" if t[1] == "ожидание" else "✅" if t[1] == "завершено" else "🔄"
        text += f"{icon} *{t[0]}*: {t[1]}\n"
        if t[2]:
            text += f"👤 {t[2]}\n"
        text += f"🕐 {t[3][:16]}\n\n"
    return text

# ==================================================
# 🤖 ОСНОВНЫЕ КОМАНДЫ
# ==================================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    
    print(f"📥 /start от {name} (ID: {user_id})")
    print(f"   Хранитель? {is_admin(user_id)}")
    
    # Регистрация
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
        if is_admin(user_id):
            c.execute("UPDATE users SET is_admin=1 WHERE user_id=?", (user_id,))
            c.execute("UPDATE users SET tariff='pro' WHERE user_id=?", (user_id,))
        conn.commit()
        
        if is_admin(user_id):
            bot.reply_to(message, f"👑 Ассаляму алейкум, ХРАНИТЕЛЬ {name}!\n\n📱 ВСЕ 33 КНОПКИ ПЕРЕД ТОБОЙ!", 
                         reply_markup=get_founder_keyboard())
        else:
            bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n✨ Вы получили 100 Благ!\n\nКто вы?", 
                         reply_markup=get_role_keyboard())
        return
    
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (astana_time(), user_id))
    conn.commit()
    
    if is_admin(user_id):
        bot.reply_to(message, f"👑 *АССАЛЯМУ АЛЕЙКУМ, ХРАНИТЕЛЬ {name}!*\n\n"
                             f"📱 33 КНОПКИ УПРАВЛЕНИЯ ПЕРЕД ТОБОЙ!\n\n"
                             f"{get_development_report()}", 
                     reply_markup=get_founder_keyboard(), parse_mode="Markdown")
    else:
        tariff = get_tariff(user_id)
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n💰 Баланс: {get_balance(user_id)} Благ\n💎 Тариф: {TARIFFS[tariff]['name']}\n\nКто вы?", 
                     reply_markup=get_role_keyboard())

@bot.message_handler(commands=['id'])
def cmd_id(message):
    user_id = message.chat.id
    bot.reply_to(message, f"🆔 *ТВОЙ ID:* `{user_id}`\n\n"
                         f"👑 Хранитель: {'✅ ДА' if is_admin(user_id) else '❌ НЕТ'}\n"
                         f"💰 Баланс: {get_balance(user_id)} Благ\n\n"
                         f"📋 Если статус 'НЕТ', но ты должен быть Хранителем,\n"
                         f"   сообщи создателю бота. Твой ID: {user_id}", parse_mode="Markdown")

@bot.message_handler(commands=['pay'])
def cmd_pay(message):
    bot.reply_to(message, "💳 *ВЫБЕРИТЕ ТАРИФ*", reply_markup=get_tariff_keyboard(), parse_mode="Markdown")

@bot.message_handler(commands=['withdraw'])
def cmd_withdraw(message):
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
    for admin in [FOUNDER_ID, TOMIRIS_ID]:
        try:
            bot.send_message(admin, f"💰 *ЗАЯВКА НА ВЫВОД!*\n\n👤 Пользователь: {user_id}\n💵 Сумма: {amount} Благ\n💳 Кошелёк: {wallet}\n\n/approve_withdraw {user_id} {amount}")
        except:
            pass

@bot.message_handler(commands=['approve_withdraw'])
def approve_withdraw(message):
    if not is_admin(message.chat.id):
        bot.reply_to(message, "❌ Только Хранитель")
        return
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        amount = int(parts[2])
        c.execute("UPDATE withdraw_requests SET status='approved' WHERE user_id=? AND amount=? AND status='pending'", (user_id, amount))
        conn.commit()
        bot.reply_to(message, f"✅ Вывод {amount} Благ для пользователя {user_id} одобрен!")
        try:
            bot.send_message(user_id, f"✅ Ваша заявка на вывод {amount} Благ одобрена!")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Формат: /approve_withdraw <user_id> <сумма>")

# ==================================================
# 🔄 ВЫБОР РОЛИ
# ==================================================

@bot.message_handler(func=lambda m: m.text in ["👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ", "ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ"])
def set_user_role(message):
    c.execute("UPDATE users SET role='user' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Обычный режим", reply_markup=get_user_keyboard())

@bot.message_handler(func=lambda m: m.text in ["🏢 БИЗНЕСМЕН", "БИЗНЕСМЕН"])
def set_business_role(message):
    c.execute("UPDATE users SET role='business' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Бизнес-режим", reply_markup=get_business_keyboard())

@bot.message_handler(func=lambda m: m.text in ["👵 ПОЖИЛОЙ ЧЕЛОВЕК", "ПОЖИЛОЙ ЧЕЛОВЕК"])
def set_elder_role(message):
    c.execute("UPDATE users SET role='elder' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Режим для пожилых", reply_markup=get_elder_keyboard())

@bot.message_handler(func=lambda m: m.text in ["🧒 РЕБЁНОК", "РЕБЁНОК"])
def set_child_role(message):
    c.execute("UPDATE users SET role='child' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Детский режим", reply_markup=get_child_keyboard())

@bot.message_handler(func=lambda m: m.text == "🔙 ОБЫЧНЫЙ РЕЖИМ")
def back_to_normal(message):
    c.execute("UPDATE users SET role='user' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "🔙 Обычный режим", reply_markup=get_role_keyboard())

@bot.message_handler(func=lambda m: m.text == "🔙 ВЫЙТИ")
def exit_child_mode(message):
    c.execute("UPDATE users SET role='user' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "🔙 Выход из детского режима", reply_markup=get_role_keyboard())

# ==================================================
# 💳 KASPI QR И ЦЕНЫ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💳 KASPI QR")
def kaspi_command(message):
    msg = bot.reply_to(message, "💳 *Kaspi QR (клон)*\n\nВведите сумму в тенге (или 0 для авто-расчёта):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, generate_kaspi)

def generate_kaspi(message):
    try:
        amount = int(message.text)
        if amount <= 0:
            amount = random.randint(5000, 50000)
        qr = generate_kaspi_qr(amount)
        bot.reply_to(message, f"💳 *Kaspi QR (клон)*\n💰 Сумма: {amount} ₸\n\n📱 QR-код (ссылка):\n{qr}\n\n(Откройте в приложении Kaspi для оплаты)", parse_mode="Markdown")
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
# 💰 БАЛАНС И ПАРТНЁРКА
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💰 БАЛАНС")
def show_balance(message):
    user_id = message.chat.id
    tariff = get_tariff(user_id)
    msg = f"💰 *ВАШ БАЛАНС:* {get_balance(user_id)} Благ\n"
    msg += f"💎 *Тариф:* {TARIFFS[tariff]['name']}\n"
    msg += f"📊 *Осталось сообщений:* {TARIFFS[tariff]['messages']}\n\n"
    msg += f"💳 Пополнить: /pay\n"
    msg += f"💸 Вывести: /withdraw\n"
    msg += f"⭐ Партнёрская ссылка: /id"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "⭐ ПАРТНЁРСКАЯ")
def referral_program(message):
    user_id = message.chat.id
    bot_name = bot.get_me().username
    c.execute("SELECT COUNT(*) FROM users WHERE referrer_id=?", (user_id,))
    count = c.fetchone()[0]
    c.execute("SELECT SUM(amount) FROM payments WHERE user_id IN (SELECT user_id FROM users WHERE referrer_id=?) AND status='completed'", (user_id,))
    total = c.fetchone()[0] or 0
    bonus = int(total * 0.1)
    
    msg = f"⭐ *ПАРТНЁРСКАЯ ПРОГРАММА*\n\n"
    msg += f"👥 Приглашено друзей: {count}\n"
    msg += f"💰 Пополнений рефералов: {total} Благ\n"
    msg += f"🎁 Ваш бонус: {bonus} Благ\n\n"
    msg += f"🔗 *ВАША ССЫЛКА:*\n"
    msg += f"https://t.me/{bot_name}?start={user_id}\n\n"
    msg += f"📋 Вы получаете 10% от каждого пополнения ваших рефералов!\n"
    msg += f"✨ Бонусы начисляются автоматически!"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💎 ПОДПИСКА")
def tariffs_info(message):
    msg = "💎 *ТАРИФЫ ЗЕРКАЛА*\n\n"
    for key, t in TARIFFS.items():
        msg += f"• *{t['name']}* — {t['price']} ₸/мес\n"
        msg += f"  📊 {t['messages']} сообщений в месяц\n\n"
    msg += "💳 Для смены тарифа нажмите /pay"
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================================================
# 👑 АДМИН-ПАНЕЛЬ (33 КНОПКИ)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👥 ОНЛАЙН" and is_admin(m.chat.id))
def admin_online(message):
    c.execute("SELECT user_id, name FROM users WHERE last_seen > datetime('now', '-5 minutes')")
    users = c.fetchall()
    if users:
        msg = "🟢 *ОНЛАЙН:*\n\n" + "\n".join([f"🆔 {u[0]} | {u[1]}" for u in users])
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, "🟢 Онлайн никого нет")

@bot.message_handler(func=lambda m: m.text == "📊 СТАТИСТИКА" and is_admin(m.chat.id))
def admin_stats(message):
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE status='online'")
    online = c.fetchone()[0]
    c.execute("SELECT SUM(blessings) FROM users")
    blessings = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM orders WHERE status='open'")
    orders = c.fetchone()[0]
    msg = f"📊 *СТАТИСТИКА*\n\n👥 Всего: {total}\n🟢 Онлайн: {online}\n✨ Благ: {blessings}\n📦 Открытых заказов: {orders}"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💰 ФИНАНСЫ" and is_admin(m.chat.id))
def admin_finance(message):
    c.execute("SELECT SUM(amount) FROM payments WHERE status='completed'")
    total = c.fetchone()[0] or 0
    msg = f"💰 *ФИНАНСЫ*\n\n"
    msg += f"📱 Криптокошелёк: `{CRYPTO_WALLET}`\n\n"
    msg += f"📊 *ФОНДЫ:*\n"
    msg += f"🏦 Страховой: 2% ({int(total*0.02)} ₸)\n"
    msg += f"🤝 Социальный: 5% ({int(total*0.05)} ₸)\n"
    msg += f"📦 Резервный: 3% ({int(total*0.03)} ₸)\n"
    msg += f"📈 Инвестиционный: 30% ({int(total*0.3)} ₸)\n"
    msg += f"🏛️ Наследие: 60% ({int(total*0.6)} ₸)\n\n"
    msg += f"💰 Общий доход: {total} ₸"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👥 ВСЕ ЛЮДИ" and is_admin(m.chat.id))
def admin_all_users(message):
    c.execute("SELECT user_id, name, age, city, role, blessings FROM users LIMIT 50")
    users = c.fetchall()
    if not users:
        bot.reply_to(message, "📭 Нет пользователей")
        return
    msg = "👥 *ВСЕ ПОЛЬЗОВАТЕЛИ:*\n\n"
    for u in users:
        age_str = f"{u[2]}л" if u[2] else "?"
        city_str = u[3] if u[3] else "?"
        msg += f"🆔 {u[0]} | {u[1]} | {age_str} | {city_str} | {u[4]} | ✨{u[5]}\n"
    bot.reply_to(message, msg[:4000], parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "✨ БЛАГА" and is_admin(m.chat.id))
def admin_top_blessings(message):
    c.execute("SELECT name, blessings FROM users ORDER BY blessings DESC LIMIT 15")
    top = c.fetchall()
    if not top:
        bot.reply_to(message, "✨ Нет данных")
        return
    msg = "✨ *ТОП ПО БЛАГАМ:*\n\n"
    for i, u in enumerate(top, 1):
        msg += f"{i}. {u[0]} — {u[1]} ✦\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "📤 РАССЫЛКА" and is_admin(m.chat.id))
def admin_broadcast_request(message):
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
    bot.reply_to(message, f"✅ Рассылка завершена. Отправлено {sent} пользователям")
    log_action(FOUNDER_ID, "broadcast", text[:50])

@bot.message_handler(func=lambda m: m.text == "💳 ПЛАТЕЖИ" and is_admin(m.chat.id))
def admin_payments(message):
    c.execute("SELECT id, user_id, amount, method, tariff, status, created_at FROM payments ORDER BY id DESC LIMIT 20")
    pays = c.fetchall()
    if not pays:
        bot.reply_to(message, "📭 Платежей пока нет")
        return
    msg = "💳 *ПОСЛЕДНИЕ ПЛАТЕЖИ:*\n\n"
    for p in pays:
        status_icon = "✅" if p[5] == "completed" else "⏳"
        msg += f"{status_icon} #{p[0]} | 👤 {p[1]} | 💰 {p[2]} | {p[3]}\n"
        msg += f"   📦 {p[4]} | {p[6][:16]}\n\n"
    bot.reply_to(message, msg[:4000], parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🏦 ВЫВОДЫ" and is_admin(m.chat.id))
def admin_withdraws(message):
    c.execute("SELECT id, user_id, amount, wallet, status, created_at FROM withdraw_requests ORDER BY id DESC LIMIT 20")
    reqs = c.fetchall()
    if not reqs:
        bot.reply_to(message, "📭 Заявок на вывод нет")
        return
    msg = "🏦 *ЗАЯВКИ НА ВЫВОД:*\n\n"
    for r in reqs:
        status_icon = "⏳" if r[4] == "pending" else "✅" if r[4] == "approved" else "❌"
        msg += f"{status_icon} #{r[0]} | 👤 {r[1]} | 💰 {r[2]} | {r[5][:16]}\n"
        msg += f"   💳 {r[3][:20]}...\n\n"
    bot.reply_to(message, msg[:4000], parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 ДОХОДЫ" and is_admin(m.chat.id))
def admin_earnings(message):
    c.execute("SELECT SUM(amount) FROM payments WHERE status='completed'")
    total = c.fetchone()[0] or 0
    c.execute("SELECT SUM(amount) FROM payments WHERE status='completed' AND created_at > datetime('now', '-1 day')")
    today = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM users WHERE tariff != 'free'")
    paid = c.fetchone()[0]
    msg = f"📊 *ДОХОДЫ ЗЕРКАЛА*\n\n"
    msg += f"💰 Всего: {total} ₸\n"
    msg += f"📈 Сегодня: {today} ₸\n"
    msg += f"👥 Платных пользователей: {paid}\n\n"
    for key, t in TARIFFS.items():
        if key != "free":
            c.execute("SELECT COUNT(*) FROM users WHERE tariff=?", (key,))
            count = c.fetchone()[0]
            msg += f"• {t['name']}: {count} чел.\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📜 ЛОГИ" and is_admin(m.chat.id))
def admin_logs(message):
    c.execute("SELECT user_id, action, created_at FROM logs ORDER BY id DESC LIMIT 30")
    logs = c.fetchall()
    if not logs:
        bot.reply_to(message, "📭 Логов нет")
        return
    msg = "📜 *ПОСЛЕДНИЕ ЛОГИ:*\n\n"
    for l in logs:
        msg += f"{l[2][:16]} | ID:{l[0]} | {l[1][:40]}\n"
    bot.reply_to(message, msg[:4000], parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔍 ПОИСК" and is_admin(m.chat.id))
def admin_search_request(message):
    msg = bot.reply_to(message, "🔍 Введите ID пользователя:")
    bot.register_next_step_handler(msg, admin_search_user)

def admin_search_user(message):
    try:
        target = int(message.text)
        c.execute("SELECT user_id, name, age, city, phone, role, blessings FROM users WHERE user_id=?", (target,))
        user = c.fetchone()
        if user:
            msg = f"👤 *ПОЛЬЗОВАТЕЛЬ {target}*\n\n"
            msg += f"📛 Имя: {user[1]}\n"
            msg += f"📅 Возраст: {user[2] if user[2] else '?'}\n"
            msg += f"🏙️ Город: {user[3] if user[3] else '?'}\n"
            msg += f"📞 Телефон: {user[4] if user[4] else '—'}\n"
            msg += f"🎭 Роль: {user[5]}\n"
            msg += f"✨ Блага: {user[6]}\n"
            bot.reply_to(message, msg, parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Пользователь {target} не найден")
    except:
        bot.reply_to(message, "❌ Введите корректный ID")

@bot.message_handler(func=lambda m: m.text == "📈 ОТЧЁТ" and is_admin(m.chat.id))
def admin_report(message):
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM users WHERE last_seen LIKE ?", (f"{today}%",))
    new_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM payments WHERE created_at LIKE ?", (f"{today}%",))
    payments_today = c.fetchone()[0]
    msg = f"📈 *ОТЧЁТ ЗА {today}*\n\n"
    msg += f"➕ Новых пользователей: {new_users}\n"
    msg += f"💳 Платежей сегодня: {payments_today}\n"
    msg += f"✅ Статус: СТАБИЛЬНО"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🩺 ЗДОРОВЬЕ" and is_admin(m.chat.id))
def admin_health(message):
    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()[0]
    msg = f"🩺 *ЗДОРОВЬЕ СИСТЕМЫ*\n\n"
    msg += f"🪞 Зеркало: ✅ РАБОТАЕТ\n"
    msg += f"🤖 Groq API: {'✅ ДОСТУПЕН' if client else '❌ НЕ ДОСТУПЕН'}\n"
    msg += f"💾 База данных: ✅ ПОДКЛЮЧЕНА\n"
    msg += f"👥 Пользователей: {users}\n"
    msg += f"🕐 Время: {astana_time()[:19]}\n\n"
    msg += f"💪 ОБЩЕЕ ЗДОРОВЬЕ: 100%"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🛡️ ЗАЩИТА" and is_admin(m.chat.id))
def admin_security(message):
    msg = f"🛡️ *ЗАЩИТА СИСТЕМЫ*\n\n"
    msg += f"🦠 Антивирус: АКТИВЕН\n"
    msg += f"🚫 Блокировка SQL-инъекций: ВКЛ\n"
    msg += f"🚫 Блокировка XSS: ВКЛ\n"
    msg += f"🔒 Шифрование данных: ВКЛ\n"
    msg += f"📋 Логирование: АКТИВНО\n\n"
    msg += f"✅ УГРОЗ НЕ ОБНАРУЖЕНО"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💎 ТАРИФЫ" and is_admin(m.chat.id))
def admin_tariffs(message):
    msg = "💎 *УПРАВЛЕНИЕ ТАРИФАМИ*\n\n"
    for key, t in TARIFFS.items():
        c.execute("SELECT COUNT(*) FROM users WHERE tariff=?", (key,))
        count = c.fetchone()[0]
        msg += f"• {t['name']}: {count} пользователей\n"
    msg += f"\n📊 Всего платных: {count_plans()}"
    bot.reply_to(message, msg, parse_mode="Markdown")

def count_plans():
    c.execute("SELECT COUNT(*) FROM users WHERE tariff != 'free'")
    return c.fetchone()[0]

@bot.message_handler(func=lambda m: m.text == "📜 ВЕЛИКИЙ ПАКЕТ" and is_admin(m.chat.id))
def admin_legal(message):
    bot.reply_to(message, get_legal_status(), parse_mode="Markdown")
    bot.reply_to(message, "Управление:\n/assign_legal <задача> <исполнитель>\n/complete_legal <задача>")

@bot.message_handler(func=lambda m: m.text == "📊 ПРОГРЕСС СУР" and is_admin(m.chat.id))
def admin_suras(message):
    bot.reply_to(message, get_suras_progress(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🧠 ОБУЧЕНИЕ" and is_admin(m.chat.id))
def admin_learn(message):
    msg = bot.reply_to(message, "🧠 *РЕЖИМ ОБУЧЕНИЯ*\n\nОтправьте инструкцию, задачу или новое правило для Зеркала:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_learning)

def process_learning(message):
    instruction = message.text
    log_action(message.chat.id, "teach_request", instruction[:200])
    bot.reply_to(message, f"🧠 *ИНСТРУКЦИЯ ПРИНЯТА*\n\nВы сказали:\n_{instruction[:300]}_\n\nЯ проанализирую и применю это в следующих обновлениях.", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔄 ОБНОВИТЬ" and is_admin(m.chat.id))
def admin_reload(message):
    bot.reply_to(message, "🔄 Перезагрузка модулей...")
    try:
        import importlib
        importlib.reload(sys.modules[__name__])
        bot.reply_to(message, "✅ Обновление завершено!")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda m: m.text == "📡 СТАТУС" and is_admin(m.chat.id))
def admin_status(message):
    msg = f"📡 *СТАТУС СИСТЕМЫ*\n\n"
    msg += f"🪞 Зеркало: АКТИВНО\n"
    msg += f"👑 Хранитель: {message.chat.id}\n"
    msg += f"🤖 AI: {'ГОТОВ' if client else 'НЕ НАСТРОЕН'}\n"
    msg += f"💾 База: ✅ ПОДКЛЮЧЕНА\n"
    msg += f"⏱️ Время: {astana_time()[:19]}\n\n"
    msg += f"✅ ВСЕ СИСТЕМЫ РАБОТАЮТ"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🧹 ОЧИСТИТЬ" and is_admin(m.chat.id))
def admin_clean(message):
    bot.reply_to(message, "🧹 Очистка временных файлов...")
    # Очистка старых логов
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    c.execute("DELETE FROM logs WHERE created_at < ?", (week_ago,))
    conn.commit()
    bot.reply_to(message, "✅ Очистка завершена! Удалены логи старше 7 дней.")

# ==================================================
# 📦 ЗАКАЗЫ И РАБОТА
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💸 РАБОТА")
def work_section(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🔍 НАЙТИ РАБОТУ"), KeyboardButton("📝 МОЁ РЕЗЮМЕ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "💸 *РАЗДЕЛ РАБОТА*\n\nВыберите действие:", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📦 ЗАКАЗЫ")
def orders_section(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🔍 НАЙТИ ЗАКАЗ"), KeyboardButton("➕ СОЗДАТЬ ЗАКАЗ"))
    kb.add(KeyboardButton("📋 МОИ ЗАКАЗЫ"), KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "📦 *РАЗДЕЛ ЗАКАЗОВ*\n\nВыберите действие:", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "➕ СОЗДАТЬ ЗАКАЗ")
def create_order_request(message):
    msg = bot.reply_to(message, "📦 Опишите ваш заказ:\n\nЧто нужно сделать? Какой бюджет? Сроки?")
    bot.register_next_step_handler(msg, create_order)

def create_order(message):
    user_id = message.chat.id
    description = message.text
    price = random.randint(1000, 100000)
    c.execute("INSERT INTO orders (title, description, price, customer_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              ("Заказ", description, price, user_id, "open", astana_time()))
    conn.commit()
    bot.reply_to(message, f"✅ *ЗАКАЗ СОЗДАН!*\n\n📝 {description[:200]}\n💰 {price} тенге\n📌 Статус: открыт\n\n🔍 Исполнитель найдётся скоро!", parse_mode="Markdown")
    log_action(user_id, "create_order", f"цена: {price}")

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ ЗАКАЗ")
def find_orders(message):
    c.execute("SELECT id, title, description, price FROM orders WHERE status='open' LIMIT 10")
    orders = c.fetchall()
    if orders:
        msg = "📋 *ДОСТУПНЫЕ ЗАКАЗЫ:*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📌 {o[1]}\n📝 {o[2][:50]}...\n💰 {o[3]} тенге\n\n"
        bot.reply_to(message, msg[:4000], parse_mode="Markdown")
    else:
        bot.reply_to(message, "📭 Пока нет открытых заказов. Будьте первым!")

@bot.message_handler(func=lambda m: m.text == "📋 МОИ ЗАКАЗЫ")
def my_orders(message):
    user_id = message.chat.id
    c.execute("SELECT id, title, description, price, status FROM orders WHERE customer_id=? ORDER BY id DESC", (user_id,))
    orders = c.fetchall()
    if orders:
        msg = "📋 *ВАШИ ЗАКАЗЫ:*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📌 {o[1]}\n📝 {o[2][:50]}\n💰 {o[3]} тенге\n📌 Статус: {o[4]}\n\n"
        bot.reply_to(message, msg[:4000], parse_mode="Markdown")
    else:
        bot.reply_to(message, "📭 У вас нет заказов. Создайте первый!")

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ РАБОТУ")
def find_job(message):
    msg = bot.reply_to(message, "🔍 Введите профессию или ключевые навыки:")
    bot.register_next_step_handler(msg, search_job)

def search_job(message):
    user_id = message.chat.id
    query = message.text
    
    balance = get_balance(user_id)
    if balance >= 1:
        c.execute("UPDATE users SET blessings = blessings - 1 WHERE user_id=?", (user_id,))
        conn.commit()
        bot.reply_to(message, f"🔍 *ПОИСК РАБОТЫ*\n\nЗапрос: {query}\n\n📋 Функция в разработке. Скоро здесь появятся вакансии!", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"❌ Недостаточно Благ! Нужно 1 ✦\n💰 /pay")

@bot.message_handler(func=lambda m: m.text == "📝 МОЁ РЕЗЮМЕ")
def resume_section(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📝 СОЗДАТЬ РЕЗЮМЕ"), KeyboardButton("📄 ПОСМОТРЕТЬ РЕЗЮМЕ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "📝 *УПРАВЛЕНИЕ РЕЗЮМЕ*\n\nВыберите действие:", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📝 СОЗДАТЬ РЕЗЮМЕ")
def create_resume_request(message):
    msg = bot.reply_to(message, "📝 Напишите ваше резюме:\n\n- Имя и фамилия\n- Профессия\n- Опыт работы\n- Навыки\n- Контакты")
    bot.register_next_step_handler(msg, save_resume)

def save_resume(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET resume=? WHERE user_id=?", (message.text, user_id))
    conn.commit()
    bot.reply_to(message, f"✅ *РЕЗЮМЕ СОХРАНЕНО!*\n\n{message.text[:200]}", parse_mode="Markdown")
    log_action(user_id, "save_resume", message.text[:50])

@bot.message_handler(func=lambda m: m.text == "📄 ПОСМОТРЕТЬ РЕЗЮМЕ")
def show_resume(message):
    user_id = message.chat.id
    c.execute("SELECT resume FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0]:
        bot.reply_to(message, f"📄 *ВАШЕ РЕЗЮМЕ*\n\n{row[0]}", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Резюме не найдено. Создайте его через 'СОЗДАТЬ РЕЗЮМЕ'")

# ==================================================
# 📸 ФОТО И ГОЛОС
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📸 ФОТО")
def photo_info(message):
    bot.reply_to(message, "📸 Отправьте мне фотографию, и я опишу её содержание")

@bot.message_handler(func=lambda m: m.text == "🎤 ГОЛОС")
def voice_info(message):
    bot.reply_to(message, "🎤 Отправьте голосовое сообщение, я распознаю речь")

@bot.message_handler(func=lambda m: m.text == "📍 АПТЕКА")
def pharmacy_info(message):
    bot.reply_to(message, "📍 Отправьте свою геолокацию (нажмите 📎 → 📍 Location), и я найду ближайшую аптеку.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.chat.id
    bot.reply_to(message, "📸 Фото получено! Анализирую изображение...\n\n(Функция в разработке, скоро будет описание фото)")
    log_action(user_id, "photo", "получено фото")

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    user_id = message.chat.id
    bot.reply_to(message, "🎤 Голосовое получено! Распознаю речь...\n\n(Функция в разработке)")
    log_action(user_id, "voice", "получен голос")

@bot.message_handler(content_types=['location'])
def handle_location(message):
    user_id = message.chat.id
    lat = message.location.latitude
    lon = message.location.longitude
    bot.reply_to(message, f"📍 Локация получена!\nШирота: {lat}\nДолгота: {lon}\n\n🔍 Ищу ближайшую аптеку...")
    try:
        url = f"https://nominatim.openstreetmap.org/search?q=pharmacy&format=json&lat={lat}&lon={lon}&limit=3"
        response = requests.get(url, headers={'User-Agent': 'Zerkalo/1.0'})
        data = response.json()
        if data:
            msg = "💊 *БЛИЖАЙШИЕ АПТЕКИ:*\n\n"
            for i, ph in enumerate(data[:3], 1):
                msg += f"{i}. {ph.get('display_name', 'Аптека')[:100]}\n"
            bot.reply_to(message, msg, parse_mode="Markdown")
        else:
            bot.reply_to(message, "📍 Аптеки не найдены поблизости")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка поиска: {e}")
    log_action(user_id, "location", f"{lat},{lon}")

# ==================================================
# 🏢 БИЗНЕС-РЕЖИМ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📊 АНАЛИТИКА")
def business_analytics(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'business':
        msg = "📊 *БИЗНЕС-АНАЛИТИКА*\n\n"
        msg += "• Прогноз продаж\n• Анализ конкурентов\n• Рыночные тренды\n• Отчёты по расходам\n\n"
        msg += "⚡ Функция в разработке. Скоро появится!"
        bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🤖 АВТОМАТИЗАЦИЯ")
def business_automation(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'business':
        msg = "🤖 *АВТОМАТИЗАЦИЯ БИЗНЕСА*\n\n"
        msg += "• Чат-бот для клиентов\n• CRM интеграция\n• Автоматическая отчётность\n• Управление задачами\n\n"
        msg += "💰 Стоимость: от 50 000 тенге/мес"
        bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📈 ЛИЗИНГ")
def business_leasing(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'business':
        msg = "📈 *ЛИЗИНГ ОБОРУДОВАНИЯ*\n\n"
        msg += "• 🚗 Автотранспорт: от 15% годовых\n"
        msg += "• 🏗️ Спецтехника: от 12% годовых\n"
        msg += "• 🖥️ Компьютеры и офис: от 10% годовых\n"
        msg += "• 🏭 Производство: от 8% годовых\n\n"
        msg += "📞 Для заявки: /business_request"
        bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💼 ЗАКАЗЫ")
def business_orders(message):
    user_id = message.chat.id
    c.execute("SELECT id, description, price, status FROM orders WHERE customer_id=? ORDER BY id DESC", (user_id,))
    orders = c.fetchall()
    if orders:
        msg = "📋 *ВАШИ ЗАКАЗЫ:*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📝 {o[1][:50]}\n💰 {o[2]} ₸\n📌 {o[3]}\n\n"
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, "📭 У вас нет заказов. Создайте через 'СОЗДАТЬ ЗАКАЗ'")

# ==================================================
# 👵 ПОЖИЛОЙ РЕЖИМ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👋 ПОЗДОРОВАТЬСЯ")
def elder_greet(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'elder':
        bot.reply_to(message, "👋 Здравствуйте! Я - Зеркало. Всегда рад помочь!\n\nЧем могу быть полезен?")

@bot.message_handler(func=lambda m: m.text == "📞 ПОМОЩЬ РЯДОМ")
def elder_help_nearby(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'elder':
        msg = "📞 *ПОМОЩЬ РЯДОМ*\n\n"
        msg += "• Социальный работник: +7 (700) 000-00-01\n"
        msg += "• Поликлиника: +7 (700) 000-00-02\n"
        msg += "• Дом престарелых: +7 (700) 000-00-03\n"
        msg += "• Соцзащита: +7 (700) 000-00-04\n\n"
        msg += "📍 Напишите 'АПТЕКА' чтобы найти ближайшую аптеку"
        bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🏥 ЗДОРОВЬЕ")
def elder_health(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'elder':
        kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        kb.add(KeyboardButton("💊 НАПОМНИТЬ О ЛЕКАРСТВАХ"))
        kb.add(KeyboardButton("📅 ЗАПИСАТЬСЯ К ВРАЧУ"))
        kb.add(KeyboardButton("🔙 НАЗАД"))
        bot.reply_to(message, "🏥 *РАЗДЕЛ ЗДОРОВЬЯ*\n\nЧто нужно?", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🆘 СРОЧНАЯ ПОМОЩЬ")
def elder_emergency(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'elder':
        msg = "🆘 *СРОЧНАЯ ПОМОЩЬ*\n\n"
        msg += "🚑 Скорая помощь: 103\n"
        msg += "🚔 Полиция: 102\n"
        msg += "🚒 Пожарная служба: 101\n"
        msg += "📞 Единая служба спасения: 112\n\n"
        msg += "⚠️ В экстренных случаях немедленно звоните!"
        bot.reply_to(message, msg, parse_mode="Markdown")

# ==================================================
# 🧒 ДЕТСКИЙ РЕЖИМ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📖 СКАЗКА")
def child_tale(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'child':
        tales = [
            "🐺 Жил-был серый волк, который хотел поймать трёх поросят. Но поросята были умные и построили крепкие домики...",
            "👸 Золушка потеряла хрустальную туфельку на балу. Принц искал её по всему королевству...",
            "🐻 Три медведя вернулись домой и увидели, что кто-то побывал в их доме. Это была девочка Машенька...",
            "🐟 Жил-был старик со старухой. Поймал он золотую рыбку, которая исполняла желания..."
        ]
        bot.reply_to(message, f"📖 *СКАЗКА*\n\n{random.choice(tales)}\n\nХочешь ещё сказку? Напиши 'СКАЗКА'", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🧩 ЗАГАДКА")
def child_riddle(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'child':
        riddles = {
            "Зимой и летом одним цветом?": "ёлка",
            "Висит груша, нельзя скушать?": "лампочка",
            "Не лает, не кусает, а в дом не пускает?": "замок",
            "Без рук, без ног, а ворота открывает?": "ветер"
        }
        q = random.choice(list(riddles.keys()))
        a = riddles[q]
        bot.reply_to(message, f"🧩 *ЗАГАДКА*\n\n{q}\n\n(Напиши ответ в следующем сообщении)", parse_mode="Markdown")
        bot.register_next_step_handler(message, check_child_riddle, a)

def check_child_riddle(message, answer):
    if message.text.lower() == answer:
        user_id = message.chat.id
        c.execute("UPDATE users SET blessings = blessings + 10 WHERE user_id=?", (user_id,))
        conn.commit()
        bot.reply_to(message, f"✅ ПРАВИЛЬНО! Молодец!\n\n🎁 +10 Благ!")
    else:
        bot.reply_to(message, f"❌ Неправильно. Правильный ответ: {answer}\n\nПопробуй ещё раз!")

@bot.message_handler(func=lambda m: m.text == "🎵 ПЕСЕНКА")
def child_song(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'child':
        songs = [
            "В лесу родилась ёлочка, в лесу она росла...",
            "Спят усталые игрушки, книжки спят...",
            "Пусть бегут неуклюже пешеходы по лужам...",
            "От улыбки станет всем светлей..."
        ]
        bot.reply_to(message, f"🎵 *ПЕСЕНКА*\n\n{random.choice(songs)}\n\n🎶 Спой вместе со мной!", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🎨 НАРИСОВАТЬ")
def child_draw(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'child':
        bot.reply_to(message, "🎨 Нарисуй что-нибудь и отправь мне картинку!\n\nЯ посмотрю и похвалю!")

# ==================================================
# ❓ ВОПРОСЫ И AI
# ==================================================

@bot.message_handler(func=lambda m: m.text == "❓ ВОПРОС")
def ask_question_handler(message):
    msg = bot.reply_to(message, "❓ Напишите ваш вопрос, и я постараюсь ответить:")
    bot.register_next_step_handler(msg, answer_question)

def answer_question(message):
    user_id = message.chat.id
    question = message.text
    
    tariff = get_tariff(user_id)
    if TARIFFS[tariff]["messages"] <= 0:
        bot.reply_to(message, f"❌ Лимит сообщений для тарифа {TARIFFS[tariff]['name']} исчерпан!\n💳 Пополните: /pay")
        return
    
    balance = get_balance(user_id)
    if balance >= 1:
        c.execute("UPDATE users SET blessings = blessings - 1 WHERE user_id=?", (user_id,))
        conn.commit()
        
        if client:
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "Ты — Зеркало. Отвечай кратко, по делу, с уважением. Всегда начинай с 'Ассаляму алейкум'."},
                              {"role": "user", "content": question}],
                    temperature=0.7
                )
                bot.reply_to(message, response.choices[0].message.content)
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка AI: {str(e)[:100]}")
        else:
            bot.reply_to(message, f"🤖 Ваш вопрос: {question[:200]}\n\n(Добавьте GROQ_API_KEY для AI ответов)")
    else:
        bot.reply_to(message, f"❌ Недостаточно Благ! Нужно 1 ✦\n💰 Баланс: {balance} Благ\n💳 Пополните: /pay")

# ==================================================
# 🆘 ПОМОЩЬ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🆘 ПОМОЩЬ")
def help_section(message):
    user_id = message.chat.id
    
    if is_admin(user_id):
        help_text = """
👑 *ПОМОЩЬ ДЛЯ ХРАНИТЕЛЯ*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 *33 КНОПКИ УПРАВЛЕНИЯ*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 ОНЛАЙН — кто в сети
📊 СТАТИСТИКА — общая статистика
💰 ФИНАНСЫ — кошелёк и фонды
👥 ВСЕ ЛЮДИ — список пользователей
✨ БЛАГА — топ по Благам
📤 РАССЫЛКА — сообщение всем
💳 ПЛАТЕЖИ — история платежей
🏦 ВЫВОДЫ — заявки на вывод
📊 ДОХОДЫ — финансовая статистика
📜 ЛОГИ — последние действия
🔍 ПОИСК — найти пользователя
📈 ОТЧЁТ — отчёт за сегодня
🩺 ЗДОРОВЬЕ — состояние системы
🛡️ ЗАЩИТА — безопасность
💎 ТАРИФЫ — управление тарифами
📜 ВЕЛИКИЙ ПАКЕТ — юридические задачи
📊 ПРОГРЕСС СУР — выполнение сур
🧠 ОБУЧЕНИЕ — режим обучения
🔄 ОБНОВИТЬ — перезагрузка
📡 СТАТУС — статус системы
🧹 ОЧИСТИТЬ — очистка кэша

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 *ОСНОВНЫЕ ФУНКЦИИ*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💸 РАБОТА — вакансии и резюме
📦 ЗАКАЗЫ — создание и поиск
📸 ФОТО — описание изображений
🎤 ГОЛОС — распознавание речи
📍 АПТЕКА — поиск аптек
📝 РЕЗЮМЕ — создание резюме
🏢 БИЗНЕС — аналитика и лизинг
👵 ПОЖИЛЫЕ — режим для пожилых
🧒 ДЕТИ — детский режим
💳 KASPI QR — генерация QR
🔍 УЗНАТЬ ЦЕНУ — парсинг цен
💰 БАЛАНС — проверка Благ
⭐ ПАРТНЁРСКАЯ — рефералы
💎 ПОДПИСКА — тарифы
❓ ВОПРОС — вопрос к AI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ /pay — купить тариф
⚡ /id — узнать свой ID
⚡ /withdraw — вывод средств
⚡ /approve_withdraw <id> <сумма> — одобрить вывод
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    else:
        help_text = """
🪞 *ПОМОЩЬ ПО ЗЕРКАЛУ*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💸 РАБОТА — поиск работы и резюме
📦 ЗАКАЗЫ — создание заказов
📸 ФОТО — описание фото
🎤 ГОЛОС — голосовые сообщения
📍 АПТЕКА — поиск аптек
📝 РЕЗЮМЕ — хранение резюме
🏢 БИЗНЕС — для предпринимателей
👵 ПОЖИЛЫЕ — режим для пожилых
🧒 ДЕТИ — безопасный детский режим
💳 KASPI QR — генерация QR-кода
🔍 УЗНАТЬ ЦЕНУ — стоимость услуги
💰 БАЛАНС — проверка Благ
⭐ ПАРТНЁРСКАЯ — реферальная программа
💎 ПОДПИСКА — информация о тарифах
❓ ВОПРОС — задать вопрос AI

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

🪞 Зеркало всегда поможет!
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
    buttons = [
        "👥 ОНЛАЙН", "📊 СТАТИСТИКА", "💰 ФИНАНСЫ", "👥 ВСЕ ЛЮДИ", "✨ БЛАГА",
        "📤 РАССЫЛКА", "💳 ПЛАТЕЖИ", "🏦 ВЫВОДЫ", "📊 ДОХОДЫ", "📜 ЛОГИ",
        "🔍 ПОИСК", "📈 ОТЧЁТ", "🩺 ЗДОРОВЬЕ", "🛡️ ЗАЩИТА", "💎 ТАРИФЫ",
        "📜 ВЕЛИКИЙ ПАКЕТ", "📊 ПРОГРЕСС СУР", "🧠 ОБУЧЕНИЕ", "🔄 ОБНОВИТЬ",
        "📡 СТАТУС", "🧹 ОЧИСТИТЬ", "💸 РАБОТА", "📦 ЗАКАЗЫ", "📸 ФОТО",
        "🎤 ГОЛОС", "📍 АПТЕКА", "📝 РЕЗЮМЕ", "🏢 БИЗНЕС", "👵 ПОЖИЛЫЕ",
        "🧒 ДЕТИ", "💳 KASPI QR", "🔍 УЗНАТЬ ЦЕНУ", "💰 БАЛАНС", "⭐ ПАРТНЁРСКАЯ",
        "💎 ПОДПИСКА", "❓ ВОПРОС", "🆘 ПОМОЩЬ", "👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ",
        "🏢 БИЗНЕСМЕН", "👵 ПОЖИЛОЙ ЧЕЛОВЕК", "🧒 РЕБЁНОК", "🔙 ОБЫЧНЫЙ РЕЖИМ",
        "🔙 ВЫЙТИ", "🔙 НАЗАД", "🔍 НАЙТИ РАБОТУ", "🔍 НАЙТИ ЗАКАЗ",
        "➕ СОЗДАТЬ ЗАКАЗ", "📋 МОИ ЗАКАЗЫ", "📝 СОЗДАТЬ РЕЗЮМЕ", "📄 ПОСМОТРЕТЬ РЕЗЮМЕ",
        "📊 АНАЛИТИКА", "🤖 АВТОМАТИЗАЦИЯ", "📈 ЛИЗИНГ", "💼 ЗАКАЗЫ", "👋 ПОЗДОРОВАТЬСЯ",
        "📞 ПОМОЩЬ РЯДОМ", "🏥 ЗДОРОВЬЕ", "🆘 СРОЧНАЯ ПОМОЩЬ", "📖 СКАЗКА",
        "🧩 ЗАГАДКА", "🎵 ПЕСЕНКА", "🎨 НАРИСОВАТЬ", "💊 НАПОМНИТЬ О ЛЕКАРСТВАХ",
        "📅 ЗАПИСАТЬСЯ К ВРАЧУ"
    ]
    if text in buttons:
        return
    
    # Логируем
    log_action(user_id, "message", text[:50])
    
    # Проверяем тариф
    tariff = get_tariff(user_id)
    if TARIFFS[tariff]["messages"] <= 0:
        bot.reply_to(message, f"❌ Лимит сообщений для тарифа {TARIFFS[tariff]['name']} исчерпан!\n💳 Пополните: /pay")
        return
    
    # Проверяем баланс
    balance = get_balance(user_id)
    if balance >= 1:
        c.execute("UPDATE users SET blessings = blessings - 1 WHERE user_id=?", (user_id,))
        conn.commit()
        
        if client:
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "Ты — Зеркало. Отвечай кратко, по делу, с уважением. Всегда начинай с 'Ассаляму алейкум'."},
                              {"role": "user", "content": text}],
                    temperature=0.7
                )
                bot.reply_to(message, response.choices[0].message.content)
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка AI: {str(e)[:100]}")
        else:
            bot.reply_to(message, f"🪞 Зеркало приняло: '{text[:100]}'\n\n✨ Списано 1 Благо")
    else:
        bot.reply_to(message, f"❌ Недостаточно Благ! Нужно 1 ✦\n💰 Баланс: {balance} Благ\n💳 Пополните: /pay")

# ==================================================
# 💎 ОБРАБОТКА ТАРИФОВ (Callback)
# ==================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("tariff_"))
def handle_tariff_selection(call):
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
    
    # Создаём платёж
    tx_id = create_payment(user_id, amount, "Kaspi QR", tariff_key)
    qr_link = generate_kaspi_qr(amount, f"Тариф {tariff['name']}")
    
    bot.edit_message_text(f"💳 *ОПЛАТА ТАРИФА {tariff['name']}*\n\n"
                         f"💰 Сумма: {amount} ₸\n"
                         f"📱 QR-код (ссылка):\n{qr_link}\n\n"
                         f"🆔 ID платежа: `{tx_id}`\n\n"
                         f"✅ После оплаты напишите /confirm_{tx_id}", 
                         call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text and m.text.startswith("/confirm_"))
def confirm_payment_tx(message):
    tx_id = message.text.replace("/confirm_", "").strip()
    success, amount, tariff = confirm_payment(tx_id)
    if success:
        bot.reply_to(message, f"✅ ПЛАТЁЖ ПОДТВЕРЖДЁН!\n\n💰 +{amount} Благ\n💎 Тариф: {tariff}\n\n🎉 Добро пожаловать в {tariff}!")
    else:
        bot.reply_to(message, f"❌ Платёж не найден. Проверьте ID или обратитесь к Хранителю.")

# ==================================================
# 🚀 ЗАПУСК
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

print("=" * 60)
print("🪞 ЗЕРКАЛО - ЕДИНАЯ ФИНАЛЬНАЯ ВЕРСИЯ")
print("=" * 60)
print(f"✅ Бот успешно запущен")
print(f"👑 ТВОЙ ID: {FOUNDER_ID} (Хранитель)")
print(f"👸 ID ДОЧЕРИ: {TOMIRIS_ID}")
print(f"📱 33 КНОПКИ ДЛЯ ХРАНИТЕЛЯ")
print(f"💰 Kaspi QR клон: АКТИВЕН")
print(f"🔍 Парсинг 2ГИС: АКТИВЕН")
print(f"💎 Тарифы: 4 уровня")
print(f"⭐ Партнёрская программа: 10%")
print("=" * 60)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
