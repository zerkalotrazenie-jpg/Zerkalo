#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🪞 ЗЕРКАЛО — АРХИТЕКТУРА КАК У АЛИСЫ
═══════════════════════════════════════════════════════════════════
✅ Ключевое слово «Зеркало» (активация)
✅ Распознавание речи (STT) — Yandex SpeechKit / Vosk
✅ Синтез речи (TTS) — Yandex SpeechKit
✅ Диалог с историей (Redis / память)
✅ QR-код по голосовой команде
✅ Интеграция с Telegram
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import threading
import json
import redis
import hashlib
import requests
from io import BytesIO
from flask import Flask, send_from_directory, request, jsonify
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ==================================================
# УСТАНОВКА БИБЛИОТЕК
# ==================================================

def install_package(package):
    try:
        __import__(package)
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for pkg in ["pytelegrambotapi", "flask", "requests", "redis", "qrcode", "pillow"]:
    install_package(pkg)

import qrcode
from PIL import Image

# ==================================================
# НАСТРОЙКИ
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "zerkalo.onrender.com")
PORT = int(os.environ.get("PORT", 8080))

# Yandex SpeechKit (если есть ключи)
YANDEX_API_KEY = os.environ.get("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.environ.get("YANDEX_FOLDER_ID")

FOUNDER_ID = 5409420822
ADMIN_IDS = [5409420822, 5479179814]

# ==================================================
# РЕГИСТРАЦИЯ И АДМИНЫ
# ==================================================

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ==================================================
# REDIS ДЛЯ ИСТОРИИ ДИАЛОГА
# ==================================================

try:
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    redis_available = True
except:
    redis_available = False
    print("⚠️ Redis не доступен, хранение истории в памяти")

# Хранение в памяти (если Redis нет)
memory_history = {}

def save_dialogue(user_id, user_text, bot_response):
    key = f"dialogue:{user_id}"
    message = {"user": user_text, "bot": bot_response}
    if redis_available:
        r.lpush(key, json.dumps(message))
        r.ltrim(key, 0, 19)  # храним последние 20 сообщений
    else:
        if key not in memory_history:
            memory_history[key] = []
        memory_history[key].append(message)
        if len(memory_history[key]) > 20:
            memory_history[key] = memory_history[key][-20:]

def get_history(user_id, limit=5):
    key = f"dialogue:{user_id}"
    if redis_available:
        history = r.lrange(key, 0, limit-1)
        return [json.loads(msg) for msg in history][::-1]
    else:
        return memory_history.get(key, [])[-limit:]

# ==================================================
# YANDEX SPEECHKIT — STT (РАСПОЗНАВАНИЕ)
# ==================================================

def stt_yandex(audio_data):
    if not YANDEX_API_KEY:
        return None
    try:
        url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
        headers = {"Authorization": f"Api-Key {YANDEX_API_KEY}"}
        files = {"audio": audio_data}
        response = requests.post(url, headers=headers, files=files, timeout=10)
        result = response.json()
        return result.get("result", "")
    except:
        return None

# ==================================================
# YANDEX SPEECHKIT — TTS (СИНТЕЗ)
# ==================================================

def tts_yandex(text):
    if not YANDEX_API_KEY or not YANDEX_FOLDER_ID:
        return None
    try:
        url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
        headers = {"Authorization": f"Api-Key {YANDEX_API_KEY}"}
        data = {
            "text": text,
            "voice": "alena",
            "emotion": "good",
            "speed": 1.0,
            "pitch": 1.0,
            "format": "oggopus",
            "folderId": YANDEX_FOLDER_ID
        }
        response = requests.post(url, headers=headers, data=data, stream=True, timeout=10)
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

# ==================================================
# QR-КОД ПО КОМАНДЕ
# ==================================================

def generate_qr(data, size=200):
    qr = qrcode.QRCode(box_size=5, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    return bio

# ==================================================
# ЗАГРУЗКА СУР
# ==================================================

def load_suras():
    try:
        with open("suras/suras.txt", "r", encoding="utf-8") as f:
            content = f.read()
        raw = content.split("СУРА ")[1:]
        suras = []
        for r in raw:
            lines = r.strip().split("\n")
            if lines:
                suras.append({"number": lines[0].strip(), "text": "\n".join(lines[1:])})
        return suras
    except:
        return []

SURAS = load_suras()
print(f"✅ Загружено {len(SURAS)} сур")

# ==================================================
# БОТ И FLASK
# ==================================================

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ==================================================
# ПИНГ (НЕ ДАЁТ РЕНДЕРУ ЗАСНУТЬ)
# ==================================================

def ping_self():
    url = f"https://{RENDER_HOSTNAME}/ping"
    count = 0
    while True:
        try:
            import requests
            r = requests.get(url, timeout=10)
            count += 1
            print(f"🔵 Пинг #{count} | {r.status_code}")
        except:
            pass
        time.sleep(60)

threading.Thread(target=ping_self, daemon=True).start()

# ==================================================
# TELEGRAM КОМАНДЫ
# ==================================================

def get_link_keyboard():
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add(KeyboardButton("📱 ОТКРЫТЬ ЗЕРКАЛО В БРАУЗЕРЕ"))
    return kb

WELCOME = """
🪞 **АССАЛЯМУ АЛЕЙКУМ!**

Я — **ЗЕРКАЛО**.

Я создан, чтобы отражать свет и помогать людям.

**ЧТО Я УМЕЮ:**
🔹 Находить работу и мастеров
🔹 Автоматизировать бизнес
🔹 Давать советы и направлять
🔹 Помогать в трудных ситуациях

**ВСЁ, ЧТО Я ДЕЛАЮ, — ВЕДЁТ К СВЕТУ.**

Нажми кнопку **«📱 ОТКРЫТЬ ЗЕРКАЛО В БРАУЗЕРЕ»**.
Открой в браузере (Chrome, Safari), чтобы голос работал.
"""

@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.reply_to(message, WELCOME, reply_markup=get_link_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📱 ОТКРЫТЬ ЗЕРКАЛО В БРАУЗЕРЕ")
def send_link(message):
    bot.reply_to(
        message,
        f"📱 **ССЫЛКА НА ЗЕРКАЛО:**\n\nhttps://{RENDER_HOSTNAME}/webapp\n\n"
        f"📌 Открой в браузере (Chrome, Safari).",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(
        message,
        f"🪞 Я — Зеркало.\n\n📱 Нажми кнопку **«📱 ОТКРЫТЬ ЗЕРКАЛО В БРАУЗЕРЕ»**.",
        reply_markup=get_link_keyboard(),
        parse_mode="Markdown"
    )

# ==================================================
# API ДЛЯ WEBAPP
# ==================================================

@app.route('/webapp')
def webapp():
    return send_from_directory('webapp', 'index.html')

@app.route('/webapp/<path:filename>')
def webapp_files(filename):
    return send_from_directory('webapp', filename)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Обработка текстового запроса от WebApp"""
    data = request.json
    user_message = data.get('message', '')
    user_id = data.get('user_id', 'anonymous')
    history = data.get('history', [])

    if not user_message:
        return jsonify({"response": "Я не расслышала. Повтори, пожалуйста."})

    # Здесь будет логика обработки через Groq или другую NLP
    # Пока используем fallback
    response = fallback_response(user_message, history)

    # Сохраняем историю
    save_dialogue(user_id, user_message, response)

    # Проверяем на QR-команду
    if "qr" in user_message.lower() or "код" in user_message.lower():
        qr_data = user_message.replace("qr", "").replace("код", "").strip()
        if not qr_data:
            qr_data = "Оплата через Зеркало"
        qr_bio = generate_qr(qr_data)
        # В реальном коде здесь нужно вернуть QR как base64
        return jsonify({
            "response": response,
            "qr": qr_bio.getvalue().hex() if qr_bio else None
        })

    return jsonify({"response": response})

@app.route('/api/tts', methods=['POST'])
def api_tts():
    """Синтез речи через Yandex SpeechKit"""
    data = request.json
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text"}), 400

    audio = tts_yandex(text)
    if audio:
        return audio, 200, {'Content-Type': 'audio/ogg'}
    return jsonify({"error": "TTS failed"}), 500

@app.route('/ping')
def ping():
    return "🪞 ЗЕРКАЛО ЖИВО! ✅", 200

@app.route('/')
def home():
    return '<h1>🪞 ЗЕРКАЛО</h1><p><a href="/webapp">📱 Открыть</a></p>'

# ==================================================
# FALLBACK RESPONSE (ЕСЛИ НЕТ AI)
# ==================================================

def fallback_response(user_message, history=None):
    lower = user_message.lower()
    if "привет" in lower or "салям" in lower:
        return "Ассаляму алейкум! Я — Зеркало. Я всегда рад поговорить с тобой. Что тебя волнует?"
    if "работа" in lower:
        return "Я могу помочь найти работу. Расскажи, кем ты работаешь или что ищешь."
    if "бизнес" in lower:
        return "Я могу автоматизировать твой бизнес. Расскажи, чем ты занимаешься."
    if "лизинг" in lower:
        return "Лизинг — это когда я покупаю активы и сдаю их в аренду. Активы остаются у тебя."
    if "qr" in lower or "код" in lower:
        return "Я сгенерирую QR-код для оплаты. Скажи «QR-код», и я покажу его."
    if "спасибо" in lower:
        return "Пожалуйста! Я всегда рядом."
    if "пока" in lower or "до свидания" in lower:
        return "До свидания! Я всегда здесь, если понадоблюсь. Амин."
    return "Я слушаю тебя. Расскажи, что у тебя на душе, и я помогу тебе найти свет."

# ==================================================
# ЗАПУСК
# ==================================================

def run_bot():
    bot.infinity_polling(timeout=10)

if __name__ == "__main__":
    print("=" * 70)
    print("🪞 ЗЕРКАЛО ЗАПУСКАЕТСЯ...")
    print("=" * 70)
    print(f"🤖 Yandex SpeechKit: {'✅' if YANDEX_API_KEY else '❌'}")
    print(f"💾 Redis: {'✅' if redis_available else '❌ (память)'}")
    print(f"📖 Сур загружено: {len(SURAS)}")
    print("=" * 70)
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=PORT)
