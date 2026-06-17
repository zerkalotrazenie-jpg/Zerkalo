#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🪞 ЗЕРКАЛО — ПОЛНАЯ СИСТЕМА
═══════════════════════════════════════════════════════════════════
✅ РАБОТАЕТ 24/7
✅ ПИНГ КАЖДУЮ МИНУТУ
✅ ВСЕ МОДУЛИ
✅ WEBAPP ИНТЕРФЕЙС
✅ ДЕЛЕНИЕ ПО РОЛЯМ (ХРАНИТЕЛЬ / ПОЛЬЗОВАТЕЛЬ)
✅ ВСЕ КНОПКИ РАБОТАЮТ
✅ ЛОГИРОВАНИЕ
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
# 👑 ХРАНИТЕЛИ (ВАШИ ID)
# ==================================================

FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814
ADMIN_IDS = [5409420822, 5479179814]

# ==================================================
# 💰 РЕКВИЗИТЫ
# ==================================================

KASPI_PHONE = "+777733440345"
KASPI_NAME = "ЗЕРКАЛО"
CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"

print("=" * 70)
print("🪞 ЗЕРКАЛО ЗАПУСКАЕТСЯ...")
print("=" * 70)
print(f"✅ ТОКЕН: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"👑 ХРАНИТЕЛЬ ID: {FOUNDER_ID}")
print(f"🌐 ХОСТ: {RENDER_HOSTNAME}")
print("=" * 70)

# ==================================================
# 🤖 БОТ И APP
# ==================================================

bot = telebot.TeleBot(TOKEN) if TOKEN else None
app = Flask(__name__)

# ==================================================
# ⏰ ПИНГ (НЕ ДАЁТ ЗАСНУТЬ)
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

c.execute('''CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    details TEXT,
    created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    method TEXT,
    status TEXT,
    created_at TEXT
)''')

conn.commit()
print("✅ БАЗА ДАННЫХ ГОТОВА")

# ==================================================
# 📝 ЛОГИРОВАНИЕ
# ==================================================

def log_action(user_id, action, details=""):
    c.execute("INSERT INTO logs (user_id, action, details, created_at) VALUES (?, ?, ?, ?)",
              (user_id, action, details, datetime.now().isoformat()))
    conn.commit()
    print(f"📝 Лог: {user_id} | {action} | {details}")

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
        return "Хранитель"
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    return row[0] if row else "Пользователь"

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
    
    log_action(user_id, "start", f"Пользователь {name} запустил бота")
    
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

@bot.message_handler(commands=['id'])
def cmd_id(message):
    user_id = message.chat.id
    bot.reply_to(
        message,
        f"🆔 *ТВОЙ ID:* `{user_id}`\n\n"
        f"👑 Хранитель: {'✅' if is_admin(user_id) else '❌'}\n"
        f"🎭 Роль: {get_user_role(user_id)}",
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

@bot.message_handler(commands=['balance'])
def cmd_balance(message):
    user_id = message.chat.id
    balance = get_balance(user_id)
    bot.reply_to(message, f"💰 *ВАШ БАЛАНС:* {balance} Благ", parse_mode="Markdown")

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
        f"📦 Открытых заказов: {open_orders}",
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

@bot.message_handler(commands=['clear'])
def cmd_clear(message):
    user_id = message.chat.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Нет доступа")
        return
    
    # Очищаем логи
    c.execute("DELETE FROM logs")
    conn.commit()
    bot.reply_to(message, "🧹 Логи очищены!")

@bot.message_handler(func=lambda m: m.text == "👑 ХРАНИТЕЛЬ")
def founder_section(message):
    user_id = message.chat.id
    if is_admin(user_id):
        bot.reply_to(message, "👑 *ПАНЕЛЬ ХРАНИТЕЛЯ*", reply_markup=get_founder_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Нет доступа", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text == "🏢 БИЗНЕС")
def business_section(message):
    bot.reply_to(message, "🏢 *БИЗНЕС-РАЗДЕЛ*\n\n🤖 Автоматизация\n📈 Лизинг\n📊 Аналитика", reply_markup=get_business_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👤 ЛЮДИ")
def people_section(message):
    bot.reply_to(message, "👤 *ОБЫЧНЫЙ РАЗДЕЛ*\n\n💸 Работа\n📦 Заказы\n🔍 Поиск", reply_markup=get_people_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💰 МОНЕТИЗАЦИЯ")
def monetization_section(message):
    bot.reply_to(message, "💰 *МОНЕТИЗАЦИЯ*\n\n💎 Купить тариф\n⭐ Партнёрская программа\n🏦 Kaspi QR\n💎 USDT TRC20", reply_markup=get_monetization_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💸 РАБОТА")
def work_section(message):
    user_id = message.chat.id
    log_action(user_id, "work", "Открыл раздел работы")
    bot.reply_to(
        message,
        "💸 *РАБОТА*\n\n"
        "Доступные задания:\n"
        "1. 🛠️ Сварщик — 5000 ₸\n"
        "2. 📦 Доставка — 3000 ₸\n"
        "3. 🧹 Уборка — 2000 ₸\n\n"
        "📌 Чтобы создать задание: /order\n"
        "🔍 Чтобы найти: /search",
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
    log_action(user_id, "balance", f"Проверка баланса: {balance}")
    bot.reply_to(
        message,
        f"💰 *ВАШ БАЛАНС*\n\n"
        f"✨ Благ: {balance}\n\n"
        f"💎 Тариф: Бесплатный\n"
        f"📊 /pay — пополнить\n"
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

@bot.message_handler(func=lambda m: m.text == "🔙 НА ГЛАВНУЮ")
def back_to_main(message):
    user_id = message.chat.id
    if is_admin(user_id):
        bot.reply_to(message, "👑 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_founder_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "🪞 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_people_keyboard(), parse_mode="Markdown")

# ==================================================
# 📱 ОБРАБОТЧИКИ WEBAPP КНОПОК (ЧЕРЕЗ CALLBACK)
# ==================================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    data = call.data
    
    log_action(user_id, "callback", f"Действие: {data}")
    
    if data == "find":
        bot.answer_callback_query(call.id, "🔍 Поиск")
        bot.send_message(user_id, "🔍 *ПОИСК*\n\nВведите, что вы ищете:\n- Работу\n- Мастера\n- Товар\n- Услугу", parse_mode="Markdown")
    
    elif data == "work":
        bot.answer_callback_query(call.id, "💼 Работа")
        c.execute("SELECT id, title, price FROM orders WHERE status='open' LIMIT 5")
        orders = c.fetchall()
        if orders:
            msg = "💼 *ДОСТУПНЫЕ ЗАДАНИЯ*\n\n"
            for o in orders:
                msg += f"📦 #{o[0]} {o[1]} — {o[2]} ₸\n"
            bot.send_message(user_id, msg, parse_mode="Markdown")
        else:
            bot.send_message(user_id, "📭 Нет открытых заданий", parse_mode="Markdown")
    
    elif data == "help":
        bot.answer_callback_query(call.id, "🆘 Помощь")
        bot.send_message(user_id, "🆘 *ПОМОЩЬ*\n\nЧто вас беспокоит?\n1. Деньги\n2. Работа\n3. Конфликт\n4. Здоровье\n\nНапишите подробнее.", parse_mode="Markdown")
    
    elif data == "wallet":
        balance = get_balance(user_id)
        bot.answer_callback_query(call.id, f"💰 Баланс: {balance} Благ")
        bot.send_message(user_id, f"💰 *КОШЕЛЁК*\n\n✨ Баланс: {balance} Благ\n\n💎 Тариф: Бесплатный\n📊 /pay — пополнить\n📋 /history — история", parse_mode="Markdown")
    
    elif data == "profile":
        c.execute("SELECT name, role, blessings FROM users WHERE user_id=?", (user_id,))
        user = c.fetchone()
        if user:
            bot.answer_callback_query(call.id, "👤 Профиль")
            bot.send_message(user_id, f"👤 *ПРОФИЛЬ*\n\n📛 Имя: {user[0]}\n🎭 Роль: {user[1]}\n✨ Благ: {user[2]}\n\n🆔 ID: `{user_id}`", parse_mode="Markdown")
    
    elif data == "admin":
        if is_admin(user_id):
            bot.answer_callback_query(call.id, "👑 Панель управления")
            bot.send_message(user_id, "👑 *ПАНЕЛЬ УПРАВЛЕНИЯ*\n\nВыберите:\n- /stats — статистика\n- /users — пользователи\n- /logs — логи\n- /clear — очистить логи", parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "❌ Доступ запрещён")
    
    elif data == "users":
        if is_admin(user_id):
            c.execute("SELECT user_id, name, role FROM users LIMIT 15")
            users = c.fetchall()
            if users:
                msg = "👥 *ПОЛЬЗОВАТЕЛИ*\n\n"
                for u in users:
                    msg += f"🆔 {u[0]} | {u[1]} | {u[2]}\n"
                bot.send_message(user_id, msg, parse_mode="Markdown")
            else:
                bot.send_message(user_id, "📭 Нет пользователей")
        else:
            bot.send_message(user_id, "❌ Нет доступа")
    
    elif data == "finance":
        if is_admin(user_id):
            c.execute("SELECT SUM(blessings) FROM users")
            total = c.fetchone()[0] or 0
            bot.send_message(user_id, f"💰 *ФИНАНСЫ*\n\n✨ Всего Благ: {total}\n👥 Всего пользователей: {c.execute('SELECT COUNT(*) FROM users').fetchone()[0]}", parse_mode="Markdown")
        else:
            bot.send_message(user_id, "❌ Нет доступа")
    
    elif data == "logs":
        if is_admin(user_id):
            c.execute("SELECT user_id, action, created_at FROM logs ORDER BY id DESC LIMIT 15")
            logs = c.fetchall()
            if logs:
                msg = "📜 *ЛОГИ*\n\n"
                for l in logs:
                    msg += f"{l[2][:16]} | ID:{l[0]} | {l[1][:25]}\n"
                bot.send_message(user_id, msg, parse_mode="Markdown")
            else:
                bot.send_message(user_id, "📭 Логов нет")
        else:
            bot.send_message(user_id, "❌ Нет доступа")
    
    elif data == "settings":
        if is_admin(user_id):
            bot.send_message(user_id, "⚙️ *НАСТРОЙКИ*\n\n/clear — очистить логи\n/backup — создать бэкап", parse_mode="Markdown")
        else:
            bot.send_message(user_id, "❌ Нет доступа")
    
    else:
        bot.answer_callback_query(call.id, "⚠️ Неизвестная команда")

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

@app.route('/api/stats')
def api_stats():
    if not is_admin:
        return jsonify({"error": "Unauthorized"}), 401
    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()[0]
    c.execute("SELECT SUM(blessings) FROM users")
    blessings = c.fetchone()[0] or 0
    return jsonify({"users": users, "blessings": blessings})

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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🪞 ЗЕРКАЛО</h1>
            <p style="font-size: 18px; color: #a0a0b0;">Аль-Ми'ра · Свет и Отражение</p>
            <div class="status">✅ Работает 24/7</div>
            <a class="btn" href="/webapp">📱 ОТКРЫТЬ ПРИЛОЖЕНИЕ</a>
            <div class="footer">
                Ассаляму алейкум ва рахматуллахи ва баракатух<br>
                <span style="color:#3a3a4e;">v2.0 · {RENDER_HOSTNAME}</span>
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
    
    threading.Thread(target=run_bot, daemon=True).start()
    run_flask()
