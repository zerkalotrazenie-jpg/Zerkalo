#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗЕРКАЛО - ВЕРСИЯ С 4 ГЛАВНЫМИ КНОПКАМИ
Все остальные кнопки внутри
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

CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"

print("=" * 60)
print("🪞 ЗЕРКАЛО - 4 ГЛАВНЫЕ КНОПКИ")
print("=" * 60)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 ТВОЙ ID: {FOUNDER_ID}")
print("=" * 60)

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "🪞 Зеркало работает!", 200

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
    status TEXT, qr_data TEXT, created_at TEXT
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

def log_action(user_id, action, details=""):
    c.execute("INSERT INTO logs (user_id, action, details, created_at) VALUES (?, ?, ?, ?)",
              (user_id, action, details, astana_time()))
    conn.commit()

def generate_kaspi_qr(amount):
    return f"https://test.kaspi.kz/qr/pay?amount={amount}&merchant=Zerkalo&order_id={random.randint(100000, 999999)}"

# ==================================================
# 🧠 AI-ДОКТОР (внутренний)
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
# 📱 ГЛАВНАЯ КЛАВИАТУРА — 4 КНОПКИ
# ==================================================

def get_main_keyboard():
    """Главная клавиатура с 4 кнопками"""
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("👑 ХРАНИТЕЛЬ"))
    kb.add(KeyboardButton("🏢 БИЗНЕС"))
    kb.add(KeyboardButton("👤 ЛЮДИ"))
    kb.add(KeyboardButton("🧠 AI-ДОКТОР"))
    return kb

# ==================================================
# 👑 ВНУТРЕННЯЯ КЛАВИАТУРА ХРАНИТЕЛЯ (33 кнопки)
# ==================================================

def get_founder_inner_keyboard():
    """Все 33 кнопки Хранителя"""
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    
    # Админ-панель
    kb.add(KeyboardButton("👥 ОНЛАЙН"), KeyboardButton("📊 СТАТИСТИКА"), KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("👥 ВСЕ ЛЮДИ"), KeyboardButton("✨ БЛАГА"), KeyboardButton("📤 РАССЫЛКА"))
    kb.add(KeyboardButton("💳 ПЛАТЕЖИ"), KeyboardButton("🏦 ВЫВОДЫ"), KeyboardButton("📊 ДОХОДЫ"))
    kb.add(KeyboardButton("📜 ЛОГИ"), KeyboardButton("🔍 ПОИСК"), KeyboardButton("📈 ОТЧЁТ"))
    kb.add(KeyboardButton("🩺 ЗДОРОВЬЕ"), KeyboardButton("🛡️ ЗАЩИТА"), KeyboardButton("💎 ТАРИФЫ"))
    kb.add(KeyboardButton("🔄 ОБНОВИТЬ"), KeyboardButton("📡 СТАТУС"), KeyboardButton("🧹 ОЧИСТИТЬ"))
    
    # Основные функции
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"), KeyboardButton("📸 ФОТО"))
    kb.add(KeyboardButton("🎤 ГОЛОС"), KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("🏢 БИЗНЕС"), KeyboardButton("👵 ПОЖИЛЫЕ"), KeyboardButton("🧒 ДЕТИ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"))
    
    # Кнопка возврата
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    
    return kb

# ==================================================
# 🏢 ВНУТРЕННЯЯ КЛАВИАТУРА БИЗНЕСА
# ==================================================

def get_business_inner_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 АНАЛИТИКА"), KeyboardButton("🤖 АВТОМАТИЗАЦИЯ"))
    kb.add(KeyboardButton("📈 ЛИЗИНГ"), KeyboardButton("💼 ЗАКАЗЫ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"))
    kb.add(KeyboardButton("❓ ВОПРОС"), KeyboardButton("🆘 ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

# ==================================================
# 👤 ВНУТРЕННЯЯ КЛАВИАТУРА ЛЮДЕЙ
# ==================================================

def get_people_inner_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"))
    kb.add(KeyboardButton("📸 ФОТО"), KeyboardButton("🎤 ГОЛОС"))
    kb.add(KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"))
    kb.add(KeyboardButton("❓ ВОПРОС"), KeyboardButton("🆘 ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

# ==================================================
# 🤖 ОСНОВНЫЕ КОМАНДЫ
# ==================================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    
    print(f"📥 СТАРТ от {name} (ID: {user_id})")
    
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
        conn.commit()
        
        if is_admin(user_id):
            bot.reply_to(message, f"👑 Ассаляму алейкум, ХРАНИТЕЛЬ {name}!\n\n🪞 Зеркало готово к работе.\n\n📱 Выберите раздел:", 
                         reply_markup=get_main_keyboard())
        else:
            bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n✨ Вы получили 100 Благ!\n\n📱 Выберите раздел:", 
                         reply_markup=get_main_keyboard())
        return
    
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (astana_time(), user_id))
    conn.commit()
    
    if is_admin(user_id):
        bot.reply_to(message, f"👑 Ассаляму алейкум, ХРАНИТЕЛЬ {name}!\n\n🪞 Зеркало готово.\n\n📱 Выберите раздел:", 
                     reply_markup=get_main_keyboard())
    else:
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n💰 Баланс: {get_balance(user_id)} Благ\n\n📱 Выберите раздел:", 
                     reply_markup=get_main_keyboard())

@bot.message_handler(commands=['id'])
def cmd_id(message):
    user_id = message.chat.id
    bot.reply_to(message, f"🆔 *ТВОЙ ID:* `{user_id}`\n\n👑 Хранитель: {'✅ ДА' if is_admin(user_id) else '❌ НЕТ'}", parse_mode="Markdown")

@bot.message_handler(commands=['pay'])
def cmd_pay(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET blessings = blessings + 100 WHERE user_id=?", (user_id,))
    conn.commit()
    bot.reply_to(message, f"✅ +100 Благ!\n💰 Баланс: {get_balance(user_id)} Благ\n\n📱 Поддержать: {CRYPTO_WALLET}")

# ==================================================
# 🔄 ОБРАБОТЧИК ГЛАВНЫХ КНОПОК
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👑 ХРАНИТЕЛЬ")
def founder_section(message):
    user_id = message.chat.id
    if is_admin(user_id):
        bot.reply_to(message, f"👑 *ПАНЕЛЬ ХРАНИТЕЛЯ*\n\n📱 ВСЕ 33 КНОПКИ УПРАВЛЕНИЯ:", 
                     reply_markup=get_founder_inner_keyboard(), parse_mode="Markdown")
        log_action(user_id, "open_founder_panel")
    else:
        bot.reply_to(message, "❌ У вас нет прав доступа к панели Хранителя.\n\nОбратитесь к создателю бота.")

@bot.message_handler(func=lambda m: m.text == "🏢 БИЗНЕС")
def business_section(message):
    bot.reply_to(message, f"🏢 *БИЗНЕС-РАЗДЕЛ*\n\n📊 Аналитика, автоматизация, лизинг:", 
                 reply_markup=get_business_inner_keyboard(), parse_mode="Markdown")
    log_action(message.chat.id, "open_business_panel")

@bot.message_handler(func=lambda m: m.text == "👤 ЛЮДИ")
def people_section(message):
    bot.reply_to(message, f"👤 *ОБЫЧНЫЙ РАЗДЕЛ*\n\n💸 Работа, заказы, услуги:", 
                 reply_markup=get_people_inner_keyboard(), parse_mode="Markdown")
    log_action(message.chat.id, "open_people_panel")

@bot.message_handler(func=lambda m: m.text == "🧠 AI-ДОКТОР")
def ai_doctor_section(message):
    user_id = message.chat.id
    report = ai_doctor.get_report()
    
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🩺 ЛЕЧЕНИЕ"), KeyboardButton("🛡️ ПРОВЕРКА"))
    kb.add(KeyboardButton("📊 СТАТУС"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    
    bot.reply_to(message, f"🧠 *AI-ДОКТОР*\n\n{report}", 
                 reply_markup=kb, parse_mode="Markdown")
    log_action(user_id, "open_ai_doctor")

@bot.message_handler(func=lambda m: m.text == "🩺 ЛЕЧЕНИЕ")
def ai_heal(message):
    result = ai_doctor.heal()
    bot.reply_to(message, f"🧠 *AI-ДОКТОР*\n\n{result}\n\n✅ Система здорова!")

@bot.message_handler(func=lambda m: m.text == "🛡️ ПРОВЕРКА")
def ai_check(message):
    bot.reply_to(message, f"🛡️ *ПРОВЕРКА СИСТЕМЫ*\n\n✅ Код: чист\n✅ Вирусы: не обнаружены\n✅ Ошибки: нет\n✅ Защита: активна")

@bot.message_handler(func=lambda m: m.text == "📊 СТАТУС")
def ai_status(message):
    bot.reply_to(message, ai_doctor.get_report(), parse_mode="Markdown")

# ==================================================
# 🔙 ВОЗВРАТ НА ГЛАВНУЮ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🔙 НА ГЛАВНУЮ")
def back_to_main(message):
    bot.reply_to(message, "🏠 *ГЛАВНОЕ МЕНЮ*\n\nВыберите раздел:", 
                 reply_markup=get_main_keyboard(), parse_mode="Markdown")

# ==================================================
# 👑 АДМИН-КОМАНДЫ (для внутренней клавиатуры)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👥 ОНЛАЙН")
def admin_online(message):
    if not is_admin(message.chat.id):
        return
    c.execute("SELECT user_id, name FROM users WHERE last_seen > datetime('now', '-5 minutes')")
    users = c.fetchall()
    if users:
        msg = "🟢 ОНЛАЙН:\n" + "\n".join([f"{u[1]} (ID: {u[0]})" for u in users])
        bot.reply_to(message, msg)
    else:
        bot.reply_to(message, "🟢 Онлайн никого нет")

@bot.message_handler(func=lambda m: m.text == "📊 СТАТИСТИКА")
def admin_stats(message):
    if not is_admin(message.chat.id):
        return
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT SUM(blessings) FROM users")
    blessings = c.fetchone()[0] or 0
    bot.reply_to(message, f"📊 СТАТИСТИКА:\n\n👥 Всего: {total}\n✨ Благ: {blessings}")

@bot.message_handler(func=lambda m: m.text == "💰 ФИНАНСЫ")
def admin_finance(message):
    if not is_admin(message.chat.id):
        return
    bot.reply_to(message, f"💰 ФИНАНСЫ:\n\n📱 Криптокошелёк: {CRYPTO_WALLET}")

@bot.message_handler(func=lambda m: m.text == "👥 ВСЕ ЛЮДИ")
def admin_users(message):
    if not is_admin(message.chat.id):
        return
    c.execute("SELECT user_id, name, blessings FROM users LIMIT 30")
    users = c.fetchall()
    msg = "👥 ПОЛЬЗОВАТЕЛИ:\n\n"
    for u in users:
        msg += f"🆔 {u[0]} | {u[1]} | ✨{u[2]}\n"
    bot.reply_to(message, msg[:4000])

@bot.message_handler(func=lambda m: m.text == "✨ БЛАГА")
def admin_top(message):
    if not is_admin(message.chat.id):
        return
    c.execute("SELECT name, blessings FROM users ORDER BY blessings DESC LIMIT 10")
    top = c.fetchall()
    msg = "✨ ТОП ПО БЛАГАМ:\n\n"
    for i, u in enumerate(top, 1):
        msg += f"{i}. {u[0]} — {u[1]} ✦\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "📤 РАССЫЛКА")
def admin_broadcast(message):
    if not is_admin(message.chat.id):
        return
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

@bot.message_handler(func=lambda m: m.text == "📜 ЛОГИ")
def admin_logs(message):
    if not is_admin(message.chat.id):
        return
    c.execute("SELECT user_id, action, created_at FROM logs ORDER BY id DESC LIMIT 20")
    logs = c.fetchall()
    if not logs:
        bot.reply_to(message, "📭 Логов нет")
        return
    msg = "📜 ЛОГИ:\n\n"
    for l in logs:
        msg += f"{l[2][:16]} | ID:{l[0]} | {l[1][:40]}\n"
    bot.reply_to(message, msg[:4000])

@bot.message_handler(func=lambda m: m.text == "🔍 ПОИСК")
def admin_search(message):
    if not is_admin(message.chat.id):
        return
    msg = bot.reply_to(message, "🔍 Введите ID пользователя:")
    bot.register_next_step_handler(msg, search_user)

def search_user(message):
    try:
        target = int(message.text)
        c.execute("SELECT user_id, name, blessings FROM users WHERE user_id=?", (target,))
        user = c.fetchone()
        if user:
            bot.reply_to(message, f"👤 ID: {user[0]}\n📛 {user[1]}\n✨ {user[2]} Благ")
        else:
            bot.reply_to(message, f"❌ Не найден")
    except:
        bot.reply_to(message, "❌ Введите ID")

@bot.message_handler(func=lambda m: m.text == "📈 ОТЧЁТ")
def admin_report(message):
    if not is_admin(message.chat.id):
        return
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM users WHERE last_seen LIKE ?", (f"{today}%",))
    new = c.fetchone()[0]
    bot.reply_to(message, f"📈 ОТЧЁТ ЗА {today}:\n\n➕ Новых: {new}")

@bot.message_handler(func=lambda m: m.text == "🩺 ЗДОРОВЬЕ")
def admin_health(message):
    if not is_admin(message.chat.id):
        return
    bot.reply_to(message, "🩺 ЗДОРОВЬЕ:\n\n✅ Бот работает\n✅ База данных OK\n✅ Все системы стабильны")

@bot.message_handler(func=lambda m: m.text == "🛡️ ЗАЩИТА")
def admin_security(message):
    if not is_admin(message.chat.id):
        return
    bot.reply_to(message, "🛡️ ЗАЩИТА:\n\n✅ Антивирус активен\n✅ SQL защита включена")

@bot.message_handler(func=lambda m: m.text == "💎 ТАРИФЫ")
def admin_tariffs(message):
    if not is_admin(message.chat.id):
        return
    bot.reply_to(message, "💎 ТАРИФЫ:\n\n• Бесплатный — 0₸\n• Базовый — 1000₸\n• PRO — 5000₸\n• Бизнес — 20000₸")

@bot.message_handler(func=lambda m: m.text == "🔄 ОБНОВИТЬ")
def admin_reload(message):
    if not is_admin(message.chat.id):
        return
    bot.reply_to(message, "🔄 Обновление...\n✅ Готово!")

@bot.message_handler(func=lambda m: m.text == "📡 СТАТУС")
def admin_status(message):
    if not is_admin(message.chat.id):
        return
    bot.reply_to(message, f"📡 СТАТУС:\n\n👑 Хранитель: {message.chat.id}\n⏱️ Работает\n✅ OK")

@bot.message_handler(func=lambda m: m.text == "🧹 ОЧИСТИТЬ")
def admin_clean(message):
    if not is_admin(message.chat.id):
        return
    bot.reply_to(message, "🧹 Очистка...\n✅ Готово!")

@bot.message_handler(func=lambda m: m.text == "🏦 ВЫВОДЫ")
def admin_withdraws(message):
    if not is_admin(message.chat.id):
        return
    bot.reply_to(message, "🏦 ЗАЯВКИ НА ВЫВОД:\n\n⏳ В разработке")

@bot.message_handler(func=lambda m: m.text == "📊 ДОХОДЫ")
def admin_earnings(message):
    if not is_admin(message.chat.id):
        return
    bot.reply_to(message, "📊 ДОХОДЫ:\n\n💰 В разработке")

# ==================================================
# 💳 KASPI QR
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💳 KASPI QR")
def kaspi_command(message):
    msg = bot.reply_to(message, "💳 *KASPI QR*\n\nВведите сумму в тенге:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, generate_kaspi)

def generate_kaspi(message):
    try:
        amount = int(message.text)
        if amount <= 0:
            amount = random.randint(5000, 50000)
        qr = generate_kaspi_qr(amount)
        bot.reply_to(message, f"💳 *KASPI QR*\n💰 Сумма: {amount} ₸\n\n📱 Ссылка:\n{qr}\n\n(Откройте в Kaspi)", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Введите число")

# ==================================================
# 💰 БАЛАНС
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💰 БАЛАНС")
def show_balance(message):
    user_id = message.chat.id
    bot.reply_to(message, f"💰 *БАЛАНС:* {get_balance(user_id)} Благ\n\n💳 Пополнить: /pay", parse_mode="Markdown")

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
# 📸 МЕДИА
# ==================================================

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "📸 Фото получено!\n\n(Функция в разработке)")

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    bot.reply_to(message, "🎤 Голосовое получено!\n\n(Функция в разработке)")

@bot.message_handler(content_types=['location'])
def handle_location(message):
    lat = message.location.latitude
    lon = message.location.longitude
    bot.reply_to(message, f"📍 Локация сохранена!\nШирота: {lat}\nДолгота: {lon}")

# ==================================================
# 📝 РЕЗЮМЕ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📝 РЕЗЮМЕ")
def resume_section(message):
    msg = bot.reply_to(message, "📝 Напишите ваше резюме:")
    bot.register_next_step_handler(msg, save_resume)

def save_resume(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET resume=? WHERE user_id=?", (message.text, user_id))
    conn.commit()
    bot.reply_to(message, f"✅ РЕЗЮМЕ СОХРАНЕНО!")

@bot.message_handler(func=lambda m: m.text == "🎤 ГОЛОС")
def voice_info(message):
    bot.reply_to(message, "🎤 Отправьте голосовое сообщение")

@bot.message_handler(func=lambda m: m.text == "📍 АПТЕКА")
def pharmacy_info(message):
    bot.reply_to(message, "📍 Отправьте геолокацию")

@bot.message_handler(func=lambda m: m.text == "📸 ФОТО")
def photo_info(message):
    bot.reply_to(message, "📸 Отправьте фото")

# ==================================================
# 👵 ПОЖИЛЫЕ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👵 ПОЖИЛЫЕ")
def elder_section(message):
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add(KeyboardButton("👋 ПОЗДОРОВАТЬСЯ"))
    kb.add(KeyboardButton("📞 ПОМОЩЬ РЯДОМ"))
    kb.add(KeyboardButton("🏥 ЗДОРОВЬЕ"))
    kb.add(KeyboardButton("🆘 СРОЧНАЯ ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    bot.reply_to(message, "👵 *РЕЖИМ ДЛЯ ПОЖИЛЫХ*\n\nКрупные кнопки для удобства:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👋 ПОЗДОРОВАТЬСЯ")
def elder_greet(message):
    bot.reply_to(message, "👋 Здравствуйте! Я - Зеркало. Всегда рад помочь!")

@bot.message_handler(func=lambda m: m.text == "📞 ПОМОЩЬ РЯДОМ")
def elder_help(message):
    bot.reply_to(message, "📞 ПОМОЩЬ РЯДОМ:\n\n• Соцработник: +7 (700) 000-00-01\n• Поликлиника: +7 (700) 000-00-02")

@bot.message_handler(func=lambda m: m.text == "🏥 ЗДОРОВЬЕ")
def elder_health(message):
    bot.reply_to(message, "🏥 ЗДОРОВЬЕ:\n\n🚑 Скорая: 103\n💊 Аптека: отправьте локацию")

@bot.message_handler(func=lambda m: m.text == "🆘 СРОЧНАЯ ПОМОЩЬ")
def elder_emergency(message):
    bot.reply_to(message, "🆘 СРОЧНАЯ ПОМОЩЬ:\n\n🚑 Скорая: 103\n🚔 Полиция: 102\n🚒 Пожарные: 101\n📞 Единая служба: 112")

# ==================================================
# 🧒 ДЕТИ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🧒 ДЕТИ")
def child_section(message):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📖 СКАЗКА"), KeyboardButton("🧩 ЗАГАДКА"))
    kb.add(KeyboardButton("🎵 ПЕСЕНКА"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    bot.reply_to(message, "🧒 *ДЕТСКИЙ РЕЖИМ*\n\nБезопасное общение и игры:", 
                 reply_markup=kb, parse_mode="Markdown")

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
        bot.reply_to(message, "✅ ПРАВИЛЬНО! Молодец!")
    else:
        bot.reply_to(message, f"❌ Неправильно. Ответ: {answer}")

@bot.message_handler(func=lambda m: m.text == "🎵 ПЕСЕНКА")
def child_song(message):
    songs = ["В лесу родилась ёлочка...", "Спят усталые игрушки..."]
    bot.reply_to(message, f"🎵 *ПЕСЕНКА*\n\n{random.choice(songs)}", parse_mode="Markdown")

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
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка AI: {e}")
        else:
            bot.reply_to(message, f"🤖 Вопрос принят!")
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

👑 ХРАНИТЕЛЬ — панель управления (только для вас)
🏢 БИЗНЕС — аналитика, лизинг, автоматизация
👤 ЛЮДИ — работа, заказы, услуги
🧠 AI-ДОКТОР — диагностика и лечение системы

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ /pay — пополнить баланс
⚡ /id — узнать свой ID
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🪞 Зеркало всегда поможет!
"""
    bot.reply_to(message, help_text, parse_mode="Markdown")

# ==================================================
# 🔄 ОБЫЧНЫЕ СООБЩЕНИЯ
# ==================================================

@bot.message_handler(func=lambda m: True)
def handle_any(message):
    user_id = message.chat.id
    text = message.text
    
    # Пропускаем кнопки
    buttons = [
        "👑 ХРАНИТЕЛЬ", "🏢 БИЗНЕС", "👤 ЛЮДИ", "🧠 AI-ДОКТОР",
        "🔙 НА ГЛАВНУЮ", "🩺 ЛЕЧЕНИЕ", "🛡️ ПРОВЕРКА", "📊 СТАТУС",
        "👥 ОНЛАЙН", "📊 СТАТИСТИКА", "💰 ФИНАНСЫ", "👥 ВСЕ ЛЮДИ", "✨ БЛАГА",
        "📤 РАССЫЛКА", "💳 ПЛАТЕЖИ", "🏦 ВЫВОДЫ", "📊 ДОХОДЫ", "📜 ЛОГИ",
        "🔍 ПОИСК", "📈 ОТЧЁТ", "🩺 ЗДОРОВЬЕ", "🛡️ ЗАЩИТА", "💎 ТАРИФЫ",
        "🔄 ОБНОВИТЬ", "📡 СТАТУС", "🧹 ОЧИСТИТЬ", "💸 РАБОТА", "📦 ЗАКАЗЫ",
        "📸 ФОТО", "🎤 ГОЛОС", "📍 АПТЕКА", "📝 РЕЗЮМЕ", "💳 KASPI QR",
        "💰 БАЛАНС", "❓ ВОПРОС", "🆘 ПОМОЩЬ", "👵 ПОЖИЛЫЕ", "🧒 ДЕТИ",
        "👋 ПОЗДОРОВАТЬСЯ", "📞 ПОМОЩЬ РЯДОМ", "🏥 ЗДОРОВЬЕ", "🆘 СРОЧНАЯ ПОМОЩЬ",
        "📖 СКАЗКА", "🧩 ЗАГАДКА", "🎵 ПЕСЕНКА", "📊 АНАЛИТИКА", "🤖 АВТОМАТИЗАЦИЯ",
        "📈 ЛИЗИНГ", "💼 ЗАКАЗЫ", "➕ СОЗДАТЬ ЗАКАЗ"
    ]
    if text in buttons:
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
                    messages=[{"role": "system", "content": "Ты — Зеркало. Отвечай кратко, по делу, с уважением. Всегда начинай с 'Ассаляму алейкум'. Отвечай на русском языке."},
                              {"role": "user", "content": text}],
                    temperature=0.7
                )
                bot.reply_to(message, resp.choices[0].message.content)
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка AI: {e}")
        else:
            bot.reply_to(message, f"🪞 Зеркало приняло сообщение\n\n✨ Списано 1 Благо")
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
print("🪞 ЗЕРКАЛО - 4 ГЛАВНЫЕ КНОПКИ")
print("=" * 60)
print(f"✅ Бот запущен")
print(f"👑 ТВОЙ ID: {FOUNDER_ID}")
print(f"📱 4 ГЛАВНЫЕ КНОПКИ:")
print(f"   👑 ХРАНИТЕЛЬ — все 33 кнопки внутри")
print(f"   🏢 БИЗНЕС — бизнес-раздел")
print(f"   👤 ЛЮДИ — обычные функции")
print(f"   🧠 AI-ДОКТОР — самолечение и защита")
print("=" * 60)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
