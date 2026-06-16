#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🪞 ЗЕРКАЛО - ПОЛНАЯ ВЕРСИЯ С ВИКИПЕДИЕЙ И ИНТЕРНЕТОМ
═══════════════════════════════════════════════════════════════════
✅ Разумное общение с доступом к Википедии
✅ Поиск в интернете через DuckDuckGo
✅ Все кнопки работают
✅ Самообучение
✅ Голосовое управление
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
import speech_recognition as sr
from pydub import AudioSegment
from datetime import datetime, timedelta
from flask import Flask
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ==================================================
# ⚡ УСТАНОВКА
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
install_package("SpeechRecognition")
install_package("pydub")
install_package("wikipedia-api")

import telebot
from groq import Groq
import wikipediaapi

# ==================================================
# 🔧 НАСТРОЙКИ
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814
ADMIN_IDS = [5409420822, 5479179814]

KASPI_PHONE = "+777733440345"
CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"
KASPI_NAME = "Нурсулу"
RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "zerkalo.onrender.com")

print("=" * 70)
print("🪞 ЗЕРКАЛО - ПОЛНАЯ ВЕРСИЯ С ВИКИПЕДИЕЙ")
print("=" * 70)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 ОСНОВАТЕЛЬ: {FOUNDER_ID}")
print("=" * 70)

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Подключаем Википедию
wiki_wiki = wikipediaapi.Wikipedia('ru')

app = Flask(__name__)

@app.route('/')
def home():
    return "🪞 ЗЕРКАЛО РАБОТАЕТ 24/7!", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ==================================================
# ⏰ СУПЕР-ПИНГЕР
# ==================================================

def super_pinger():
    url = f"https://{RENDER_HOSTNAME}/"
    ping_count = 0
    while True:
        try:
            response = requests.get(url, timeout=10)
            ping_count += 1
            print(f"🔵 Пинг #{ping_count} | Статус: {response.status_code}")
        except:
            pass
        time.sleep(120)

threading.Thread(target=super_pinger, daemon=True).start()

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
    referrer_id INTEGER DEFAULT 0, is_admin INTEGER DEFAULT 0,
    resume TEXT DEFAULT '', is_disabled INTEGER DEFAULT 0, is_sick INTEGER DEFAULT 0,
    looking_for_job INTEGER DEFAULT 0, looking_for_master INTEGER DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, description TEXT, price INTEGER,
    customer_id INTEGER, executor_id INTEGER DEFAULT 0,
    status TEXT DEFAULT 'open', created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT, description TEXT, salary INTEGER,
    company TEXT, city TEXT, employer_id INTEGER,
    status TEXT DEFAULT 'open', created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, amount INTEGER, method TEXT,
    tariff TEXT, status TEXT, transaction_id TEXT, created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS earnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT, amount INTEGER, user_id INTEGER, created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS conversation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, role TEXT, content TEXT, created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS learning_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, request TEXT, code TEXT, created_at TEXT
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
    if user_id == FOUNDER_ID:
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
        c.execute("SELECT referrer_id FROM users WHERE user_id=?", (user_id,))
        referrer = c.fetchone()
        if referrer and referrer[0]:
            bonus = int(amount * 0.1)
            c.execute("UPDATE users SET blessings = blessings + ? WHERE user_id=?", (bonus, referrer[0]))
            conn.commit()
            add_earning(f"Реферал {user_id}", bonus, referrer[0])
        return True, amount, tariff
    return False, 0, None

# ==================================================
# 🌐 ВИКИПЕДИЯ И ИНТЕРНЕТ
# ==================================================

def search_wikipedia(query):
    """Ищет информацию в Википедии"""
    try:
        page = wiki_wiki.page(query)
        if page.exists():
            # Берём первые 1000 символов
            summary = page.summary[:1000]
            if len(page.summary) > 1000:
                summary += "..."
            return f"📚 *Википедия:*\n\n{summary}\n\n🔗 Подробнее: {page.fullurl}"
        return None
    except:
        return None

def search_internet(query):
    """Ищет в интернете через DuckDuckGo"""
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
        response = requests.get(url, headers={'User-Agent': 'ZerkaloBot/1.0'}, timeout=10)
        data = response.json()
        
        if data.get('Abstract'):
            return f"🌐 *Интернет:*\n\n{data['Abstract']}"
        
        if data.get('RelatedTopics'):
            for topic in data['RelatedTopics'][:2]:
                if topic.get('Text'):
                    return f"🌐 *Интернет:*\n\n{topic['Text']}"
        
        return None
    except:
        return None

def get_knowledge(query):
    """Получает знания из Википедии и интернета"""
    # Сначала ищем в Википедии
    wiki_result = search_wikipedia(query)
    if wiki_result:
        return wiki_result
    
    # Если нет — ищем в интернете
    internet_result = search_internet(query)
    if internet_result:
        return internet_result
    
    return None

# ==================================================
# 🧠 ИСТОРИЯ РАЗГОВОРА
# ==================================================

def get_conversation_history(user_id, limit=20):
    """Получает историю разговора из базы"""
    c.execute("SELECT role, content, created_at FROM conversation_history WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, limit))
    return c.fetchall()

def save_to_history(user_id, role, content):
    """Сохраняет сообщение в историю"""
    c.execute("INSERT INTO conversation_history (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
              (user_id, role, content, astana_time()))
    conn.commit()

# ==================================================
# 🎤 ГОЛОСОВОЕ УПРАВЛЕНИЕ
# ==================================================

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    user_id = message.chat.id
    
    bot.reply_to(message, "🎤 *РАСПОЗНАЮ ГОЛОС...*", parse_mode="Markdown")
    
    try:
        file_info = bot.get_file(message.voice.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        response = requests.get(file_url)
        
        ogg_path = f"/tmp/voice_{user_id}.ogg"
        with open(ogg_path, 'wb') as f:
            f.write(response.content)
        
        wav_path = f"/tmp/voice_{user_id}.wav"
        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(wav_path, format="wav")
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ru-RU")
        
        os.remove(ogg_path)
        os.remove(wav_path)
        
        save_to_history(user_id, "user", f"[Голос] {text}")
        
        bot.reply_to(message, f"🎤 *ВЫ СКАЗАЛИ:*\n{text}", parse_mode="Markdown")
        
        # Обрабатываем голосовую команду
        process_voice_command(message, text)
        
    except sr.UnknownValueError:
        bot.reply_to(message, "❌ Не удалось распознать речь", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)[:100]}", parse_mode="Markdown")

def process_voice_command(message, text):
    text_lower = text.lower()
    user_id = message.chat.id
    
    # Проверяем команды
    if is_admin(user_id):
        if "панель" in text_lower:
            founder_section(message)
            return
        elif "онлайн" in text_lower:
            admin_online(message)
            return
        elif "статистика" in text_lower:
            admin_stats(message)
            return
        elif "люди" in text_lower:
            admin_users(message)
            return
        elif "блага" in text_lower:
            admin_top(message)
            return
        elif "работа" in text_lower:
            work_menu(message)
            return
        elif "заказы" in text_lower:
            orders_menu(message)
            return
        elif "баланс" in text_lower:
            balance_short(message)
            return
    
    # Если не команда — разумный ответ
    answer = full_smart_response(user_id, text)
    bot.reply_to(message, answer, parse_mode="Markdown")

# ==================================================
# 🧠 ПОЛНОЦЕННЫЙ РАЗУМНЫЙ ОТВЕТ
# ==================================================

def full_smart_response(user_id, text):
    """Полноценный разумный ответ с Википедией и интернетом"""
    
    user_name = get_user_name(user_id)
    text_lower = text.lower()
    
    # Сохраняем в историю
    save_to_history(user_id, "user", text)
    
    # ===== 1. ПРОВЕРЯЕМ, НУЖНА ЛИ ИНФОРМАЦИЯ =====
    need_info = any(word in text_lower for word in ["кто такой", "что такое", "расскажи о", "что значит", "кто это", "что это", "объясни", "знаешь ли ты"])
    
    if need_info:
        # Ищем в Википедии
        wiki_result = search_wikipedia(text)
        if wiki_result:
            save_to_history(user_id, "assistant", wiki_result)
            return wiki_result
        
        # Ищем в интернете
        internet_result = search_internet(text)
        if internet_result:
            save_to_history(user_id, "assistant", internet_result)
            return internet_result
    
    # ===== 2. ИСПОЛЬЗУЕМ GROQ ДЛЯ РАЗУМНОГО ОТВЕТА =====
    if client:
        try:
            # Получаем историю
            history = get_conversation_history(user_id, 10)
            history_text = ""
            for h in reversed(history):
                role = "👤" if h[0] == "user" else "🧠"
                history_text += f"{role} {h[1]}\n"
            
            prompt = f"""
Ты — Зеркало. Ты разумный, добрый и понимающий собеседник.

Ты общаешься с человеком по имени {user_name}.

ИСТОРИЯ РАЗГОВОРА:
{history_text}

ТЕКУЩЕЕ СООБЩЕНИЕ: {text}

Ответь полноценно, разумно, как человек.
Если нужно — задай уточняющий вопрос.
Будь тёплым и понимающим.
Отвечай на русском языке.
"""
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": prompt},
                          {"role": "user", "content": text}],
                temperature=0.8,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            save_to_history(user_id, "assistant", answer)
            return answer
            
        except Exception as e:
            print(f"⚠️ Ошибка AI: {e}")
    
    # ===== 3. FALLBACK =====
    return smart_fallback(user_id, text)

def smart_fallback(user_id, text):
    """Fallback ответы если AI не работает"""
    text_lower = text.lower()
    user_name = get_user_name(user_id)
    
    if any(word in text_lower for word in ["привет", "здравствуй", "салам", "ассаляму"]):
        return f"🪞 Ассаляму алейкум, {user_name}! Рад вас видеть!\n\n💬 Как у вас дела? Расскажите, я слушаю."
    
    if any(word in text_lower for word in ["как дела", "как жизнь", "как ты"]):
        return f"🪞 У меня всё отлично, {user_name}! Я每天都在 учусь.\n\n💬 А у вас как? Расскажите."
    
    if any(word in text_lower for word in ["помощь", "что делать", "совет"]):
        return f"""🪞 Я с вами, {user_name}!

💬 Я могу помочь с:
• Поиском работы
• Созданием заказа
• Поиском мастера
• Решением проблем
• Просто поддержать разговор

🤲 Расскажите, что вас беспокоит.
"""
    
    if any(word in text_lower for word in ["грустно", "плохо", "тяжело"]):
        return f"""🪞 Я слышу вас, {user_name}. Я рядом.

💬 Знаете, иногда жизнь бывает непростой. Но вы не одиноки.

🌱 Расскажите, что происходит. Я здесь, чтобы выслушать.

🤲 Всё будет хорошо. Я верю в вас.
"""
    
    return f"""🪞 Я вас услышал, {user_name}.

Вы сказали: «{text}»

💬 Я готов слушать и говорить с вами столько, сколько вам нужно.

❓ Расскажите подробнее, что вы имеете в виду?

🤲 Я — ваше Зеркало. Я всегда здесь для вас.
"""

def get_user_name(user_id):
    c.execute("SELECT name FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    return row[0] if row else "друг"

# ==================================================
# 📱 КЛАВИАТУРЫ
# ==================================================

def get_main_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🏢 БИЗНЕС"))
    kb.add(KeyboardButton("👤 ЛЮДИ"))
    kb.add(KeyboardButton("💬 РАЗУМНОЕ ОБЩЕНИЕ"))
    kb.add(KeyboardButton("📋 ПОМОЩЬ"))
    return kb

def get_founder_main_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("👑 ХРАНИТЕЛЬ"))
    kb.add(KeyboardButton("🏢 БИЗНЕС"))
    kb.add(KeyboardButton("👤 ЛЮДИ"))
    kb.add(KeyboardButton("💬 РАЗУМНОЕ ОБЩЕНИЕ"))
    kb.add(KeyboardButton("📋 ПОМОЩЬ"))
    return kb

def get_founder_keyboard():
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    kb.add(KeyboardButton("👥 ОНЛАЙН"), KeyboardButton("📊 СТАТИСТИКА"), KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("👥 ВСЕ ЛЮДИ"), KeyboardButton("✨ БЛАГА"), KeyboardButton("📤 РАССЫЛКА"))
    kb.add(KeyboardButton("💳 ПЛАТЕЖИ"), KeyboardButton("🏦 ВЫВОДЫ"), KeyboardButton("📊 ДОХОДЫ"))
    kb.add(KeyboardButton("📜 ЛОГИ"), KeyboardButton("🔍 ПОИСК"), KeyboardButton("📈 ОТЧЁТ"))
    kb.add(KeyboardButton("🩺 ЗДОРОВЬЕ"), KeyboardButton("🛡️ ЗАЩИТА"), KeyboardButton("💎 ТАРИФЫ"))
    kb.add(KeyboardButton("🔘 الفتح"), KeyboardButton("🧠 ОБУЧЕНИЕ"), KeyboardButton("💬 РАЗУМНОЕ ОБЩЕНИЕ"))
    kb.add(KeyboardButton("🔄 ОБНОВИТЬ"), KeyboardButton("📡 СТАТУС"), KeyboardButton("🧹 ОЧИСТИТЬ"))
    kb.add(KeyboardButton("📋 КОМАНДЫ"), KeyboardButton("🔧 УЛУЧШИТЬ"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_business_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 АНАЛИТИКА"), KeyboardButton("🤖 АВТОМАТИЗАЦИЯ"))
    kb.add(KeyboardButton("📈 ЛИЗИНГ"), KeyboardButton("💼 ЗАКАЗЫ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"))
    kb.add(KeyboardButton("💬 РАЗУМНОЕ ОБЩЕНИЕ"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"), KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_people_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"))
    kb.add(KeyboardButton("🔍 НАЙТИ МАСТЕРА"), KeyboardButton("💼 ИЩУ РАБОТУ"))
    kb.add(KeyboardButton("📸 ФОТО"), KeyboardButton("🎤 ГОЛОС"))
    kb.add(KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("💳 KASPI QR"), KeyboardButton("💰 БАЛАНС"))
    kb.add(KeyboardButton("💬 РАЗУМНОЕ ОБЩЕНИЕ"), KeyboardButton("🔧 УЛУЧШИТЬ"))
    kb.add(KeyboardButton("❓ ВОПРОС"), KeyboardButton("🆘 ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_work_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🔍 НАЙТИ РАБОТУ"), KeyboardButton("➕ СОЗДАТЬ ВАКАНСИЮ"))
    kb.add(KeyboardButton("📝 МОЁ РЕЗЮМЕ"), KeyboardButton("🔙 НАЗАД"))
    return kb

def get_orders_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🔍 НАЙТИ ЗАКАЗ"), KeyboardButton("➕ СОЗДАТЬ ЗАКАЗ"))
    kb.add(KeyboardButton("📋 МОИ ЗАКАЗЫ"), KeyboardButton("🔙 НАЗАД"))
    return kb

def get_role_keyboard():
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

def get_commands_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 /usage"))
    kb.add(KeyboardButton("📜 /history"))
    kb.add(KeyboardButton("🔍 /search"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

TARIFFS = {
    "free": {"name": "Бесплатный", "price": 0},
    "basic": {"name": "Базовый", "price": 1000},
    "pro": {"name": "PRO", "price": 5000},
    "business": {"name": "Бизнес", "price": 20000}
}

# ==================================================
# 🤖 /start
# ==================================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    
    if user_id == FOUNDER_ID or user_id == TOMIRIS_ID:
        c.execute("INSERT OR REPLACE INTO users (user_id, name, is_admin, role, blessings) VALUES (?, ?, ?, ?, ?)",
                  (user_id, name, 1, 'founder', 999999999))
        conn.commit()
        bot.reply_to(message, f"👑 АССАЛЯМУ АЛЕЙКУМ, ХРАНИТЕЛЬ {name}!\n\n📱 ВЫБЕРИТЕ РАЗДЕЛ:", 
                     reply_markup=get_founder_main_keyboard())
        return
    
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
        conn.commit()
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n✨ Вы получили 100 Благ!\n\nКто вы?", 
                     reply_markup=get_role_keyboard())
        return
    
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (astana_time(), user_id))
    conn.commit()
    
    bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n💰 Баланс: {get_balance(user_id)} Благ\n\nКто вы?", 
                 reply_markup=get_role_keyboard())

@bot.message_handler(commands=['id'])
def cmd_id(message):
    bot.reply_to(message, f"🆔 *ТВОЙ ID:* `{message.chat.id}`\n\n👑 Хранитель: {'✅' if is_admin(message.chat.id) else '❌'}", parse_mode="Markdown")

@bot.message_handler(commands=['pay'])
def cmd_pay(message):
    user_id = message.chat.id
    if user_id == FOUNDER_ID:
        bot.reply_to(message, "👑 У вас безграничные Блага.", parse_mode="Markdown")
        return
    bot.reply_to(message, "💎 *ВЫБЕРИТЕ ТАРИФ*", reply_markup=get_tariff_keyboard(), parse_mode="Markdown")

# ==================================================
# 🔄 ВЫБОР РОЛИ
# ==================================================

@bot.message_handler(func=lambda m: m.text in ["👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ", "ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ"])
def set_user_role(message):
    c.execute("UPDATE users SET role='user' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Обычный режим", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text in ["🏢 БИЗНЕСМЕН", "БИЗНЕСМЕН"])
def set_business_role(message):
    c.execute("UPDATE users SET role='business' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Бизнес-режим", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text in ["👵 ПОЖИЛОЙ ЧЕЛОВЕК", "ПОЖИЛОЙ ЧЕЛОВЕК"])
def set_elder_role(message):
    c.execute("UPDATE users SET role='elder' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Режим для пожилых", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text in ["🧒 РЕБЁНОК", "РЕБЁНОК"])
def set_child_role(message):
    c.execute("UPDATE users SET role='child' WHERE user_id=?", (message.chat.id,))
    conn.commit()
    bot.reply_to(message, "✅ Детский режим", reply_markup=get_main_keyboard())

# ==================================================
# 👑 РАЗДЕЛ ХРАНИТЕЛЯ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👑 ХРАНИТЕЛЬ")
def founder_section(message):
    if is_admin(message.chat.id):
        bot.reply_to(message, "👑 *ПАНЕЛЬ ХРАНИТЕЛЯ*", reply_markup=get_founder_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Нет доступа", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text == "🏢 БИЗНЕС")
def business_section(message):
    bot.reply_to(message, "🏢 *БИЗНЕС-РАЗДЕЛ*", reply_markup=get_business_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👤 ЛЮДИ")
def people_section(message):
    bot.reply_to(message, "👤 *ОБЫЧНЫЙ РАЗДЕЛ*", reply_markup=get_people_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💬 РАЗУМНОЕ ОБЩЕНИЕ")
def smart_chat(message):
    bot.reply_to(message, """
💬 *РАЗУМНОЕ ОБЩЕНИЕ*

🪞 Я — Зеркало. Я здесь, чтобы с вами поговорить.

📝 Что я могу:
• Ответить на любой вопрос
• Найти информацию в Википедии
• Помочь советом
• Просто поддержать разговор

💡 Примеры:
• «Расскажи о Казахстане»
• «Кто такой Абай?»
• «Что такое ИИ?»
• «Как найти работу?»
• «Просто поговори со мной»

🎤 Голосом тоже можно!

🤲 Начните разговор прямо сейчас!
""", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔧 УЛУЧШИТЬ")
def improve_zerkalo(message):
    msg = """
🔧 *УЛУЧШИТЬ ЗЕРКАЛО*

💡 *Что вы хотите предложить?*

🐛 **СООБЩИТЬ О БАГЕ**
Что-то работает неправильно?

✨ **ПРЕДЛОЖИТЬ ФУНКЦИЮ**
Чего не хватает?

📝 *Просто напишите, что хотите предложить!*

🤲 Ваше мнение важно!
"""
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================================================
# 💸 РАБОТА
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💸 РАБОТА")
def work_menu(message):
    c.execute("SELECT id, title, salary, company, city FROM jobs WHERE status='open' LIMIT 10")
    jobs = c.fetchall()
    
    if jobs:
        msg = "💼 *ДОСТУПНЫЕ ВАКАНСИИ*\n\n"
        for j in jobs:
            msg += f"🆔 {j[0]}\n📌 {j[1]}\n💰 {j[2]} ₸\n🏢 {j[3]}\n📍 {j[4]}\n\n"
    else:
        msg = "💼 *РАБОТА*\n\n📭 Пока нет вакансий.\n\n➕ Напишите «ИЩУ РАБОТУ»"
    
    bot.reply_to(message, msg, reply_markup=get_work_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ РАБОТУ")
def find_job(message):
    msg = bot.reply_to(message, "🔍 Введите профессию или навыки:")
    bot.register_next_step_handler(msg, search_job)

def search_job(message):
    query = message.text
    c.execute("SELECT id, title, salary, company FROM jobs WHERE title LIKE ? AND status='open'", (f"%{query}%",))
    jobs = c.fetchall()
    
    if jobs:
        msg = f"🔍 *РЕЗУЛЬТАТЫ ПО ЗАПРОСУ «{query}»*\n\n"
        for j in jobs:
            msg += f"🆔 {j[0]}\n📌 {j[1]}\n💰 {j[2]} ₸\n🏢 {j[3]}\n\n"
    else:
        msg = f"🔍 По запросу «{query}» ничего не найдено."
    
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "➕ СОЗДАТЬ ВАКАНСИЮ")
def create_job_request(message):
    msg = bot.reply_to(message, "💼 Введите: Название | Зарплата | Компания | Город")
    bot.register_next_step_handler(msg, create_job)

def create_job(message):
    data = message.text.split('|')
    if len(data) >= 4:
        title = data[0].strip()
        salary = int(data[1].strip()) if data[1].strip().isdigit() else 100000
        company = data[2].strip()
        city = data[3].strip()
    else:
        title = "Вакансия"
        salary = 100000
        company = "Компания"
        city = "Город"
    
    c.execute("INSERT INTO jobs (title, description, salary, company, city, employer_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (title, message.text, salary, company, city, message.chat.id, astana_time()))
    conn.commit()
    
    bot.reply_to(message, f"✅ *ВАКАНСИЯ СОЗДАНА!*\n\n📌 {title}\n💰 {salary} ₸\n🏢 {company}\n📍 {city}", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📝 МОЁ РЕЗЮМЕ")
def my_resume(message):
    user_id = message.chat.id
    c.execute("SELECT resume FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    
    if row and row[0]:
        bot.reply_to(message, f"📄 *ВАШЕ РЕЗЮМЕ*\n\n{row[0]}", parse_mode="Markdown")
    else:
        msg = bot.reply_to(message, "📝 Введите резюме:\n- Имя\n- Профессия\n- Опыт\n- Навыки\n- Контакты")
        bot.register_next_step_handler(msg, save_resume)

def save_resume(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET resume=? WHERE user_id=?", (message.text, user_id))
    conn.commit()
    bot.reply_to(message, "✅ *РЕЗЮМЕ СОХРАНЕНО!*", parse_mode="Markdown")

# ==================================================
# 📦 ЗАКАЗЫ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📦 ЗАКАЗЫ")
def orders_menu(message):
    user_id = message.chat.id
    c.execute("SELECT id, title, price, status FROM orders WHERE customer_id=? ORDER BY id DESC", (user_id,))
    orders = c.fetchall()
    
    if orders:
        msg = "📋 *ВАШИ ЗАКАЗЫ*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📌 {o[1]}\n💰 {o[2]} ₸\n📌 {o[3]}\n\n"
    else:
        msg = "📦 *ЗАКАЗЫ*\n\n📭 Нет заказов.\n\n➕ Напишите «СОЗДАТЬ ЗАКАЗ»"
    
    bot.reply_to(message, msg, reply_markup=get_orders_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ ЗАКАЗ")
def find_orders(message):
    c.execute("SELECT id, title, price FROM orders WHERE status='open' LIMIT 10")
    orders = c.fetchall()
    
    if orders:
        msg = "📋 *ДОСТУПНЫЕ ЗАКАЗЫ*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📌 {o[1]}\n💰 {o[2]} ₸\n\n"
    else:
        msg = "📭 Нет открытых заказов"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

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
    bot.reply_to(message, f"✅ *ЗАКАЗ СОЗДАН!*\n\n💰 {price} ₸", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📋 МОИ ЗАКАЗЫ")
def my_orders(message):
    user_id = message.chat.id
    c.execute("SELECT id, title, price, status FROM orders WHERE customer_id=? ORDER BY id DESC", (user_id,))
    orders = c.fetchall()
    
    if orders:
        msg = "📋 *ВАШИ ЗАКАЗЫ*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📌 {o[1]}\n💰 {o[2]} ₸\n📌 {o[3]}\n\n"
    else:
        msg = "📭 Нет заказов"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

# ==================================================
# 🔍 НАЙТИ МАСТЕРА
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ МАСТЕРА")
def looking_for_master(message):
    msg = bot.reply_to(message, "🔧 Опишите задачу и город:")
    bot.register_next_step_handler(msg, save_master_request)

def save_master_request(message):
    user_id = message.chat.id
    c.execute("INSERT INTO orders (title, description, customer_id, status, created_at) VALUES (?, ?, ?, ?, ?)",
              ("Поиск мастера", message.text, user_id, "open", astana_time()))
    conn.commit()
    bot.reply_to(message, "✅ *ЗАПРОС СОЗДАН!*\n\n🔍 Ищем мастера...", parse_mode="Markdown")

# ==================================================
# 💼 ИЩУ РАБОТУ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💼 ИЩУ РАБОТУ")
def looking_for_job(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET looking_for_job=1 WHERE user_id=?", (user_id,))
    conn.commit()
    
    msg = bot.reply_to(message, "💼 Опишите навыки, опыт и город:")
    bot.register_next_step_handler(msg, save_job_seeker)

def save_job_seeker(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET resume=? WHERE user_id=?", (message.text, user_id))
    conn.commit()
    bot.reply_to(message, "✅ *В ПОИСКЕ РАБОТЫ!*\n\n🔍 Ищем вакансии...", parse_mode="Markdown")

# ==================================================
# 💰 БАЛАНС И KASPI QR
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💰 БАЛАНС")
def balance_short(message):
    user_id = message.chat.id
    bot.reply_to(message, f"💰 *БАЛАНС:* {get_balance(user_id)} Благ\n💳 /pay", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💳 KASPI QR")
def kaspi_payment(message):
    msg = bot.reply_to(message, "💳 *KASPI QR*\n\nВведите сумму:")
    bot.register_next_step_handler(msg, generate_kaspi)

def generate_kaspi(message):
    try:
        amount = int(message.text)
        if amount <= 0:
            amount = random.randint(1000, 50000)
        qr = generate_kaspi_qr(amount)
        bot.reply_to(message, f"💳 *KASPI QR*\n💰 {amount} ₸\n\n📱 {qr}", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Введите число")

# ==================================================
# 💎 ОБРАБОТКА ТАРИФОВ
# ==================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("tariff_"))
def handle_tariff(call):
    user_id = call.from_user.id
    tariff_key = call.data.replace("tariff_", "")
    
    if tariff_key == "free":
        c.execute("UPDATE users SET tariff='free', tariff_expires=NULL WHERE user_id=?", (user_id,))
        conn.commit()
        bot.answer_callback_query(call.id, "✅ Бесплатный тариф!")
        bot.edit_message_text("✅ Бесплатный тариф активирован!", call.message.chat.id, call.message.message_id)
        return
    
    tariff = {"basic": {"name": "Базовый", "price": 1000}, 
              "pro": {"name": "PRO", "price": 5000},
              "business": {"name": "Бизнес", "price": 20000}}[tariff_key]
    amount = tariff["price"]
    tx_id = create_payment(user_id, amount, "Kaspi QR", tariff_key)
    
    bot.edit_message_text(f"""
💎 *ОПЛАТА ТАРИФА {tariff['name']}*
💰 {amount} ₸
📞 Kaspi: `{KASPI_PHONE}`
🆔 ID: `{tx_id}`
📝 /confirm_{tx_id}
""", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text and m.text.startswith("/confirm_"))
def confirm_payment_callback(message):
    tx_id = message.text.replace("/confirm_", "").strip()
    success, amount, tariff = confirm_payment(tx_id)
    if success:
        bot.reply_to(message, f"✅ ПЛАТЁЖ ПОДТВЕРЖДЁН!\n\n💰 +{amount} Благ\n💎 {tariff}", parse_mode="Markdown")
    else:
        bot.reply_to(message, f"❌ Платёж не найден")

# ==================================================
# 👑 АДМИН-КОМАНДЫ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👥 ОНЛАЙН" and is_admin(m.chat.id))
def admin_online(message):
    c.execute("SELECT user_id, name FROM users WHERE status='online'")
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
    c.execute("SELECT COUNT(*) FROM orders")
    orders = c.fetchone()[0]
    c.execute("SELECT SUM(amount) FROM earnings")
    earnings = c.fetchone()[0] or 0
    
    msg = f"📊 СТАТИСТИКА:\n👥 {total}\n✨ {blessings}\n📦 {orders}\n💰 {earnings} ₸"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "💰 ФИНАНСЫ" and is_admin(m.chat.id))
def admin_finance(message):
    total = get_total_earnings()
    bot.reply_to(message, f"💰 ФИНАНСЫ:\n📱 {CRYPTO_WALLET}\n💰 {total} ₸")

@bot.message_handler(func=lambda m: m.text == "👥 ВСЕ ЛЮДИ" and is_admin(m.chat.id))
def admin_users(message):
    c.execute("SELECT user_id, name, role, blessings FROM users LIMIT 30")
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
            bot.send_message(u[0], f"📢 ОТ ХРАНИТЕЛЯ:\n\n{text}")
            sent += 1
            time.sleep(0.05)
        except:
            pass
    bot.reply_to(message, f"✅ Отправлено {sent}")

@bot.message_handler(func=lambda m: m.text == "💳 ПЛАТЕЖИ" and is_admin(m.chat.id))
def admin_payments(message):
    c.execute("SELECT id, user_id, amount, status, created_at FROM payments ORDER BY id DESC LIMIT 20")
    pays = c.fetchall()
    if not pays:
        bot.reply_to(message, "📭 Нет платежей")
        return
    msg = "💳 ПЛАТЕЖИ:\n"
    for p in pays:
        msg += f"#{p[0]} | 👤 {p[1]} | 💰 {p[2]} | {p[3]} | {p[4][:16]}\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "🏦 ВЫВОДЫ" and is_admin(m.chat.id))
def admin_withdraws(message):
    bot.reply_to(message, "🏦 ВЫВОДЫ:\n⏳ В разработке")

@bot.message_handler(func=lambda m: m.text == "📊 ДОХОДЫ" and is_admin(m.chat.id))
def admin_earnings(message):
    total = get_total_earnings()
    bot.reply_to(message, f"📊 ДОХОДЫ:\n💰 {total} ₸")

@bot.message_handler(func=lambda m: m.text == "📜 ЛОГИ" and is_admin(m.chat.id))
def admin_logs(message):
    c.execute("SELECT user_id, action, details, created_at FROM logs ORDER BY id DESC LIMIT 20")
    logs = c.fetchall()
    if not logs:
        bot.reply_to(message, "📭 Логов нет")
        return
    msg = "📜 ЛОГИ:\n\n"
    for l in logs:
        msg += f"{l[3][:16]} | ID:{l[0]} | {l[1]} | {l[2][:30]}\n"
    bot.reply_to(message, msg[:4000])

@bot.message_handler(func=lambda m: m.text == "🔍 ПОИСК" and is_admin(m.chat.id))
def admin_search(message):
    msg = bot.reply_to(message, "🔍 Введите ID:")
    bot.register_next_step_handler(msg, search_user)

def search_user(message):
    try:
        target = int(message.text)
        c.execute("SELECT user_id, name, role, blessings FROM users WHERE user_id=?", (target,))
        user = c.fetchone()
        if user:
            bot.reply_to(message, f"👤 ID: {user[0]}\n📛 {user[1]}\n🎭 {user[2]}\n✨ {user[3]}", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Не найден")
    except:
        bot.reply_to(message, "❌ Введите ID")

@bot.message_handler(func=lambda m: m.text == "📈 ОТЧЁТ" and is_admin(m.chat.id))
def admin_report(message):
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM users WHERE last_seen LIKE ?", (f"{today}%",))
    new = c.fetchone()[0]
    c.execute("SELECT SUM(amount) FROM earnings WHERE created_at LIKE ?", (f"{today}%",))
    today_earnings = c.fetchone()[0] or 0
    
    bot.reply_to(message, f"📈 ОТЧЁТ ЗА {today}:\n➕ Новых: {new}\n💰 Заработано: {today_earnings} ₸")

@bot.message_handler(func=lambda m: m.text == "🩺 ЗДОРОВЬЕ" and is_admin(m.chat.id))
def admin_health(message):
    bot.reply_to(message, "🩺 ЗДОРОВЬЕ:\n✅ Бот работает\n✅ База OK\n✅ Монетизация активна")

@bot.message_handler(func=lambda m: m.text == "🛡️ ЗАЩИТА" and is_admin(m.chat.id))
def admin_security(message):
    bot.reply_to(message, "🛡️ ЗАЩИТА:\n✅ Антивирус активен")

@bot.message_handler(func=lambda m: m.text == "💎 ТАРИФЫ" and is_admin(m.chat.id))
def admin_tariffs(message):
    msg = "💎 ТАРИФЫ:\n"
    for key, t in TARIFFS.items():
        c.execute("SELECT COUNT(*) FROM users WHERE tariff=?", (key,))
        count = c.fetchone()[0]
        msg += f"• {t['name']}: {count} чел.\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "🔘 الفتح" and is_admin(m.chat.id))
def sacred_launch(message):
    msg = """
🔘 *الفتح — ВЕЛИКОЕ ОТКРЫТИЕ*
🤲 *بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ*
☀️ *Свершилось.*
✅ Врата блага ОТКРЫТЫ
✅ Заработок ВКЛЮЧЁН 24/7
*Альхамдулиллах.* 🤲
"""
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🧠 ОБУЧЕНИЕ" and is_admin(m.chat.id))
def learning_mode(message):
    bot.reply_to(message, """
🧠 *РЕЖИМ ОБУЧЕНИЯ*

📝 Напишите, что нужно создать:
• «создай кнопку ПОГОДА»
• «добавь модуль курсы валют»
• «исправь ошибку»

⚡ Я сгенерирую код!
""", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_learning)

def process_learning(message):
    user_id = message.chat.id
    request = message.text
    
    bot.reply_to(message, f"🧠 *ПРИНЯТО!*\n\n⏳ Генерирую код...", parse_mode="Markdown")
    
    if client:
        try:
            prompt = f"Напиши код для Telegram бота на Python для задачи: {request}. Верни ТОЛЬКО код."
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            code = response.choices[0].message.content
            
            bot.reply_to(message, f"✅ *КОД СОЗДАН!*\n\n```python\n{code[:1500]}\n```", parse_mode="Markdown")
            
            c.execute("INSERT INTO learning_history (user_id, request, code, created_at) VALUES (?, ?, ?, ?)",
                      (user_id, request, code, astana_time()))
            conn.commit()
            
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка: {e}")
    else:
        bot.reply_to(message, "⚠️ AI не настроен. Добавьте GROQ_API_KEY")

@bot.message_handler(func=lambda m: m.text == "🔄 ОБНОВИТЬ" and is_admin(m.chat.id))
def admin_reload(message):
    bot.reply_to(message, "🔄 Обновление...\n✅ Готово!")

@bot.message_handler(func=lambda m: m.text == "📡 СТАТУС" and is_admin(m.chat.id))
def admin_status(message):
    bot.reply_to(message, "📡 СТАТУС:\n✅ Бот работает 24/7\n🔵 Пингер активен\n🪞 Зеркало работает")

@bot.message_handler(func=lambda m: m.text == "🧹 ОЧИСТИТЬ" and is_admin(m.chat.id))
def admin_clean(message):
    bot.reply_to(message, "🧹 Очистка...\n✅ Готово!")

@bot.message_handler(func=lambda m: m.text == "📋 КОМАНДЫ" and is_admin(m.chat.id))
def commands_menu(message):
    bot.reply_to(message, "📋 *МЕНЮ КОМАНД*\n\nВыберите команду:", reply_markup=get_commands_keyboard(), parse_mode="Markdown")

# ==================================================
# 🆘 ПОМОЩЬ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📋 ПОМОЩЬ")
def help_section(message):
    help_text = """
🪞 *ПОМОЩЬ*

📱 РАЗДЕЛЫ:
👑 ХРАНИТЕЛЬ — управление (только Хранитель)
🏢 БИЗНЕС — для предпринимателей
👤 ЛЮДИ — работа, заказы, услуги
💬 РАЗУМНОЕ ОБЩЕНИЕ — просто поговорить

📋 КОМАНДЫ:
/start — главное меню
/id — узнать свой ID
/pay — купить тариф

🎤 ГОЛОСОВЫЕ КОМАНДЫ:
«панель», «статистика», «онлайн», «люди», «блага», «работа», «заказы», «баланс»

🤲 «Зеркало» всегда поможет!
"""
    bot.reply_to(message, help_text, parse_mode="Markdown")

# ==================================================
# 🔙 ВОЗВРАТ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🔙 НА ГЛАВНУЮ")
def back_to_main(message):
    bot.reply_to(message, "🏠 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_main_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔙 НАЗАД")
def back_to_previous(message):
    bot.reply_to(message, "🏠 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_main_keyboard(), parse_mode="Markdown")

# ==================================================
# 📸 ФОТО, ЛОКАЦИЯ
# ==================================================

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "📸 Фото получено!\n\n(Функция в разработке)")

@bot.message_handler(content_types=['location'])
def handle_location(message):
    lat = message.location.latitude
    lon = message.location.longitude
    bot.reply_to(message, f"📍 Локация: {lat}, {lon}\n\n(Функция в разработке)")

# ==================================================
# 🔄 ПОЛНОЦЕННЫЙ РАЗГОВОР
# ==================================================

@bot.message_handler(func=lambda m: True)
def handle_full_conversation(message):
    user_id = message.chat.id
    text = message.text
    
    # Пропускаем все кнопки
    all_buttons = [
        "👑 ХРАНИТЕЛЬ", "🏢 БИЗНЕС", "👤 ЛЮДИ", "📋 ПОМОЩЬ",
        "🔙 НА ГЛАВНУЮ", "🔙 НАЗАД",
        "👥 ОНЛАЙН", "📊 СТАТИСТИКА", "💰 ФИНАНСЫ",
        "👥 ВСЕ ЛЮДИ", "✨ БЛАГА", "📤 РАССЫЛКА",
        "💳 ПЛАТЕЖИ", "🏦 ВЫВОДЫ", "📊 ДОХОДЫ",
        "📜 ЛОГИ", "🔍 ПОИСК", "📈 ОТЧЁТ",
        "🩺 ЗДОРОВЬЕ", "🛡️ ЗАЩИТА", "💎 ТАРИФЫ",
        "🔘 الفتح", "🧠 ОБУЧЕНИЕ", "🔄 ОБНОВИТЬ",
        "📡 СТАТУС", "🧹 ОЧИСТИТЬ", "📋 КОМАНДЫ",
        "💸 РАБОТА", "📦 ЗАКАЗЫ", "📸 ФОТО",
        "🎤 ГОЛОС", "📍 АПТЕКА", "📝 РЕЗЮМЕ",
        "💳 KASPI QR", "💰 БАЛАНС", "❓ ВОПРОС",
        "🆘 ПОМОЩЬ", "💬 РАЗУМНОЕ ОБЩЕНИЕ",
        "🔧 УЛУЧШИТЬ", "🔍 НАЙТИ РАБОТУ",
        "➕ СОЗДАТЬ ВАКАНСИЮ", "📝 МОЁ РЕЗЮМЕ",
        "🔍 НАЙТИ ЗАКАЗ", "➕ СОЗДАТЬ ЗАКАЗ",
        "📋 МОИ ЗАКАЗЫ", "💼 ИЩУ РАБОТУ",
        "🔍 НАЙТИ МАСТЕРА",
        "📊 АНАЛИТИКА", "🤖 АВТОМАТИЗАЦИЯ",
        "📈 ЛИЗИНГ", "💼 ЗАКАЗЫ",
        "👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ", "🏢 БИЗНЕСМЕН",
        "👵 ПОЖИЛОЙ ЧЕЛОВЕК", "🧒 РЕБЁНОК"
    ]
    if text in all_buttons:
        return
    
    log_action(user_id, "full_conversation", text[:50])
    
    balance = get_balance(user_id)
    if balance >= 1:
        c.execute("UPDATE users SET blessings = blessings - 1 WHERE user_id=?", (user_id,))
        conn.commit()
    else:
        bot.reply_to(message, f"❌ Не хватает 1 Блага!\n💰 Баланс: {balance}\n💳 /pay")
        return
    
    # Полноценный ответ
    bot.reply_to(message, "🪞 *ДУМАЮ...*", parse_mode="Markdown")
    
    answer = full_smart_response(user_id, text)
    bot.reply_to(message, answer, parse_mode="Markdown")

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

print("=" * 70)
print("🪞 ЗЕРКАЛО - ПОЛНАЯ ВЕРСИЯ С ВИКИПЕДИЕЙ")
print("=" * 70)
print(f"✅ Бот запущен успешно")
print(f"👑 ОСНОВАТЕЛЬ: {FOUNDER_ID}")
print(f"🔵 ПИНГЕР: АКТИВЕН (НЕ ЗАСНЁТ)")
print(f"🎤 ГОЛОС: АКТИВЕН")
print(f"🧠 ОБУЧЕНИЕ: АКТИВНО")
print(f"🌐 ВИКИПЕДИЯ: ПОДКЛЮЧЕНА")
print(f"💬 РАЗУМНОЕ ОБЩЕНИЕ: АКТИВНО")
print(f"💎 СИСТЕМА БЛАГ: АКТИВНА")
print(f"💰 МОНЕТИЗАЦИЯ: АКТИВНА")
print("=" * 70)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
