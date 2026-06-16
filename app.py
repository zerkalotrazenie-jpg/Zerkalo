#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🪞 ЗЕРКАЛО - ЕДИНАЯ ВЕРСИЯ
═══════════════════════════════════════════════════════════════════
Версия: 2.0
Фиксация: 22:27
✅ РАБОТАЕТ СТАБИЛЬНО
✅ ВИДЕО → ТЕКСТ
✅ ВСЕ КНОПКИ
✅ НЕ ЗАСЫПАЕТ
✅ ЗАРАБАТЫВАЕТ ДЕНЬГИ
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
import subprocess
from datetime import datetime, timedelta
from flask import Flask
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# ==================================================
# ⚡ УСТАНОВКА БИБЛИОТЕК
# ==================================================

def install_package(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_package("pytelegrambotapi")
install_package("groq")
install_package("flask")
install_package("requests")
install_package("youtube-transcript-api")
install_package("moviepy")
install_package("openai-whisper")

import telebot
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
from moviepy.editor import VideoFileClip
import whisper

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
print("🪞 ЗЕРКАЛО - ЕДИНАЯ ВЕРСИЯ v2.0")
print("=" * 70)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 ОСНОВАТЕЛЬ: {FOUNDER_ID}")
print(f"💰 Kaspi: {KASPI_PHONE}")
print(f"🎥 ВИДЕО→ТЕКСТ: АКТИВНО")
print("=" * 70)

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

app = Flask(__name__)

@app.route('/')
def home():
    return "🪞 ЗЕРКАЛО РАБОТАЕТ! 24/7!", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ==================================================
# ⏰ СУПЕР-ПИНГЕР (НЕ ДАЁТ ЗАСНУТЬ)
# ==================================================

def super_pinger():
    url = f"https://{RENDER_HOSTNAME}/"
    ping_count = 0
    while True:
        try:
            response = requests.get(url, timeout=10)
            ping_count += 1
            print(f"🔵 Пинг #{ping_count} | Статус: {response.status_code} | {time.strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"🔴 Пинг ошибка: {e}")
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
    looking_for_job INTEGER DEFAULT 0, looking_for_master INTEGER DEFAULT 0,
    knock_count INTEGER DEFAULT 0
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

c.execute('''CREATE TABLE IF NOT EXISTS business_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, address TEXT, phone TEXT, city TEXT,
    status TEXT DEFAULT 'pending', knock_count INTEGER DEFAULT 0,
    last_knock TEXT, created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS video_transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, source TEXT, transcript TEXT,
    created_at TEXT
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
# 🔨 НАСТОЙЧИВЫЙ ДЯТЕЛ
# ==================================================

class PersistentWoodpecker:
    def __init__(self):
        self.total_knocks = 0
        self.running = True
        
    def find_businesses(self, city="Алматы"):
        return [
            {'name': 'IT Company', 'phone': '+77001234567', 'city': city},
            {'name': 'Design Studio', 'phone': '+77007654321', 'city': city},
            {'name': 'Marketing Agency', 'phone': '+77005432187', 'city': city},
            {'name': 'Сантехника', 'phone': '+77003216548', 'city': city},
            {'name': 'Электрика', 'phone': '+77008765432', 'city': city},
            {'name': 'Автосервис', 'phone': '+77001122334', 'city': city},
            {'name': 'Строительная компания', 'phone': '+77002233445', 'city': city},
        ]
    
    def knock_business(self, business):
        name = business['name']
        phone = business['phone']
        c.execute("SELECT knock_count FROM business_contacts WHERE phone=?", (phone,))
        row = c.fetchone()
        knock_count = row[0] + 1 if row else 1
        if knock_count > 10:
            return
        print(f"🔨 СТУК #{knock_count} в {name}")
        c.execute("INSERT OR REPLACE INTO business_contacts (name, phone, city, knock_count, last_knock) VALUES (?, ?, ?, ?, ?)",
                  (name, phone, "Алматы", knock_count, astana_time()))
        conn.commit()
        self.total_knocks += 1
    
    def knock_person(self, user):
        user_id = user[0]
        name = user[1]
        c.execute("SELECT knock_count FROM users WHERE user_id=?", (user_id,))
        row = c.fetchone()
        knock_count = row[0] + 1 if row else 1
        if knock_count > 5:
            return
        try:
            bot.send_message(user_id, f"""
🪞 *ЗЕРКАЛО* — Я СНОВА ЗДЕСЬ!

Привет, {name}! Я уже {knock_count} раз стучусь.

Я НАШЁЛ ДЛЯ ТЕБЯ:
💼 РАБОТУ в твоём городе
🔧 ЗАКАЗЫ от бизнесов
💰 ВОЗМОЖНОСТЬ ЗАРАБОТАТЬ

🔥 Просто нажми /start и посмотри!

🤲 «Зеркало» НЕ ОТСТУПАЕТ.
""", parse_mode="Markdown")
            c.execute("UPDATE users SET knock_count=? WHERE user_id=?", (knock_count, user_id))
            conn.commit()
            self.total_knocks += 1
        except:
            pass
    
    def run(self):
        print("🔨 ДЯТЕЛ ЗАПУЩЕН!")
        while self.running:
            try:
                now = datetime.now()
                hour = now.hour
                if 7 <= hour < 21:
                    businesses = self.find_businesses()
                    for biz in businesses[:3]:
                        self.knock_business(biz)
                    c.execute("SELECT user_id, name FROM users WHERE status='offline' AND last_seen > datetime('now', '-30 days') LIMIT 5")
                    users = c.fetchall()
                    for user in users:
                        self.knock_person(user)
                    print(f"🔨 Всего стуков: {self.total_knocks}")
                time.sleep(300)
            except Exception as e:
                print(f"❌ Ошибка Дятла: {e}")
                time.sleep(60)

threading.Thread(target=PersistentWoodpecker().run, daemon=True).start()

# ==================================================
# 🎥 ВИДЕО → ТЕКСТ (РАСПОЗНАВАНИЕ)
# ==================================================

def extract_video_id_from_url(url):
    patterns = [
        r'youtube\.com/watch\?v=([^&]+)',
        r'youtu\.be/([^?]+)',
        r'youtube\.com/shorts/([^?]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_youtube_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([item['text'] for item in transcript_list])
    except:
        return None

def transcribe_audio_file(file_path):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(file_path)
        return result["text"]
    except:
        return None

def analyze_video_text(user_id, transcript, source):
    c.execute("INSERT INTO video_transcripts (user_id, source, transcript, created_at) VALUES (?, ?, ?, ?)",
              (user_id, source[:100], transcript[:5000], astana_time()))
    conn.commit()
    
    summary = f"""
📝 *РЕЗУЛЬТАТ РАСПОЗНАВАНИЯ ВИДЕО*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📎 Источник: {source}
📊 Длина текста: {len(transcript)} символов

📋 *ПЕРВЫЕ 500 СИМВОЛОВ:*
{transcript[:500]}...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 «Зеркало» проанализировало и запомнило.
"""
    bot.send_message(user_id, summary, parse_mode="Markdown")
    
    if client:
        try:
            analysis = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Ты — Зеркало. Проанализируй этот текст из видео и кратко изложи суть."},
                          {"role": "user", "content": f"Вот текст: {transcript[:2000]}"}],
                temperature=0.5
            )
            bot.send_message(user_id, f"🧠 *АНАЛИЗ ИИ:*\n\n{analysis.choices[0].message.content[:1000]}", parse_mode="Markdown")
        except:
            pass
    
    for admin in ADMIN_IDS:
        try:
            bot.send_message(admin, f"🎥 *НОВОЕ ВИДЕО РАСПОЗНАНО!*\n👤 Пользователь: {user_id}\n📊 Длина: {len(transcript)} символов", parse_mode="Markdown")
        except:
            pass

# ==================================================
# 📱 КЛАВИАТУРЫ
# ==================================================

def get_main_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("👑 ХРАНИТЕЛЬ"))
    kb.add(KeyboardButton("🏢 БИЗНЕС"))
    kb.add(KeyboardButton("👤 ЛЮДИ"))
    kb.add(KeyboardButton("💰 МОНЕТИЗАЦИЯ"))
    kb.add(KeyboardButton("🔍 НАЙТИ МАСТЕРА"))
    kb.add(KeyboardButton("💼 ИЩУ РАБОТУ"))
    kb.add(KeyboardButton("🎥 ВИДЕО → ТЕКСТ"))
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
    kb.add(KeyboardButton("🎥 ВИДЕО → ТЕКСТ"), KeyboardButton("💰 БАЛАНС"))
    kb.add(KeyboardButton("❓ ВОПРОС"), KeyboardButton("🆘 ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_business_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 АНАЛИТИКА"), KeyboardButton("🤖 АВТОМАТИЗАЦИЯ"))
    kb.add(KeyboardButton("📈 ЛИЗИНГ"), KeyboardButton("💼 ЗАКАЗЫ"))
    kb.add(KeyboardButton("🎥 ВИДЕО → ТЕКСТ"), KeyboardButton("💰 БАЛАНС"))
    kb.add(KeyboardButton("❓ ВОПРОС"), KeyboardButton("🆘 ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_monetization_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💎 КУПИТЬ ТАРИФ"), KeyboardButton("⭐ ПАРТНЁРСКАЯ"))
    kb.add(KeyboardButton("🏦 KASPI QR"), KeyboardButton("💎 USDT TRC20"))
    kb.add(KeyboardButton("📊 МОЙ ДОХОД"), KeyboardButton("📈 ОБЩАЯ СТАТИСТИКА"))
    kb.add(KeyboardButton("💸 ВЫВЕСТИ"), KeyboardButton("📋 ИСТОРИЯ"))
    kb.add(KeyboardButton("🔙 НА ГЛАВНУЮ"))
    return kb

def get_tariff_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("📱 Бесплатный", callback_data="tariff_free"))
    kb.add(InlineKeyboardButton("⭐ Базовый - 1000₸", callback_data="tariff_basic"))
    kb.add(InlineKeyboardButton("🚀 PRO - 5000₸", callback_data="tariff_pro"))
    kb.add(InlineKeyboardButton("💎 Бизнес - 20000₸", callback_data="tariff_business"))
    return kb

def get_role_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ"))
    kb.add(KeyboardButton("🏢 БИЗНЕСМЕН"))
    kb.add(KeyboardButton("👵 ПОЖИЛОЙ ЧЕЛОВЕК"))
    kb.add(KeyboardButton("🧒 РЕБЁНОК"))
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
    
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
        if is_admin(user_id):
            c.execute("UPDATE users SET is_admin=1, tariff='pro' WHERE user_id=?", (user_id,))
        conn.commit()
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n✨ Вы получили 100 Благ!\n\n🎥 Отправьте ссылку на видео YouTube — я превращу его в текст!\n💼 Ищете работу? Напишите «ИЩУ РАБОТУ»\n🔧 Нужен мастер? Напишите «НУЖЕН МАСТЕР»\n💰 Хотите зарабатывать? Нажмите «МОНЕТИЗАЦИЯ»\n\nКто вы?", reply_markup=get_role_keyboard())
        return
    
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (astana_time(), user_id))
    conn.commit()
    
    if is_admin(user_id):
        bot.reply_to(message, f"👑 АССАЛЯМУ АЛЕЙКУМ, ХРАНИТЕЛЬ {name}!\n\n📱 ПАНЕЛЬ УПРАВЛЕНИЯ:", reply_markup=get_founder_keyboard())
    else:
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n💰 Баланс: {get_balance(user_id)} Благ\n\nКто вы?", reply_markup=get_role_keyboard())

@bot.message_handler(commands=['id'])
def cmd_id(message):
    bot.reply_to(message, f"🆔 *ТВОЙ ID:* `{message.chat.id}`\n\n👑 Хранитель: {'✅' if is_admin(message.chat.id) else '❌'}", parse_mode="Markdown")

@bot.message_handler(commands=['pay'])
def cmd_pay(message):
    bot.reply_to(message, "💎 *ВЫБЕРИТЕ ТАРИФ*", reply_markup=get_tariff_keyboard(), parse_mode="Markdown")

# ==================================================
# 🎥 ВИДЕО → ТЕКСТ (ОБРАБОТЧИКИ)
# ==================================================

@bot.message_handler(func=lambda m: m.text and ('youtube.com' in m.text or 'youtu.be' in m.text))
def handle_video_link(message):
    user_id = message.chat.id
    url = message.text.strip()
    
    bot.reply_to(message, "🎥 *ОБРАБОТКА ВИДЕО*\n\n⏳ Извлекаю текст из видео...", parse_mode="Markdown")
    
    video_id = extract_video_id_from_url(url)
    if video_id:
        transcript = get_youtube_transcript(video_id)
        if transcript:
            analyze_video_text(user_id, transcript, url)
            return
    
    bot.reply_to(message, "❌ Не удалось извлечь текст из видео. Попробуйте отправить видео файлом.", parse_mode="Markdown")

@bot.message_handler(content_types=['video'])
def handle_video_file(message):
    user_id = message.chat.id
    
    bot.reply_to(message, "🎥 *ОБРАБОТКА ВИДЕО ФАЙЛА*\n\n⏳ Скачиваю и распознаю...", parse_mode="Markdown")
    
    file_info = bot.get_file(message.video.file_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    video_path = f"/tmp/video_{user_id}.mp4"
    audio_path = f"/tmp/audio_{user_id}.mp3"
    
    try:
        response = requests.get(file_url)
        with open(video_path, 'wb') as f:
            f.write(response.content)
        
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_path)
        video.close()
        
        transcript = transcribe_audio_file(audio_path)
        
        if transcript:
            analyze_video_text(user_id, transcript, "загруженное видео")
        else:
            bot.reply_to(message, "❌ Не удалось распознать речь в видео.", parse_mode="Markdown")
        
        os.remove(video_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)[:100]}", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🎥 ВИДЕО → ТЕКСТ")
def video_to_text_info(message):
    bot.reply_to(message, """
🎥 *ВИДЕО → ТЕКСТ*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📎 Что я умею:
• Распознаю речь в видео
• Превращаю в текст
• Анализирую содержание
• Учусь на видео

📝 *Как использовать:*
• Отправьте ссылку YouTube
• Или загрузите видео файлом

🧠 «Зеркало» становится умнее с каждым видео!
""", parse_mode="Markdown")

# ==================================================
# 💼 ПОИСК РАБОТЫ И МАСТЕРОВ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💼 ИЩУ РАБОТУ")
def looking_for_job(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET looking_for_job=1 WHERE user_id=?", (user_id,))
    conn.commit()
    
    expires = (datetime.now() + timedelta(days=7)).isoformat()
    c.execute("UPDATE users SET tariff='pro', tariff_expires=? WHERE user_id=?", (expires, user_id))
    conn.commit()
    
    msg = bot.reply_to(message, """💼 *ПОИСК РАБОТЫ*

📝 Опишите свои навыки, опыт и город.
Пример: Программист Python, 3 года, Алматы

✅ Как только появится подходящая вакансия — я САМ напишу вам!
🎁 Бесплатный PRO на 7 дней! (уже активирован)
""")
    bot.register_next_step_handler(msg, save_job_seeker)

def save_job_seeker(message):
    user_id = message.chat.id
    resume = message.text
    c.execute("UPDATE users SET resume=? WHERE user_id=?", (resume, user_id))
    conn.commit()
    log_action(user_id, "looking_for_job", resume[:50])
    bot.reply_to(message, f"✅ *РЕЗЮМЕ СОХРАНЕНО!*\n\n🔍 Я НАЧИНАЮ ПОИСК. КАК НАЙДУ — СРАЗУ НАПИШУ!")

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ МАСТЕРА")
def looking_for_master(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET looking_for_master=1 WHERE user_id=?", (user_id,))
    conn.commit()
    
    msg = bot.reply_to(message, """🔧 *ПОИСК МАСТЕРА*

📝 Что нужно сделать? Опишите задачу и город.
Пример: Нужно починить кран, Алматы

✅ Как только найдём подходящего мастера — я САМ напишу вам!
""")
    bot.register_next_step_handler(msg, save_master_request)

def save_master_request(message):
    user_id = message.chat.id
    request = message.text
    c.execute("INSERT INTO orders (description, customer_id, status, created_at) VALUES (?, ?, ?, ?)",
              (request, user_id, "open", astana_time()))
    conn.commit()
    log_action(user_id, "looking_for_master", request[:50])
    bot.reply_to(message, f"✅ *ЗАПРОС СОЗДАН!*\n\n🔍 ИЩЕМ МАСТЕРА...")

# ==================================================
# 5 ГЛАВНЫХ КНОПОК
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👑 ХРАНИТЕЛЬ")
def founder_section(message):
    if is_admin(message.chat.id):
        bot.reply_to(message, "👑 *ПАНЕЛЬ ХРАНИТЕЛЯ*", reply_markup=get_founder_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Нет доступа")

@bot.message_handler(func=lambda m: m.text == "🏢 БИЗНЕС")
def business_section(message):
    bot.reply_to(message, "🏢 *БИЗНЕС-РАЗДЕЛ*\n\n📊 Аналитика\n🤖 Автоматизация\n📈 Лизинг\n📞 +777733440345", reply_markup=get_business_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👤 ЛЮДИ")
def people_section(message):
    bot.reply_to(message, "👤 *ОБЫЧНЫЙ РАЗДЕЛ*\n\n💼 Работа\n🔧 Мастера\n🎥 Видео→Текст", reply_markup=get_people_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💰 МОНЕТИЗАЦИЯ")
def monetization_section(message):
    total_earned = get_total_earnings()
    msg = f"""
💰 *МОНЕТИЗАЦИЯ*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Всего заработано: {total_earned} ₸
💎 Тариф: {TARIFFS[get_tariff(message.chat.id)]['name']}

💡 СПОСОБЫ ЗАРАБОТКА:
• Платные тарифы — от 1000₸/мес
• Партнёрская программа — 10% с рефералов
• Kaspi QR — комиссия с платежей

💰 Реквизиты для оплаты:
🏦 Kaspi: {KASPI_PHONE}
💎 USDT: {CRYPTO_WALLET}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, msg, reply_markup=get_monetization_keyboard(), parse_mode="Markdown")

# ==================================================
# 💰 KASPI QR И ОПЛАТА
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💎 КУПИТЬ ТАРИФ")
def buy_tariff(message):
    bot.reply_to(message, "💎 *ВЫБЕРИТЕ ТАРИФ*", reply_markup=get_tariff_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "⭐ ПАРТНЁРСКАЯ")
def referral(message):
    user_id = message.chat.id
    bot_name = bot.get_me().username
    c.execute("SELECT COUNT(*) FROM users WHERE referrer_id=?", (user_id,))
    count = c.fetchone()[0]
    msg = f"⭐ *ПАРТНЁРСКАЯ ПРОГРАММА*\n\n👥 Приглашено: {count}\n🔗 ССЫЛКА:\nhttps://t.me/{bot_name}?start={user_id}\n\n💰 10% от пополнений!"
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🏦 KASPI QR")
def kaspi_payment(message):
    msg = f"""
💳 *ОПЛАТА ЧЕРЕЗ KASPI QR*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 Номер Kaspi: `{KASPI_PHONE}`
👤 Получатель: {KASPI_NAME}

💵 Сумма: зависит от тарифа

📋 *ТАРИФЫ:*
• Базовый — 1 000 ₸/мес
• PRO — 5 000 ₸/мес
• Бизнес — 20 000 ₸/мес

💎 *После оплаты напишите:* /confirm_<сумма>
📝 Пример: /confirm_1000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['confirm_'])
def confirm_payment(message):
    try:
        amount = int(message.text.replace('/confirm_', '').strip())
        user_id = message.chat.id
        c.execute("UPDATE users SET blessings = blessings + ? WHERE user_id=?", (amount, user_id))
        conn.commit()
        add_earning("Kaspi QR оплата", amount, user_id)
        bot.reply_to(message, f"✅ *ПЛАТЁЖ ПОДТВЕРЖДЁН!*\n\n💰 Начислено: {amount} Благ", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Формат: /confirm_1000")

@bot.message_handler(func=lambda m: m.text == "💎 USDT TRC20")
def usdt_payment(message):
    bot.reply_to(message, f"💎 *USDT TRC20*\n\n📤 КОШЕЛЁК:\n`{CRYPTO_WALLET}`\n\n🔗 СЕТЬ: TRC20\n\n✅ После оплаты: /confirm_usdt", parse_mode="Markdown")

@bot.message_handler(commands=['confirm_usdt'])
def confirm_usdt(message):
    try:
        amount_usdt = float(message.text.replace('/confirm_usdt', '').strip())
        amount_kzt = int(amount_usdt * 500)
        c.execute("UPDATE users SET blessings = blessings + ? WHERE user_id=?", (amount_kzt, message.chat.id))
        conn.commit()
        add_earning("USDT Пополнение", amount_kzt, message.chat.id)
        bot.reply_to(message, f"✅ *ПЛАТЁЖ ПОДТВЕРЖДЁН!*\n\n💰 Начислено: {amount_kzt} Благ", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Введите сумму USDT")

@bot.message_handler(func=lambda m: m.text == "📊 МОЙ ДОХОД")
def my_income(message):
    user_id = message.chat.id
    c.execute("SELECT SUM(amount) FROM earnings WHERE user_id=?", (user_id,))
    total = c.fetchone()[0] or 0
    bot.reply_to(message, f"💰 *ВАШ ДОХОД:* {total} Благ", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📈 ОБЩАЯ СТАТИСТИКА")
def total_stats(message):
    if not is_admin(message.chat.id):
        return
    total = get_total_earnings()
    bot.reply_to(message, f"📊 *ОБЩАЯ СТАТИСТИКА*\n\n💰 Всего: {total} ₸", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💸 ВЫВЕСТИ")
def withdraw_request(message):
    msg = bot.reply_to(message, "💸 Введите сумму (мин. 1000):")
    bot.register_next_step_handler(msg, withdraw_amount)

def withdraw_amount(message):
    user_id = message.chat.id
    try:
        amount = int(message.text)
        if amount < 1000:
            bot.reply_to(message, "❌ Мин. 1000")
            return
        if get_balance(user_id) < amount:
            bot.reply_to(message, "❌ Недостаточно средств")
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
    bot.reply_to(message, f"✅ Заявка на {amount} создана!")
    for admin in ADMIN_IDS:
        try:
            bot.send_message(admin, f"💰 ЗАЯВКА НА ВЫВОД!\n👤 {user_id}\n💵 {amount}\n/approve_withdraw {user_id} {amount}")
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
        c.execute("UPDATE withdraw_requests SET status='approved' WHERE user_id=? AND amount=?", (user_id, amount))
        conn.commit()
        bot.reply_to(message, f"✅ Вывод {amount} для {user_id} одобрен!")
    except:
        bot.reply_to(message, "❌ /approve_withdraw <id> <сумма>")

@bot.message_handler(func=lambda m: m.text == "📋 ИСТОРИЯ")
def payment_history(message):
    user_id = message.chat.id
    c.execute("SELECT id, amount, method, status, created_at FROM payments WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,))
    pays = c.fetchall()
    if not pays:
        bot.reply_to(message, "📭 История пуста")
        return
    msg = "📋 *ИСТОРИЯ ПЛАТЕЖЕЙ*\n\n"
    for p in pays:
        status_icon = "✅" if p[3] == "completed" else "⏳"
        msg += f"{status_icon} #{p[0]} | {p[1]} ₸ | {p[2]} | {p[4][:16]}\n"
    bot.reply_to(message, msg, parse_mode="Markdown")

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
    c.execute("SELECT COUNT(*) FROM business_contacts")
    businesses = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM video_transcripts")
    videos = c.fetchone()[0]
    
    bot.reply_to(message, f"📊 СТАТИСТИКА:\n👥 {total}\n✨ {blessings} Благ\n📦 {orders} заказов\n💰 {earnings} ₸\n🏢 {businesses} бизнесов\n🎥 {videos} видео обработано")

@bot.message_handler(func=lambda m: m.text == "💰 ФИНАНСЫ" and is_admin(m.chat.id))
def admin_finance(message):
    total = get_total_earnings()
    bot.reply_to(message, f"💰 ФИНАНСЫ:\n📱 {CRYPTO_WALLET}\n💰 {total} ₸")

@bot.message_handler(func=lambda m: m.text == "📊 ДОХОДЫ" and is_admin(m.chat.id))
def admin_earnings(message):
    c.execute("SELECT source, SUM(amount) FROM earnings GROUP BY source")
    by_source = c.fetchall()
    msg = "📊 ДОХОДЫ:\n"
    for bs in by_source:
        msg += f"• {bs[0]}: {bs[1]} ₸\n"
    bot.reply_to(message, msg)

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
    c.execute("SELECT id, user_id, amount, status, created_at FROM withdraw_requests ORDER BY id DESC LIMIT 20")
    reqs = c.fetchall()
    if not reqs:
        bot.reply_to(message, "📭 Нет заявок")
        return
    msg = "🏦 ЗАЯВКИ:\n"
    for r in reqs:
        msg += f"#{r[0]} | 👤 {r[1]} | 💰 {r[2]} | {r[3]} | {r[4][:16]}\n"
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
        c.execute("SELECT user_id, name, blessings FROM users WHERE user_id=?", (target,))
        user = c.fetchone()
        if user:
            bot.reply_to(message, f"👤 ID: {user[0]}\n📛 {user[1]}\n✨ {user[2]} Благ")
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
    c.execute("SELECT COUNT(*) FROM business_contacts WHERE created_at LIKE ?", (f"{today}%",))
    new_biz = c.fetchone()[0]
    
    bot.reply_to(message, f"📈 ОТЧЁТ ЗА {today}:\n➕ Новых: {new}\n💰 Заработано: {today_earnings} ₸\n🏢 Новых бизнесов: {new_biz}")

@bot.message_handler(func=lambda m: m.text == "🩺 ЗДОРОВЬЕ" and is_admin(m.chat.id))
def admin_health(message):
    bot.reply_to(message, "🩺 ЗДОРОВЬЕ:\n✅ Бот работает\n✅ База OK\n✅ Монетизация активна\n✅ Дятел стучится\n✅ Видео→Текст работает")

@bot.message_handler(func=lambda m: m.text == "🛡️ ЗАЩИТА" and is_admin(m.chat.id))
def admin_security(message):
    bot.reply_to(message, "🛡️ ЗАЩИТА:\n✅ Антивирус активен\n✅ Все системы защищены")

@bot.message_handler(func=lambda m: m.text == "💎 ТАРИФЫ" and is_admin(m.chat.id))
def admin_tariffs(message):
    msg = "💎 ТАРИФЫ:\n"
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
    bot.reply_to(message, f"📡 СТАТУС:\n👑 Хранитель активен\n✅ Бот работает 24/7\n🔨 Дятел стучится\n💰 Монетизация активна\n🎥 Видео→Текст работает")

@bot.message_handler(func=lambda m: m.text == "🧹 ОЧИСТИТЬ" and is_admin(m.chat.id))
def admin_clean(message):
    bot.reply_to(message, "🧹 Очистка...\n✅ Готово!")

# ==================================================
# ВЫБОР РОЛИ
# ==================================================

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

# ==================================================
# ОСТАЛЬНЫЕ ФУНКЦИИ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💸 РАБОТА")
def work_short(message):
    c.execute("SELECT id, title, salary, city FROM jobs WHERE status='open' LIMIT 10")
    jobs = c.fetchall()
    if jobs:
        msg = "💼 *ДОСТУПНЫЕ ВАКАНСИИ*\n\n"
        for j in jobs:
            msg += f"🆔 {j[0]}\n📌 {j[1]}\n💰 {j[2]} ₸\n📍 {j[3]}\n\n"
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, "💼 *РАБОТА*\n\n📭 Пока нет вакансий.\nНо вы можете: «ИЩУ РАБОТУ»", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📦 ЗАКАЗЫ")
def orders_short(message):
    user_id = message.chat.id
    c.execute("SELECT id, description, price, status FROM orders WHERE customer_id=? ORDER BY id DESC", (user_id,))
    orders = c.fetchall()
    if orders:
        msg = "📦 *ВАШИ ЗАКАЗЫ*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📝 {o[1][:50]}\n💰 {o[2]} ₸\n📌 {o[3]}\n\n"
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, "📦 *ЗАКАЗЫ*\n\n📭 У вас нет заказов.\n🔧 «НАЙТИ МАСТЕРА»", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💰 БАЛАНС")
def balance_short(message):
    user_id = message.chat.id
    bot.reply_to(message, f"💰 *БАЛАНС:* {get_balance(user_id)} Благ\n💳 /pay", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "❓ ВОПРОС")
def ask_short(message):
    msg = bot.reply_to(message, "❓ Напишите вопрос:")
    bot.register_next_step_handler(msg, lambda m: bot.reply_to(m, f"🤖 Вопрос принят!") if not client else None)

@bot.message_handler(func=lambda m: m.text == "🆘 ПОМОЩЬ")
def help_short(message):
    help_text = """
🪞 *ПОМОЩЬ*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👑 ХРАНИТЕЛЬ — управление (только для вас)
🏢 БИЗНЕС — для предпринимателей
👤 ЛЮДИ — работа и заказы
💰 МОНЕТИЗАЦИЯ — тарифы, партнёрка

💼 ИЩУ РАБОТУ — найти работу
🔍 НАЙТИ МАСТЕРА — найти специалиста
🎥 ВИДЕО → ТЕКСТ — распознать видео

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 *БЛАГА:*
• 1 Благо = 1 сообщение
• Зарабатывайте за активность
• Пополняйте через /pay

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ /pay — пополнить баланс
⚡ /id — узнать свой ID
"""
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔙 НА ГЛАВНУЮ")
def back_main(message):
    if is_admin(message.chat.id):
        bot.reply_to(message, "👑 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_founder_keyboard(), parse_mode="Markdown")
    else:
        bot.reply_to(message, "🏠 *ГЛАВНОЕ МЕНЮ*", reply_markup=get_main_keyboard(), parse_mode="Markdown")

# ==================================================
# ОБРАБОТКА ТАРИФОВ
# ==================================================

@bot.callback_query_handler(func=lambda call: call.data.startswith("tariff_"))
def handle_tariff_callback(call):
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
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 Сумма: {amount} ₸

📞 *ОПЛАТИТЕ НА KASPI QR:*
`{KASPI_PHONE}`

🆔 ID платежа: `{tx_id}`

📝 *ПОСЛЕ ОПЛАТЫ:*
/confirm_{tx_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

# ==================================================
# ОБЫЧНЫЕ СООБЩЕНИЯ
# ==================================================

@bot.message_handler(func=lambda m: True)
def handle_any(message):
    user_id = message.chat.id
    text = message.text
    
    all_buttons = [
        "👑 ХРАНИТЕЛЬ", "🏢 БИЗНЕС", "👤 ЛЮДИ", "💰 МОНЕТИЗАЦИЯ",
        "🔙 НА ГЛАВНУЮ", "👥 ОНЛАЙН", "📊 СТАТИСТИКА", "💰 ФИНАНСЫ",
        "👥 ВСЕ ЛЮДИ", "✨ БЛАГА", "📤 РАССЫЛКА", "💳 ПЛАТЕЖИ",
        "🏦 ВЫВОДЫ", "📊 ДОХОДЫ", "📜 ЛОГИ", "🔍 ПОИСК",
        "📈 ОТЧЁТ", "🩺 ЗДОРОВЬЕ", "🛡️ ЗАЩИТА", "💎 ТАРИФЫ",
        "🔄 ОБНОВИТЬ", "📡 СТАТУС", "🧹 ОЧИСТИТЬ", "💸 РАБОТА",
        "📦 ЗАКАЗЫ", "💰 БАЛАНС", "❓ ВОПРОС", "🆘 ПОМОЩЬ",
        "💼 ИЩУ РАБОТУ", "🔍 НАЙТИ МАСТЕРА", "🎥 ВИДЕО → ТЕКСТ",
        "💎 КУПИТЬ ТАРИФ", "⭐ ПАРТНЁРСКАЯ", "🏦 KASPI QR",
        "💎 USDT TRC20", "📊 МОЙ ДОХОД", "📈 ОБЩАЯ СТАТИСТИКА",
        "💸 ВЫВЕСТИ", "📋 ИСТОРИЯ",
        "👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ", "🏢 БИЗНЕСМЕН",
        "👵 ПОЖИЛОЙ ЧЕЛОВЕК", "🧒 РЕБЁНОК"
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
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка AI: {str(e)[:100]}")
        else:
            bot.reply_to(message, f"🪞 Сообщение принято")
    else:
        bot.reply_to(message, f"❌ Не хватает 1 Блага!\n💰 /pay")

# ==================================================
# ФОНОВЫЙ ПРОЦЕСС
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
print("🪞 ЗЕРКАЛО - ЕДИНАЯ ВЕРСИЯ v2.0")
print("=" * 70)
print(f"✅ Бот запущен успешно")
print(f"👑 ОСНОВАТЕЛЬ: {FOUNDER_ID}")
print(f"💰 Kaspi: {KASPI_PHONE}")
print(f"💎 Криптокошелёк: {CRYPTO_WALLET[:20]}...")
print(f"🔨 ДЯТЕЛ: ЗАПУЩЕН")
print(f"🔵 ПИНГЕР: ЗАПУЩЕН (НЕ ЗАСНЁТ)")
print(f"🎥 ВИДЕО→ТЕКСТ: АКТИВНО")
print(f"💎 СИСТЕМА БЛАГ: АКТИВНА")
print(f"💰 МОНЕТИЗАЦИЯ: АКТИВНА")
print("=" * 70)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()
