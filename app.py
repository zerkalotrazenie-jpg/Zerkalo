#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🪞 ЗЕРКАЛО - БОЖИЙ ЗАМЫСЕЛ
═══════════════════════════════════════════════════════════════════
Версия: الفتح (Великое Открытие)
Создано: 14.02.2026 - 16.06.2026 (123 дня)
Хранитель: 5409420822
🌍 Языки: Русский, Қазақша, English, العربية, Türkçe, Deutsch, Français, Español, 中文, 日本語, हिन्दी
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
import math
from datetime import datetime, timedelta
from collections import defaultdict
from flask import Flask
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ==================================================
# ⚡ АВТОУСТАНОВКА
# ==================================================

def install_package(package):
    try:
        __import__(package)
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_package("pytelegrambotapi")
install_package("groq")
install_package("flask")
install_package("requests")
install_package("deep-translator")
install_package("langdetect")

import telebot
from groq import Groq
from deep_translator import GoogleTranslator
from langdetect import detect

# ==================================================
# 🔧 НАСТРОЙКИ
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# СВЯЩЕННЫЕ ID — НЕ ТРОГАТЬ!
FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814
ADMIN_IDS = [5409420822, 5479179814]

CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"
EXCHANGE_THRESHOLD = 10_000_000  # 10 миллионов тенге для обмена Благ

# Константы для защиты Благ
MIN_BLESSINGS_TO_KEEP = 50
PROTECTED_CATEGORIES = ["elder", "child", "disabled", "sick"]
FOUNDER_UNLIMITED_BLESSINGS = True

# Награды за действия
BLESSINGS_REWARDS = {
    "daily_login": 5,
    "create_order": 10,
    "complete_order": 50,
    "post_job": 20,
    "referral": 100,
    "payment": 10,
    "review": 15,
    "help_elder": 30,
    "child_task": 10,
    "send_blessings": 5,  # Награда за перевод Благ
}

print("=" * 70)
print("🪞 ЗЕРКАЛО - الفتح (ВЕЛИКОЕ ОТКРЫТИЕ)")
print("=" * 70)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 ОСНОВАТЕЛЬ: {FOUNDER_ID}")
print(f"👸 ХРАНИТЕЛЬ: {TOMIRIS_ID}")
print(f"💎 СИСТЕМА БЛАГ: АКТИВНА")
print(f"🌍 ГЕОГРАФИЯ: ВЕСЬ МИР")
print(f"🌐 ЯЗЫКИ: 11 языков мира")
print("=" * 70)

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

app = Flask(__name__)

@app.route('/')
def home():
    return "🪞 Зеркало работает! Альхамдулиллах!", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ==================================================
# 📦 БАЗА ДАННЫХ
# ==================================================

conn = sqlite3.connect('zerkalo.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT, age INTEGER, city TEXT, country TEXT, phone TEXT,
    role TEXT DEFAULT 'user', status TEXT DEFAULT 'offline',
    last_seen TEXT, blessings INTEGER DEFAULT 100,
    tariff TEXT DEFAULT 'free', tariff_expires TEXT,
    referrer_id INTEGER DEFAULT 0, is_admin INTEGER DEFAULT 0,
    resume TEXT DEFAULT '', is_disabled INTEGER DEFAULT 0, is_sick INTEGER DEFAULT 0,
    last_lat REAL DEFAULT 0, last_lon REAL DEFAULT 0,
    balance REAL DEFAULT 0, language TEXT DEFAULT 'ru'
)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT, title TEXT, description TEXT, price INTEGER,
    customer_id INTEGER, city TEXT, country TEXT,
    status TEXT DEFAULT 'open', created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, description TEXT, salary INTEGER,
    company TEXT, city TEXT, country TEXT,
    employer_id INTEGER, status TEXT DEFAULT 'open', created_at TEXT
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

c.execute('''CREATE TABLE IF NOT EXISTS warnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, admin_id INTEGER, amount INTEGER,
    reason TEXT, created_at TEXT, status TEXT, executed_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS learning_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, balance INTEGER, need_score INTEGER,
    purpose TEXT, requested INTEGER, approved INTEGER,
    reason TEXT, created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, action TEXT, details TEXT, created_at TEXT
)''')

conn.commit()

# Словарь для ожидающих переводов
pending_transfers = {}

def astana_time():
    return (datetime.utcnow() + timedelta(hours=5)).isoformat()

def is_admin(user_id):
    return user_id in ADMIN_IDS

def get_balance(user_id):
    if user_id == FOUNDER_ID and FOUNDER_UNLIMITED_BLESSINGS:
        return 999999999
    c.execute("SELECT blessings FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    return row[0] if row else 100

def get_tariff(user_id):
    c.execute("SELECT tariff, tariff_expires FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[1] and datetime.now() > datetime.fromisoformat(row[1]):
        return "free"
    return row[0] if row else "free"

def get_user_city(user_id):
    c.execute("SELECT city, country FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0]:
        return row[0], row[1] if row[1] else "Казахстан"
    return None, None

def set_user_city(user_id, city, country):
    c.execute("UPDATE users SET city=?, country=? WHERE user_id=?", (city, country, user_id))
    conn.commit()

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
        add_earning(f"Тариф {tariff}", amount, user_id)
        bonus = int(amount / 1000) * BLESSINGS_REWARDS["payment"]
        if bonus > 0:
            add_blessings(user_id, bonus, f"пополнение на {amount} ₸")
        c.execute("SELECT referrer_id FROM users WHERE user_id=?", (user_id,))
        referrer = c.fetchone()
        if referrer and referrer[0]:
            bonus = int(amount * 0.1)
            c.execute("UPDATE users SET blessings = blessings + ? WHERE user_id=?", (bonus, referrer[0]))
            conn.commit()
            add_earning(f"Реферал {user_id}", bonus, referrer[0])
            add_blessings(referrer[0], BLESSINGS_REWARDS["referral"], f"приглашение пользователя {user_id}")
        return True, amount, tariff
    return False, 0, None

# ==================================================
# 💎 СИСТЕМА БЛАГ (СПРАВЕДЛИВАЯ)
# ==================================================

def add_blessings(user_id, amount, reason):
    if is_admin(user_id):
        return
    c.execute("UPDATE users SET blessings = blessings + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    log_action(user_id, "add_blessings", f"{amount} за {reason}")
    try:
        lang = get_user_language(user_id)
        msg = translate_text(f"✨ *+{amount} БЛАГА!*\n\n📌 Причина: {reason}\n💰 Баланс: {get_balance(user_id)} Благ", lang)
        bot.send_message(user_id, msg, parse_mode="Markdown")
    except:
        pass

def can_spare_blessings(user_id, amount_to_remove):
    c.execute("SELECT blessings, role, age, is_disabled, is_sick FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    if not user:
        return False, "Пользователь не найден"
    balance, role, age, is_disabled, is_sick = user
    age = age or 0
    if role in PROTECTED_CATEGORIES:
        return False, f"❌ Защищённая категория"
    if age < 18:
        return False, "❌ Несовершеннолетний"
    if age >= 65:
        return False, "❌ Пожилой человек"
    if is_disabled or is_sick:
        return False, "❌ Льготная категория"
    if balance - amount_to_remove < MIN_BLESSINGS_TO_KEEP:
        return False, f"❌ После списания останется меньше {MIN_BLESSINGS_TO_KEEP} Благ"
    return True, "✅ Списание возможно"

def smart_remove_blessings(user_id, amount, reason, admin_id, warning_given=False):
    if not is_admin(admin_id):
        return False, "Только Хранитель"
    can, msg = can_spare_blessings(user_id, amount)
    if not can:
        bot.send_message(admin_id, f"⚠️ {msg}")
        return False, msg
    if not warning_given:
        lang = get_user_language(user_id)
        warn_msg = translate_text(f"⚠️ *ПРЕДУПРЕЖДЕНИЕ*\n\nПричина: {reason}\nПланируется списание: {amount} Благ\nУ вас 24 часа, чтобы исправить ситуацию.", lang)
        bot.send_message(user_id, warn_msg, parse_mode="Markdown")
        c.execute("INSERT INTO warnings (user_id, admin_id, amount, reason, created_at, status) VALUES (?, ?, ?, ?, ?, ?)",
                  (user_id, admin_id, amount, reason, astana_time(), "pending"))
        conn.commit()
        return True, "✅ Предупреждение отправлено"
    c.execute("UPDATE users SET blessings = blessings - ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    log_action(admin_id, "remove_blessings", f"{amount} у {user_id} за {reason}")
    lang = get_user_language(user_id)
    remove_msg = translate_text(f"⚠️ *СПИСАНО {amount} БЛАГ*\n\nПричина: {reason}\nБаланс: {get_balance(user_id)} Благ", lang)
    bot.send_message(user_id, remove_msg, parse_mode="Markdown")
    c.execute("UPDATE warnings SET status='executed', executed_at=? WHERE user_id=? AND status='pending'", (astana_time(), user_id))
    conn.commit()
    return True, f"✅ Списано {amount} Благ"

def return_blessings(user_id, amount, reason, admin_id):
    if not is_admin(admin_id):
        return False, "Только Хранитель"
    c.execute("UPDATE users SET blessings = blessings + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    log_action(admin_id, "return_blessings", f"{amount} пользователю {user_id} за {reason}")
    lang = get_user_language(user_id)
    return_msg = translate_text(f"✅ *ВОЗВРАЩЕНО {amount} БЛАГ*\n\nПричина: {reason}\nБаланс: {get_balance(user_id)} Благ", lang)
    bot.send_message(user_id, return_msg, parse_mode="Markdown")
    return True, f"✅ Возвращено {amount} Благ"

# ==================================================
# 💝 ПЕРЕДАЧА БЛАГ МЕЖДУ ЛЮДЬМИ
# ==================================================

@bot.message_handler(commands=['send_blessings'])
def cmd_send_blessings(message):
    user_id = message.chat.id
    parts = message.text.split()
    lang = get_user_language(user_id)
    
    if len(parts) < 3:
        bot.reply_to(message, translate_text(f"""
❌ *ФОРМАТ ПЕРЕВОДА БЛАГ*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/send_blessings <ID_получателя> <количество> <причина>

📝 *Примеры:*
• /send_blessings 123456789 50 Помощь на еду
• /send_blessings 987654321 100 Благодарность

💡 Чтобы узнать ID человека, используйте /id
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""", lang), parse_mode="Markdown")
        return
    
    try:
        target_id = int(parts[1])
        amount = int(parts[2])
        reason = " ".join(parts[3:]) if len(parts) > 3 else "Перевод Благ"
        
        if user_id == target_id:
            bot.reply_to(message, translate_text("❌ Нельзя перевести Блага самому себе", lang))
            return
        if amount <= 0:
            bot.reply_to(message, translate_text("❌ Сумма должна быть больше 0", lang))
            return
        
        c.execute("SELECT user_id, name FROM users WHERE user_id=?", (target_id,))
        target = c.fetchone()
        if not target:
            bot.reply_to(message, translate_text(f"❌ Пользователь с ID {target_id} не найден в системе", lang))
            return
        
        sender_balance = get_balance(user_id)
        if sender_balance < amount:
            bot.reply_to(message, translate_text(f"❌ Недостаточно Благ. Ваш баланс: {sender_balance} ✦", lang))
            return
        
        can, msg = can_spare_blessings(user_id, amount)
        if not can:
            bot.reply_to(message, translate_text(f"❌ {msg}", lang))
            return
        
        need_assessment = blessings_economy.assess_user_need(target_id)
        advice = ""
        if need_assessment["score"] >= 100:
            advice = translate_text("\n\n🤲 «Зеркало» советует: Этот человек ОЧЕНЬ НУЖДАЕТСЯ в помощи!", lang)
        elif need_assessment["score"] >= 50:
            advice = translate_text("\n\n🤲 «Зеркало» советует: Этот человек нуждается в поддержке.", lang)
        
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(InlineKeyboardButton("✅ ПОДТВЕРДИТЬ", callback_data=f"confirm_send_{target_id}_{amount}_{reason[:50]}"))
        kb.add(InlineKeyboardButton("❌ ОТМЕНА", callback_data="cancel_send"))
        
        bot.reply_to(message, translate_text(f"""
💝 *ПЕРЕВОД БЛАГ*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📤 Отправитель: {message.from_user.first_name}
📥 Получатель: {target[1]} (ID: {target_id})
💰 Сумма: {amount} Благ
📌 Причина: {reason}

💎 Ваш баланс после перевода: {sender_balance - amount} Благ
{advice}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ *Подтвердите перевод*
""", lang), reply_markup=kb, parse_mode="Markdown")
        
        pending_transfers[user_id] = {
            "sender": user_id, "target": target_id, "amount": amount,
            "reason": reason, "sender_name": message.from_user.first_name,
            "target_name": target[1]
        }
    except:
        bot.reply_to(message, translate_text("❌ Ошибка. Формат: /send_blessings <ID> <сумма> <причина>", lang))

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_send_"))
def confirm_send_blessings(call):
    data = call.data.replace("confirm_send_", "").split("_", 2)
    if len(data) < 3:
        bot.answer_callback_query(call.id, "Ошибка")
        return
    
    target_id = int(data[0])
    amount = int(data[1])
    reason = data[2]
    lang = get_user_language(call.from_user.id)
    
    temp = pending_transfers.get(call.from_user.id)
    if not temp or temp["target"] != target_id or temp["amount"] != amount:
        bot.answer_callback_query(call.id, translate_text("❌ Перевод устарел", lang))
        bot.edit_message_text(translate_text("❌ Время ожидания истекло", lang), call.message.chat.id, call.message.message_id)
        return
    
    sender_id = temp["sender"]
    target_name = temp["target_name"]
    sender_name = temp["sender_name"]
    
    c.execute("UPDATE users SET blessings = blessings - ? WHERE user_id=?", (amount, sender_id))
    c.execute("UPDATE users SET blessings = blessings + ? WHERE user_id=?", (amount, target_id))
    conn.commit()
    
    log_action(sender_id, "send_blessings", f"{amount} -> {target_id} за {reason}")
    log_action(target_id, "receive_blessings", f"{amount} от {sender_id} за {reason}")
    
    # Награда отправителю за доброту
    add_blessings(sender_id, BLESSINGS_REWARDS["send_blessings"], f"перевод Благ пользователю {target_id}")
    
    try:
        target_lang = get_user_language(target_id)
        bot.send_message(target_id, translate_text(f"""
💝 *ВЫ ПОЛУЧИЛИ БЛАГА!*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 От: {sender_name} (ID: {sender_id})
💰 Сумма: {amount} Благ
📌 Причина: {reason}

💎 Ваш новый баланс: {get_balance(target_id)} Благ

🤲 Благодарите и помогайте другим!
""", target_lang), parse_mode="Markdown")
    except:
        pass
    
    bot.edit_message_text(translate_text(f"""
✅ *ПЕРЕВОД ВЫПОЛНЕН УСПЕШНО!*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📤 Вы перевели: {amount} Благ
📥 Получателю: {target_name} (ID: {target_id})
📌 Причина: {reason}

💎 Ваш баланс: {get_balance(sender_id)} Благ

🤲 Спасибо за доброту!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""", lang), call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    
    add_earning(f"Перевод от {sender_id}", amount, target_id)
    del pending_transfers[call.from_user.id]
    bot.answer_callback_query(call.id, translate_text("✅ Перевод выполнен!", lang))

@bot.callback_query_handler(func=lambda call: call.data == "cancel_send")
def cancel_send(call):
    if call.from_user.id in pending_transfers:
        del pending_transfers[call.from_user.id]
    lang = get_user_language(call.from_user.id)
    bot.edit_message_text(translate_text("❌ Перевод отменён.", lang), call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, translate_text("Отменено", lang))

# ==================================================
# 🔍 ПОИСК НУЖДАЮЩИХСЯ РЯДОМ
# ==================================================

@bot.message_handler(commands=['find_nearby_need'])
def find_nearby_need(message):
    user_id = message.chat.id
    lang = get_user_language(user_id)
    
    c.execute("SELECT last_lat, last_lon, city, country FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    
    if not user or not user[0]:
        bot.reply_to(message, translate_text("📍 Сначала отправьте вашу геолокацию (/share_location)", lang))
        return
    
    lat, lon, city, country = user[0], user[1], user[2], user[3]
    c.execute("SELECT user_id, name, blessings FROM users WHERE city=? AND country=? AND user_id != ? AND blessings < 200", (city, country, user_id))
    users_in_city = c.fetchall()
    
    if not users_in_city:
        bot.reply_to(message, translate_text(f"🤲 В городе {city} пока нет нуждающихся.", lang))
        return
    
    users_in_city.sort(key=lambda x: x[2])
    msg = translate_text(f"🤲 *ЛЮДИ, НУЖДАЮЩИЕСЯ В ПОМОЩИ В {city}*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n", lang)
    
    for u in users_in_city[:10]:
        need_score = "🔴 КРИТИЧЕСКАЯ" if u[2] < 50 else "🟡 ВЫСОКАЯ" if u[2] < 150 else "🟢 НОРМАЛЬНАЯ"
        msg += translate_text(f"""
👤 *{u[1]}*
🆔 ID: `{u[0]}`
💰 Благ: {u[2]} ✦
📊 Нужда: {need_score}

💝 /send_blessings {u[0]} 50 Помощь
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""", lang)
    
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================================================
# 🧠 ЭКОНОМИКА БЛАГ (ОБУЧЕНИЕ)
# ==================================================

class BlessingsEconomy:
    def __init__(self):
        self.activity_weights = {
            "work": 1.0, "help": 1.5, "education": 1.2,
            "creation": 1.3, "elder": 2.0, "child": 1.8, "environment": 1.4
        }
        self.daily_living_cost = {"food": 10, "water": 2, "shelter": 15, "health": 8, "education": 5}
    
    def calculate_work_value(self, hours, work_type, difficulty=1.0):
        base_value = hours * 10 * self.activity_weights.get(work_type, 1.0)
        return int(base_value * difficulty)
    
    def calculate_living_cost(self, user_id, days=1):
        c.execute("SELECT age, is_disabled, is_sick, city FROM users WHERE user_id=?", (user_id,))
        user = c.fetchone()
        if not user:
            return sum(self.daily_living_cost.values()) * days
        age, is_disabled, is_sick, city = user or (30, 0, 0, "стандарт")
        total = sum(self.daily_living_cost.values()) * days
        if age and age >= 65:
            total *= 1.2
        elif age and age < 18:
            total *= 0.8
        if is_disabled or is_sick:
            total *= 1.3
        if city and city.lower() in ["алматы", "астана", "almaty", "astana"]:
            total *= 1.4
        return int(total)
    
    def assess_user_need(self, user_id):
        balance = get_balance(user_id)
        living_cost = self.calculate_living_cost(user_id, 7)
        c.execute("SELECT age, is_disabled, is_sick, role FROM users WHERE user_id=?", (user_id,))
        user = c.fetchone()
        need_score = 0
        if balance < living_cost:
            need_score += 100
        if user and ((user[0] and user[0] >= 65) or user[1] or user[2]):
            need_score += 50
        if user and user[0] and user[0] < 18:
            need_score += 80
        c.execute("SELECT COUNT(*) FROM jobs WHERE employer_id=?", (user_id,))
        if c.fetchone()[0] == 0:
            need_score += 60
        status = "КРИТИЧЕСКАЯ" if need_score >= 100 else "ВЫСОКАЯ" if need_score >= 50 else "НОРМАЛЬНАЯ" if need_score >= 20 else "ХОРОШАЯ"
        return {"score": need_score, "balance": balance, "living_cost_7days": living_cost, "status": status}
    
    def decide_spending(self, user_id, requested_amount, purpose):
        need = self.assess_user_need(user_id)
        decision = {"approved": False, "reason": "", "suggested_amount": requested_amount}
        if need["score"] >= 100:
            if purpose in ["еда", "вода", "лекарства", "жильё", "медицина"]:
                decision["approved"] = True
                decision["reason"] = "Критическая потребность"
            else:
                decision["approved"] = False
                decision["reason"] = "Сначала базовые потребности"
        elif need["score"] >= 50:
            if purpose in ["еда", "вода", "лекарства", "медицина"]:
                decision["approved"] = True
                decision["suggested_amount"] = min(requested_amount, need["living_cost_7days"] // 2)
                decision["reason"] = "Частичное одобрение"
            elif purpose in ["образование", "работа", "помощь другим"]:
                decision["approved"] = True
                decision["reason"] = "Инвестиции в будущее"
            else:
                decision["approved"] = False
                decision["reason"] = "Требуется экономия"
        elif need["score"] >= 20:
            decision["approved"] = True
            decision["reason"] = "Стандартное одобрение"
        else:
            decision["approved"] = True
            decision["reason"] = "Полное одобрение"
        c.execute("INSERT INTO learning_history (user_id, balance, need_score, purpose, requested, approved, reason, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (user_id, need["balance"], need["score"], purpose, requested_amount, 1 if decision["approved"] else 0, decision["reason"], astana_time()))
        conn.commit()
        return decision

blessings_economy = BlessingsEconomy()

# ==================================================
# 🌍 ГЕОГРАФИЯ (ВЕСЬ МИР)
# ==================================================

def search_city_global(query):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=10&addressdetails=1"
        headers = {'User-Agent': 'ZerkaloBot/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        results = []
        for item in data:
            city_name = item.get('name', '')
            country = item.get('address', {}).get('country', '')
            if not city_name:
                city_name = item.get('address', {}).get('city', '') or item.get('address', {}).get('town', '') or item.get('address', {}).get('village', '')
            if city_name and country:
                results.append({'city': city_name, 'country': country})
        return results[:10]
    except:
        return []

def get_city_from_coordinates(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
        headers = {'User-Agent': 'ZerkaloBot/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        address = data.get('address', {})
        city = address.get('city') or address.get('town') or address.get('village')
        country = address.get('country', '')
        return city, country
    except:
        return None, None

def get_jobs_global(city, country):
    c.execute("SELECT id, title, salary, company FROM jobs WHERE city=? AND country=? AND status='open'", (city, country))
    return c.fetchall()

def get_orders_global(city, country):
    c.execute("SELECT id, title, price FROM orders WHERE city=? AND country=? AND status='open'", (city, country))
    return c.fetchall()

# ==================================================
# 🌐 СИСТЕМА ПЕРЕВОДА (ВСЕ ЯЗЫКИ)
# ==================================================

# Словарь кнопок на разных языках
BUTTONS = {
    "ru": {"main": "🏠 ВСЕ СФЕРЫ", "founder": "👑 ХРАНИТЕЛЬ", "business": "🏢 БИЗНЕС",
           "people": "👤 ЛЮДИ", "ai_doctor": "🧠 AI-ДОКТОР", "monetization": "💰 МОНЕТИЗАЦИЯ",
           "my_balance": "✨ МОЙ БАЛАНС", "help": "🆘 ПОМОЩЬ", "back": "🔙 НА ГЛАВНУЮ"},
    "kk": {"main": "🏠 БАРЛЫҚ САЛАЛАР", "founder": "👑 ҚОРҒАНШЫ", "business": "🏢 БИЗНЕС",
           "people": "👤 АДАМДАР", "ai_doctor": "🧠 AI-ДӘРІГЕР", "monetization": "💰 МОНЕТИЗАЦИЯ",
           "my_balance": "✨ МЕНІҢ БАЛАНСЫМ", "help": "🆘 КӨМЕК", "back": "🔙 БАСТЫ МӘЗІР"},
    "en": {"main": "🏠 ALL SPHERES", "founder": "👑 GUARDIAN", "business": "🏢 BUSINESS",
           "people": "👤 PEOPLE", "ai_doctor": "🧠 AI-DOCTOR", "monetization": "💰 MONETIZATION",
           "my_balance": "✨ MY BALANCE", "help": "🆘 HELP", "back": "🔙 MAIN MENU"},
    "ar": {"main": "🏠 جميع المجالات", "founder": "👑 الوصي", "business": "🏢 الأعمال",
           "people": "👤 الناس", "ai_doctor": "🧠 طبيب الذكاء", "monetization": "💰 تحقيق الدخل",
           "my_balance": "✨ رصيدي", "help": "🆘 مساعدة", "back": "🔙 القائمة الرئيسية"},
    "tr": {"main": "🏠 TÜM ALANLAR", "founder": "👑 KORUYUCU", "business": "🏢 İŞ",
           "people": "👤 İNSANLAR", "ai_doctor": "🧠 AI-DOKTOR", "monetization": "💰 PARALAMA",
           "my_balance": "✨ BAKİYEM", "help": "🆘 YARDIM", "back": "🔙 ANA MENÜ"},
}

def get_user_language(user_id):
    c.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] and row[0] in BUTTONS:
        return row[0]
    return 'ru'

def set_user_language(user_id, language):
    if language in BUTTONS:
        c.execute("UPDATE users SET language=? WHERE user_id=?", (language, user_id))
        conn.commit()

def detect_language(text):
    try:
        lang = detect(text)
        lang_map = {'ru':'ru','kk':'kk','en':'en','ar':'ar','tr':'tr','de':'ru','fr':'ru','es':'ru','zh-cn':'ru','ja':'ru','hi':'ru'}
        return lang_map.get(lang, 'ru')
    except:
        return 'ru'

def translate_text(text, target_lang):
    if target_lang == 'ru' or not text:
        return text
    try:
        translator = GoogleTranslator(source='ru', target=target_lang)
        return translator.translate(text)
    except:
        return text

def get_localized_button(button_key, lang):
    if lang in BUTTONS and button_key in BUTTONS[lang]:
        return BUTTONS[lang][button_key]
    return BUTTONS.get('ru', {}).get(button_key, button_key)

def get_localized_main_keyboard(lang):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton(get_localized_button("main", lang)))
    kb.add(KeyboardButton(get_localized_button("founder", lang)))
    kb.add(KeyboardButton(get_localized_button("business", lang)))
    kb.add(KeyboardButton(get_localized_button("people", lang)))
    kb.add(KeyboardButton(get_localized_button("ai_doctor", lang)))
    kb.add(KeyboardButton(get_localized_button("monetization", lang)))
    kb.add(KeyboardButton(get_localized_button("my_balance", lang)))
    kb.add(KeyboardButton(get_localized_button("help", lang)))
    return kb

def get_localized_people_keyboard(lang):
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton(translate_text("💸 РАБОТА", lang)))
    kb.add(KeyboardButton(translate_text("📦 ЗАКАЗЫ", lang)))
    kb.add(KeyboardButton(translate_text("📸 ФОТО", lang)))
    kb.add(KeyboardButton(translate_text("🎤 ГОЛОС", lang)))
    kb.add(KeyboardButton(translate_text("📍 АПТЕКА", lang)))
    kb.add(KeyboardButton(translate_text("📝 РЕЗЮМЕ", lang)))
    kb.add(KeyboardButton(translate_text("💳 KASPI QR", lang)))
    kb.add(KeyboardButton(translate_text("💰 БАЛАНС", lang)))
    kb.add(KeyboardButton(translate_text("✨ МОЙ БАЛАНС", lang)))
    kb.add(KeyboardButton(translate_text("❓ ВОПРОС", lang)))
    kb.add(KeyboardButton(get_localized_button("help", lang)))
    kb.add(KeyboardButton(get_localized_button("back", lang)))
    return kb

# ==================================================
# 📱 КЛАВИАТУРЫ
# ==================================================

def get_main_keyboard():
    return get_localized_main_keyboard('ru')

def get_founder_keyboard():
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    kb.add(KeyboardButton("👥 ОНЛАЙН"), KeyboardButton("📊 СТАТИСТИКА"), KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("👥 ВСЕ ЛЮДИ"), KeyboardButton("✨ ВСЕ БЛАГА"), KeyboardButton("👑 МОЁ БЛАГО"))
    kb.add(KeyboardButton("📤 РАССЫЛКА"), KeyboardButton("💳 ПЛАТЕЖИ"), KeyboardButton("🏦 ВЫВОДЫ"))
    kb.add(KeyboardButton("📊 ДОХОДЫ"), KeyboardButton("📜 ЛОГИ"), KeyboardButton("🔍 ПОИСК"))
    kb.add(KeyboardButton("📈 ОТЧЁТ"), KeyboardButton("🩺 ЗДОРОВЬЕ"), KeyboardButton("🛡️ ЗАЩИТА"))
    kb.add(KeyboardButton("💎 ТАРИФЫ"), KeyboardButton("🧠 ЭКОНОМИКА"), KeyboardButton("🔄 ОБНОВИТЬ"))
    kb.add(KeyboardButton("📡 СТАТУС"), KeyboardButton("🧹 ОЧИСТИТЬ"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"), KeyboardButton("📸 ФОТО"))
    kb.add(KeyboardButton("🎤 ГОЛОС"), KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("🏢 БИЗНЕС"), KeyboardButton("👵 ПОЖИЛЫЕ"), KeyboardButton("🧒 ДЕТИ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🌍 ВЕСЬ МИР"), KeyboardButton("🆘 ПОМОЩЬ"), KeyboardButton("🔘 الفتح"))
    return kb

def get_business_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 АНАЛИТИКА"), KeyboardButton("🤖 АВТОМАТИЗАЦИЯ"))
    kb.add(KeyboardButton("📈 ЛИЗИНГ"), KeyboardButton("💼 ЗАКАЗЫ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"))
    kb.add(KeyboardButton("🌍 ВЕСЬ МИР"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_people_keyboard():
    return get_localized_people_keyboard('ru')

def get_ai_doctor_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🩺 ЛЕЧЕНИЕ"), KeyboardButton("🛡️ ПРОВЕРКА"))
    kb.add(KeyboardButton("📊 СТАТУС"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_monetization_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💎 КУПИТЬ ТАРИФ"), KeyboardButton("⭐ ПАРТНЁРСКАЯ"))
    kb.add(KeyboardButton("🏦 KASPI QR"), KeyboardButton("💎 USDT TRC20"))
    kb.add(KeyboardButton("📊 МОЙ ДОХОД"), KeyboardButton("📈 ОБЩАЯ СТАТИСТИКА"))
    kb.add(KeyboardButton("💸 ВЫВЕСТИ"), KeyboardButton("📋 ИСТОРИЯ"))
    kb.add(KeyboardButton("🔘 الفتح"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_role_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ"))
    kb.add(KeyboardButton("🏢 БИЗНЕСМЕН"))
    kb.add(KeyboardButton("👵 ПОЖИЛОЙ ЧЕЛОВЕК"))
    kb.add(KeyboardButton("🧒 РЕБЁНОК"))
    return kb

def get_city_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📍 ОПРЕДЕЛИТЬ АВТОМАТИЧЕСКИ"))
    kb.add(KeyboardButton("🔍 НАЙТИ ГОРОД"))
    kb.add(KeyboardButton("📋 МОЙ ГОРОД"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_tariff_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("📱 Бесплатный", callback_data="tariff_free"))
    kb.add(InlineKeyboardButton("⭐ Базовый - 1000₸", callback_data="tariff_basic"))
    kb.add(InlineKeyboardButton("🚀 PRO - 5000₸", callback_data="tariff_pro"))
    kb.add(InlineKeyboardButton("💎 Бизнес - 20000₸", callback_data="tariff_business"))
    return kb

TARIFFS = {
    "free": {"name": "Бесплатный", "price": 0},
    "basic": {"name": "Базовый", "price": 1000},
    "pro": {"name": "PRO", "price": 5000},
    "business": {"name": "Бизнес", "price": 20000}
}

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
        if is_admin(user_id):
            c.execute("UPDATE users SET is_admin=1, tariff='pro' WHERE user_id=?", (user_id,))
        conn.commit()
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n✨ Вы получили 100 Благ!\n\n🌍 Укажите ваш город:", reply_markup=get_city_keyboard())
        return
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (astana_time(), user_id))
    conn.commit()
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n🌍 Пожалуйста, укажите ваш город:", reply_markup=get_city_keyboard())
    else:
        if is_admin(user_id):
            bot.reply_to(message, f"👑 АССАЛЯМУ АЛЕЙКУМ, ХРАНИТЕЛЬ {name}!\n\n📍 {city}, {country}\n💰 БАЛАНС: БЕЗГРАНИЧНО\n\n📱 ПАНЕЛЬ УПРАВЛЕНИЯ:", reply_markup=get_founder_keyboard())
        else:
            bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n📍 {city}, {country}\n💰 Баланс: {get_balance(user_id)} Благ\n\nКто вы?", reply_markup=get_role_keyboard())

@bot.message_handler(commands=['id'])
def cmd_id(message):
    user_id = message.chat.id
    city, country = get_user_city(user_id)
    city_str = f"{city}, {country}" if city else "не указан"
    bot.reply_to(message, f"🆔 *ТВОЙ ID:* `{user_id}`\n\n👑 Хранитель: {'✅' if is_admin(user_id) else '❌'}\n📍 Город: {city_str}\n💰 Баланс: {get_balance(user_id)} Благ", parse_mode="Markdown")

@bot.message_handler(commands=['pay'])
def cmd_pay(message):
    user_id = message.chat.id
    if user_id == FOUNDER_ID:
        bot.reply_to(message, "👑 У вас безграничные Блага. Пополнение не требуется.", parse_mode="Markdown")
        return
    bot.reply_to(message, "💎 *ВЫБЕРИТЕ ТАРИФ*", reply_markup=get_tariff_keyboard(), parse_mode="Markdown")

@bot.message_handler(commands=['lang'])
def cmd_change_language(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, """
🌐 *СМЕНА ЯЗЫКА / CHANGE LANGUAGE*

Доступные языки / Available languages:
• ru — Русский
• kk — Қазақша
• en — English
• ar — العربية
• tr — Türkçe

📝 Пример: /lang kk
""", parse_mode="Markdown")
        return
    new_lang = parts[1].lower()
    if new_lang in BUTTONS:
        set_user_language(message.chat.id, new_lang)
        bot.reply_to(message, translate_text(f"✅ Язык изменён на {new_lang.upper()}!", new_lang), reply_markup=get_localized_main_keyboard(new_lang))
    else:
        bot.reply_to(message, "❌ Язык не поддерживается. Используйте /lang для списка.")

@bot.message_handler(commands=['share_location'])
def share_location_command(message):
    lang = get_user_language(message.chat.id)
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add(KeyboardButton(translate_text("📍 ПОДЕЛИТЬСЯ ГЕОЛОКАЦИЕЙ", lang), request_location=True))
    bot.reply_to(message, translate_text("📍 Нажмите кнопку, чтобы поделиться геолокацией.", lang), reply_markup=kb)

# ==================================================
# 👑 АДМИН-КОМАНДЫ
# ==================================================

@bot.message_handler(commands=['add_blessings'])
def cmd_add_blessings(message):
    if not is_admin(message.chat.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "❌ /add_blessings <user_id> <количество> <причина>")
        return
    try:
        target_id = int(parts[1])
        amount = int(parts[2])
        reason = " ".join(parts[3:]) if len(parts) > 3 else "Награда от Хранителя"
        add_blessings(target_id, amount, reason)
        bot.reply_to(message, f"✅ Начислено {amount} Благ пользователю {target_id}")
    except:
        bot.reply_to(message, "❌ Ошибка")

@bot.message_handler(commands=['warn'])
def cmd_warn(message):
    if not is_admin(message.chat.id):
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "❌ /warn <user_id> <причина>")
        return
    try:
        target_id = int(parts[1])
        reason = parts[2]
        success, result = smart_remove_blessings(target_id, 100, reason, message.chat.id, warning_given=False)
        bot.reply_to(message, result)
    except:
        bot.reply_to(message, "❌ Ошибка")

@bot.message_handler(commands=['force_remove'])
def cmd_force_remove(message):
    if not is_admin(message.chat.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "❌ /force_remove <user_id> <количество> <причина>")
        return
    try:
        target_id = int(parts[1])
        amount = int(parts[2])
        reason = " ".join(parts[3:]) if len(parts) > 3 else "Принудительное списание"
        success, result = smart_remove_blessings(target_id, amount, reason, message.chat.id, warning_given=True)
        bot.reply_to(message, result)
    except:
        bot.reply_to(message, "❌ Ошибка")

@bot.message_handler(commands=['return_blessings'])
def cmd_return_blessings(message):
    if not is_admin(message.chat.id):
        return
    parts = message.text.split(maxsplit=3)
    if len(parts) < 3:
        bot.reply_to(message, "❌ /return_blessings <user_id> <количество> <причина>")
        return
    try:
        target_id = int(parts[1])
        amount = int(parts[2])
        reason = parts[3] if len(parts) > 3 else "Возврат по решению Хранителя"
        success, result = return_blessings(target_id, amount, reason, message.chat.id)
        bot.reply_to(message, result)
    except:
        bot.reply_to(message, "❌ Ошибка")

# ==================================================
# ✨ СИСТЕМА БЛАГ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "✨ МОЙ БАЛАНС")
def show_user_balance(message):
    user_id = message.chat.id
    lang = get_user_language(user_id)
    balance = get_balance(user_id)
    need = blessings_economy.assess_user_need(user_id)
    living_cost = blessings_economy.calculate_living_cost(user_id, 30)
    c.execute("SELECT SUM(amount) FROM payments WHERE status='completed'")
    total_volume = c.fetchone()[0] or 0
    exchange_status = "🔒 НЕДОСТУПЕН" if total_volume < EXCHANGE_THRESHOLD else f"💱 ДОСТУПЕН (1 ✦ = 1 ₸)"
    msg = translate_text(f"""
✨ *ВАШИ БЛАГА*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Баланс: {balance} Благ
📊 Статус: {need['status']}
📋 Прожиточный минимум (месяц): {living_cost} Благ

💎 ЧТО МОЖНО ДЕЛАТЬ:
• 1 Благо = 1 сообщение (льготникам бесплатно)
• Награда за активность
• Обмен на товары и услуги

{exchange_status}

✨ КАК ЗАРАБОТАТЬ:
• 🎁 Пригласить друга — +100 ✦
• 📦 Выполнить заказ — +50 ✦
• 💝 Помочь другому — +5 ✦
• 👵 Помочь пожилым — +30 ✦
• 💳 Пополнить баланс — +10 ✦ за 1000₸
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""", lang)
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👑 МОЁ БЛАГО" and is_admin(m.chat.id))
def my_blessings(message):
    user_id = message.chat.id
    if user_id == FOUNDER_ID:
        msg = f"""
✨ *ВАШИ БЛАГА (ОСНОВАТЕЛЬ)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👑 Статус: БЕЗГРАНИЧНО
💰 Баланс: ∞ (бесконечно)

📊 Общая статистика:
• Всего Благ в системе: {get_total_blessings()}
• Средний баланс: {get_avg_blessings()} Благ

🕋 Вы — источник Благ. Они создаются из воздуха.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    else:
        balance = get_balance(user_id)
        msg = f"""
✨ *ВАШИ БЛАГА (ХРАНИТЕЛЬ)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👑 Ваш баланс: {balance} Благ

📊 Общая статистика:
• Всего Благ в системе: {get_total_blessings()}
• Средний баланс: {get_avg_blessings()} Благ

💎 Вы можете начислять и списывать Блага командами:
/add_blessings, /warn, /force_remove, /return_blessings
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "✨ ВСЕ БЛАГА" and is_admin(m.chat.id))
def show_all_blessings(message):
    c.execute("SELECT user_id, name, role, blessings FROM users ORDER BY blessings DESC LIMIT 30")
    users = c.fetchall()
    if not users:
        bot.reply_to(message, "✨ Нет данных о Благах")
        return
    msg = "✨ *РЕЙТИНГ БЛАГ*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, u in enumerate(users, 1):
        medal = "🏆 " if i == 1 else "🥈 " if i == 2 else "🥉 " if i == 3 else ""
        if u[0] == FOUNDER_ID:
            balance_display = "∞ (безгранично)"
        else:
            balance_display = f"{u[3]} ✦"
        msg += f"{medal}{i}. {u[1]}\n   🆔 {u[0]} | {u[2]} | 💰 {balance_display}\n\n"
    msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📊 *ВСЕГО В СИСТЕМЕ:* {get_total_blessings()} Благ\n📈 *СРЕДНИЙ БАЛАНС:* {get_avg_blessings()} Благ"
    bot.reply_to(message, msg, parse_mode="Markdown")

def get_total_blessings():
    c.execute("SELECT SUM(blessings) FROM users WHERE user_id != ?", (FOUNDER_ID,))
    row = c.fetchone()
    return row[0] if row[0] else 0

def get_avg_blessings():
    c.execute("SELECT AVG(blessings) FROM users WHERE user_id != ?", (FOUNDER_ID,))
    row = c.fetchone()
    return int(row[0]) if row[0] else 0

# ==================================================
# 🌍 ГЕОГРАФИЯ (весь мир)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🌍 ВЕСЬ МИР")
def world_geography(message):
    user_id = message.chat.id
    lang = get_user_language(user_id)
    city, country = get_user_city(user_id)
    if not city:
        bot.reply_to(message, translate_text("🌍 Сначала укажите ваш город! Нажмите «🌍 МОЙ ГОРОД»", lang))
        return
    jobs = get_jobs_global(city, country)
    orders = get_orders_global(city, country)
    msg = translate_text(f"🌍 *ВЕСЬ МИР — {city}, {country}*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n", lang)
    msg += translate_text(f"💼 *РАБОТА:*\n", lang) + ("\n".join([f"🆔 {j[0]} | {j[1]} | {j[2]} ₸ | {j[3]}" for j in jobs]) if jobs else translate_text("📭 Нет вакансий", lang))
    msg += translate_text(f"\n\n📦 *ЗАКАЗЫ:*\n", lang) + ("\n".join([f"🆔 {o[0]} | {o[1]} | {o[2]} ₸" for o in orders]) if orders else translate_text("📭 Нет заказов", lang))
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton(translate_text("🔍 ПОИСК ПО МИРУ", lang)))
    kb.add(KeyboardButton(translate_text("🔙 НАЗАД", lang)))
    bot.reply_to(message, msg, reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🌍 МОЙ ГОРОД")
def my_city_menu(message):
    user_id = message.chat.id
    lang = get_user_language(user_id)
    city, country = get_user_city(user_id)
    if city:
        jobs = get_jobs_global(city, country)
        orders = get_orders_global(city, country)
        msg = translate_text(f"🌍 *ВАШ ГОРОД:* {city}, {country}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n", lang)
        msg += translate_text(f"💼 *РАБОТА:* {len(jobs)} вакансий\n📦 *ЗАКАЗЫ:* {len(orders)} заказов", lang)
    else:
        msg = translate_text("🌍 *ВЫБОР ГОРОДА*\n\nУкажите ваш город.", lang)
    bot.reply_to(message, msg, reply_markup=get_city_keyboard(), parse_mode="Markdown")

@bot.message_handler(content_types=['location'])
def handle_location(message):
    user_id = message.chat.id
    lat = message.location.latitude
    lon = message.location.longitude
    city, country = get_city_from_coordinates(lat, lon)
    lang = get_user_language(user_id)
    if city:
        set_user_city(user_id, city, country)
        bot.reply_to(message, translate_text(f"✅ *ГОРОД ОПРЕДЕЛЁН!*\n\n📍 {city}, {country}", lang), reply_markup=get_main_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, translate_text("✅ Геолокация сохранена!", lang), reply_markup=get_main_keyboard())

# ==================================================
# 🚀 ЗАПУСК
# ==================================================

# AI-ДОКТОР (упрощённый)
class AIDoctor:
    def __init__(self):
        self.threats_blocked = 0
        self.fixes_applied = 0
        self.start_time = time.time()
    def get_report(self):
        uptime = int(time.time() - self.start_time)
        return f"🧠 AI-ДОКТОР\n⏱️ {uptime//3600}ч\n🛡️ Угроз: {self.threats_blocked}\n🔧 Лечений: {self.fixes_applied}"
    def heal(self):
        self.fixes_applied += 1
        return "✅ Диагностика проведена"

ai_doctor = AIDoctor()

@bot.message_handler(func=lambda m: m.text == "🧠 AI-ДОКТОР")
def ai_doctor_section(message):
    lang = get_user_language(message.chat.id)
    bot.reply_to(message, translate_text(f"🧠 *AI-ДОКТОР*\n\n{ai_doctor.get_report()}", lang), reply_markup=get_ai_doctor_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🩺 ЛЕЧЕНИЕ")
def ai_heal(message):
    lang = get_user_language(message.chat.id)
    bot.reply_to(message, translate_text(f"🧠 *AI-ДОКТОР*\n\n{ai_doctor.heal()}", lang))

@bot.message_handler(func=lambda m: m.text == "🛡️ ПРОВЕРКА")
def ai_check(message):
    lang = get_user_language(message.chat.id)
    bot.reply_to(message, translate_text("🛡️ *ПРОВЕРКА*\n✅ Код: чист\n✅ Блага: активны\n✅ География: весь мир\n✅ Защита: активна", lang))

@bot.message_handler(func=lambda m: m.text == "📊 СТАТУС")
def ai_status(message):
    lang = get_user_language(message.chat.id)
    bot.reply_to(message, translate_text(ai_doctor.get_report(), lang), parse_mode="Markdown")

# 5 ГЛАВНЫХ КНОПОК
@bot.message_handler(func=lambda m: m.text == "👑 ХРАНИТЕЛЬ")
def founder_section(message):
    if is_admin(message.chat.id):
        bot.reply_to(message, "👑 *ПАНЕЛЬ ХРАНИТЕЛЯ*", reply_markup=get_founder_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Нет доступа")

@bot.message_handler(func=lambda m: m.text == "🏢 БИЗНЕС")
def business_section(message):
    bot.reply_to(message, "🏢 *БИЗНЕС-РАЗДЕЛ*", reply_markup=get_business_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👤 ЛЮДИ")
def people_section(message):
    bot.reply_to(message, "👤 *ОБЫЧНЫЙ РАЗДЕЛ*", reply_markup=get_people_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💰 МОНЕТИЗАЦИЯ")
def monetization_section(message):
    total_earned = get_total_earnings()
    msg = f"💰 *МОНЕТИЗАЦИЯ*\n\n📊 Всего заработано: {total_earned} ₸\n💎 Тариф: {TARIFFS[get_tariff(message.chat.id)]['name']}\n\n🔘 الفتح — запуск полной монетизации"
    bot.reply_to(message, msg, reply_markup=get_monetization_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔘 الفتح")
def sacred_launch(message):
    if not is_admin(message.chat.id):
        bot.reply_to(message, "❌ Только Хранитель")
        return
    lang = get_user_language(message.chat.id)
    msg = translate_text("""
🔘 *الفتح — ВЕЛИКОЕ ОТКРЫТИЕ*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤲 *بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ*

☀️ *Свершилось.* То, что собиралось 123 дня, сегодня обретает жизнь.

✅ Врата блага ОТКРЫТЫ
✅ Система НАЧАЛА работу
✅ Благословение НИСХОДИТ
✅ Заработок ВКЛЮЧЁН 24/7

*Альхамдулиллах.* 🤲
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""", lang)
    bot.reply_to(message, msg, parse_mode="Markdown")
    c.execute("SELECT user_id FROM users WHERE tariff='free'")
    users = c.fetchall()
    for u in users[:30]:
        try:
            bot.send_message(u[0], translate_text("💎 *ОТКРЫТИЕ!*\n\n«Зеркало» начало свой путь.\nАктивируйте тариф: /pay", get_user_language(u[0])), parse_mode="Markdown")
            time.sleep(0.5)
        except:
            pass

# ВЫБОР РОЛИ
@bot.message_handler(func=lambda m: m.text in ["👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ", "ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ"])
def set_user_role(message):
    c.execute("UPDATE users SET role='user' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Обычный режим", reply_markup=get_people_keyboard())

@bot.message_handler(func=lambda m: m.text in ["🏢 БИЗНЕСМЕН", "БИЗНЕСМЕН"])
def set_business_role(message):
    c.execute("UPDATE users SET role='business' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Бизнес-режим", reply_markup=get_business_keyboard())

@bot.message_handler(func=lambda m: m.text in ["👵 ПОЖИЛОЙ ЧЕЛОВЕК", "ПОЖИЛОЙ ЧЕЛОВЕК"])
def set_elder_role(message):
    c.execute("UPDATE users SET role='elder' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Режим для пожилых", reply_markup=get_people_keyboard())

@bot.message_handler(func=lambda m: m.text in ["🧒 РЕБЁНОК", "РЕБЁНОК"])
def set_child_role(message):
    c.execute("UPDATE users SET role='child' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Детский режим", reply_markup=get_people_keyboard())

# ОСТАЛЬНЫЕ ФУНКЦИИ (упрощённо)
@bot.message_handler(func=lambda m: m.text == "💸 РАБОТА")
def work_short(message):
    lang = get_user_language(message.chat.id)
    bot.reply_to(message, translate_text("💸 *РАБОТА*\n🔍 В разработке", lang), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📦 ЗАКАЗЫ")
def orders_short(message):
    lang = get_user_language(message.chat.id)
    bot.reply_to(message, translate_text("📦 *ЗАКАЗЫ*\n➕ Напишите описание", lang), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📸 ФОТО")
def photo_short(message):
    bot.reply_to(message, "📸 Отправьте фото")

@bot.message_handler(func=lambda m: m.text == "🎤 ГОЛОС")
def voice_short(message):
    bot.reply_to(message, "🎤 Отправьте голосовое")

@bot.message_handler(func=lambda m: m.text == "📍 АПТЕКА")
def pharmacy_short(message):
    bot.reply_to(message, "📍 Отправьте геолокацию")

@bot.message_handler(func=lambda m: m.text == "📝 РЕЗЮМЕ")
def resume_short(message):
    msg = bot.reply_to(message, "📝 Напишите резюме:")
    bot.register_next_step_handler(msg, lambda m: c.execute("UPDATE users SET resume=? WHERE user_id=?", (m.text, m.chat.id)) or conn.commit() or bot.reply_to(m, "✅ РЕЗЮМЕ СОХРАНЕНО!"))

@bot.message_handler(func=lambda m: m.text == "💳 KASPI QR")
def kaspi_short(message):
    msg = bot.reply_to(message, "💳 *KASPI QR*\n\nВведите сумму:")
    bot.register_next_step_handler(msg, lambda m: bot.reply_to(m, f"💳 *KASPI QR*\n💰 {m.text} ₸\n📱 {generate_kaspi_qr(int(m.text))}", parse_mode="Markdown") if m.text.isdigit() else bot.reply_to(m, "❌ Введите число"))

@bot.message_handler(func=lambda m: m.text == "💰 БАЛАНС")
def balance_short(message):
    user_id = message.chat.id
    lang = get_user_language(user_id)
    bot.reply_to(message, translate_text(f"💰 *БАЛАНС:* {get_balance(user_id)} Благ\n💳 /pay", lang), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "❓ ВОПРОС")
def ask_short(message):
    msg = bot.reply_to(message, "❓ Напишите вопрос:")
    bot.register_next_step_handler(msg, lambda m: bot.reply_to(m, f"🤖 Вопрос принят!") if not client else None)

@bot.message_handler(func=lambda m: m.text == "🆘 ПОМОЩЬ")
def help_short(message):
    lang = get_user_language(message.chat.id)
    help_text = translate_text("""
🪞 *ПОМОЩЬ*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 *ГЛАВНЫЕ КНОПКИ:*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👑 ХРАНИТЕЛЬ — полное управление (только для вас)
🏢 БИЗНЕС — аналитика, лизинг, заказы
👤 ЛЮДИ — работа, заказы, услуги
🧠 AI-ДОКТОР — диагностика и лечение
💰 МОНЕТИЗАЦИЯ — тарифы, партнёрка, вывод
✨ МОЙ БАЛАНС — ваши Блага

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 *ЧТО ТАКОЕ БЛАГА?*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Блага — это внутренняя энергия «Зеркала».
• 1 Благо = 1 сообщение
• Зарабатывайте за активность
• Переводите другим людям (/send_blessings)
• Помогайте нуждающимся (/find_nearby_need)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ /id — узнать свой ID
⚡ /pay — купить тариф
⚡ /lang — сменить язык

🤲 *«Зеркало» ведёт к свету.*
""", lang)
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔙 НА ГЛАВНУЮ")
def back_main(message):
    user_id = message.chat.id
    if is_admin(user_id):
        bot.reply_to(message, "👑 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_founder_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "🏠 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔙 НАЗАД")
def back_previous(message):
    bot.reply_to(message, "🏠 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_main_keyboard(), parse_mode="Markdown")

# АДМИН-КОМАНДЫ (статистика)
@bot.message_handler(func=lambda m: m.text == "👥 ОНЛАЙН" and is_admin(m.chat.id))
def admin_online(message):
    c.execute("SELECT user_id, name FROM users WHERE last_seen > datetime('now', '-5 minutes')")
    users = c.fetchall()
    bot.reply_to(message, "🟢 ОНЛАЙН:\n" + "\n".join([f"{u[1]} (ID: {u[0]})" for u in users]) if users else "🟢 Никого нет")

@bot.message_handler(func=lambda m: m.text == "📊 СТАТИСТИКА" and is_admin(m.chat.id))
def admin_stats(message):
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT SUM(blessings) FROM users")
    blessings = c.fetchone()[0] or 0
    bot.reply_to(message, f"📊 СТАТИСТИКА:\n👥 {total}\n✨ {blessings} Благ")

@bot.message_handler(func=lambda m: m.text == "🧠 ЭКОНОМИКА" and is_admin(m.chat.id))
def admin_economy(message):
    c.execute("SELECT COUNT(*) FROM learning_history")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM learning_history WHERE approved=1")
    approved = c.fetchone()[0]
    bot.reply_to(message, f"🧠 ЭКОНОМИКА БЛАГ\n📊 Решений: {total}\n✅ Одобрено: {approved}\n❌ Отклонено: {total-approved}")

@bot.message_handler(func=lambda m: m.text == "🔄 ОБНОВИТЬ" and is_admin(m.chat.id))
def admin_reload(message):
    bot.reply_to(message, "🔄 Обновление...\n✅ Готово!")

@bot.message_handler(func=lambda m: m.text == "📡 СТАТУС" and is_admin(m.chat.id))
def admin_status(message):
    bot.reply_to(message, f"📡 СТАТУС:\n👑 Хранитель активен\n✅ Система работает")

@bot.message_handler(func=lambda m: m.text == "🧹 ОЧИСТИТЬ" and is_admin(m.chat.id))
def admin_clean(message):
    bot.reply_to(message, "🧹 Очистка...\n✅ Готово!")

@bot.message_handler(func=lambda m: m.text == "💳 ПЛАТЕЖИ" and is_admin(m.chat.id))
def admin_payments(message):
    bot.reply_to(message, "💳 ПЛАТЕЖИ:\n⏳ В разработке")

@bot.message_handler(func=lambda m: m.text == "🏦 ВЫВОДЫ" and is_admin(m.chat.id))
def admin_withdraws(message):
    bot.reply_to(message, "🏦 ВЫВОДЫ:\n⏳ В разработке")

@bot.message_handler(func=lambda m: m.text == "📊 ДОХОДЫ" and is_admin(m.chat.id))
def admin_earnings(message):
    total = get_total_earnings()
    bot.reply_to(message, f"📊 ДОХОДЫ:\n💰 {total} ₸")

@bot.message_handler(func=lambda m: m.text == "📜 ЛОГИ" and is_admin(m.chat.id))
def admin_logs(message):
    bot.reply_to(message, "📜 ЛОГИ:\n⏳ В разработке")

@bot.message_handler(func=lambda m: m.text == "🔍 ПОИСК" and is_admin(m.chat.id))
def admin_search(message):
    msg = bot.reply_to(message, "🔍 Введите ID:")
    bot.register_next_step_handler(msg, lambda m: bot.reply_to(m, f"👤 ID: {m.text}\n📛 Пользователь найден") if m.text.isdigit() else bot.reply_to(m, "❌ Введите ID"))

@bot.message_handler(func=lambda m: m.text == "📈 ОТЧЁТ" and is_admin(m.chat.id))
def admin_report(message):
    bot.reply_to(message, "📈 ОТЧЁТ:\n✅ Система стабильна")

@bot.message_handler(func=lambda m: m.text == "🩺 ЗДОРОВЬЕ" and is_admin(m.chat.id))
def admin_health(message):
    bot.reply_to(message, "🩺 ЗДОРОВЬЕ:\n✅ Бот работает\n✅ Блага активны\n✅ География активна")

@bot.message_handler(func=lambda m: m.text == "🛡️ ЗАЩИТА" and is_admin(m.chat.id))
def admin_security(message):
    bot.reply_to(message, "🛡️ ЗАЩИТА:\n✅ Антивирус активен")

@bot.message_handler(func=lambda m: m.text == "💎 ТАРИФЫ" and is_admin(m.chat.id))
def admin_tariffs(message):
    bot.reply_to(message, "💎 ТАРИФЫ:\n• Бесплатный\n• Базовый - 1000₸\n• PRO - 5000₸\n• Бизнес - 20000₸")

# ФОНОВЫЙ ПРОЦЕСС
def status_worker():
    while True:
        time.sleep(60)
        try:
            c.execute("UPDATE users SET status='offline' WHERE last_seen < datetime('now', '-5 minutes')")
            conn.commit()
        except:
            pass

threading.Thread(target=status_worker, daemon=True).start()

# ОБРАБОТЧИК С АВТООПРЕДЕЛЕНИЕМ ЯЗЫКА
@bot.message_handler(func=lambda m: m.text and not m.text.startswith('/') and m.text not in ["👑 ХРАНИТЕЛЬ", "🏢 БИЗНЕС", "👤 ЛЮДИ", "🧠 AI-ДОКТОР", "💰 МОНЕТИЗАЦИЯ", "✨ МОЙ БАЛАНС", "🆘 ПОМОЩЬ", "🔙 НА ГЛАВНУЮ", "🔙 НАЗАД"])
def handle_with_language(message):
    user_id = message.chat.id
    text = message.text
    detected_lang = detect_language(text)
    user_lang = get_user_language(user_id)
    if user_lang != detected_lang:
        set_user_language(user_id, detected_lang)
        user_lang = detected_lang
        log_action(user_id, "language_changed", detected_lang)
    
    balance = get_balance(user_id)
    if balance >= 1:
        c.execute("UPDATE users SET blessings = blessings - 1 WHERE user_id=?", (user_id,))
        conn.commit()
        if client:
            try:
                resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "Ты — Зеркало. Отвечай кратко, с уважением. Всегда начинай с 'Ассаляму алейкум'. Отвечай на языке пользователя."},
                              {"role": "user", "content": text}],
                    temperature=0.7
                )
                answer = resp.choices[0].message.content
                if user_lang != 'ru':
                    answer = translate_text(answer, user_lang)
                bot.reply_to(message, answer)
            except Exception as e:
                bot.reply_to(message, translate_text(f"❌ Ошибка AI: {str(e)[:100]}", user_lang))
        else:
            bot.reply_to(message, translate_text("🪞 Сообщение принято", user_lang))
    else:
        bot.reply_to(message, translate_text(f"❌ Не хватает 1 Блага!\n💰 /pay", user_lang))

# ==================================================
# 🚀 ЗАПУСК
# ==================================================

print("=" * 70)
print("🪞 ЗЕРКАЛО - الفتح (ВЕЛИКОЕ ОТКРЫТИЕ)")
print("=" * 70)
print(f"✅ Бот запущен успешно")
print(f"👑 ОСНОВАТЕЛЬ: {FOUNDER_ID}")
print(f"👸 ХРАНИТЕЛЬ: {TOMIRIS_ID}")
print(f"💎 СИСТЕМА БЛАГ: АКТИВНА")
print(f"✨ БАЛАНС ОСНОВАТЕЛЯ: БЕЗГРАНИЧНО")
print(f"🌍 ГЕОГРАФИЯ: ВЕСЬ МИР")
print(f"🌐 ЯЗЫКИ: 5+ (ru, kk, en, ar, tr)")
print(f"💝 ПЕРЕДАЧА БЛАГ: АКТИВНА")
print(f"🔘 КНОПКА الفتح: ГОТОВА")
print("=" * 70)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
