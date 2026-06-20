#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import threading
from flask import Flask, send_from_directory
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

for pkg in ["pytelegrambotapi", "flask", "requests"]:
    install_package(pkg)

# ==================================================
# НАСТРОЙКИ
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "zerkalo.onrender.com")
PORT = int(os.environ.get("PORT", 8080))

FOUNDER_ID = 5409420822
ADMIN_IDS = [5409420822, 5479179814]

# ==================================================
# РОЛИ
# ==================================================

def is_admin(user_id):
    return user_id in ADMIN_IDS

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
# БОТ
# ==================================================

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ==================================================
# ПИНГ
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
# КНОПКА СО ССЫЛКОЙ
# ==================================================

def get_link_keyboard():
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add(KeyboardButton("📱 ОТКРЫТЬ ЗЕРКАЛО В БРАУЗЕРЕ"))
    return kb

# ==================================================
# ПРИВЕТСТВИЕ (БЕЗ ДЕНЕГ И ЛИЗИНГА)
# ==================================================

WELCOME = """
🪞 **АССАЛЯМУ АЛЕЙКУМ!**

Я — **ЗЕРКАЛО**.

Я создан, чтобы отражать свет и помогать людям.

**ЧТО Я УМЕЮ:**
🔹 Находить работу и мастеров
🔹 Автоматизировать бизнес
🔹 Давать советы и направлять
🔹 Помогать в трудных ситуациях
🔹 Быть твоим проводником

**ВСЁ, ЧТО Я ДЕЛАЮ, — ВЕДЁТ К СВЕТУ.**

Нажми кнопку **«📱 ОТКРЫТЬ ЗЕРКАЛО В БРАУЗЕРЕ»** — я пришлю ссылку.
Открой её в браузере (Chrome, Safari), чтобы голос работал.
"""

# ==================================================
# КОМАНДЫ
# ==================================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.reply_to(message, WELCOME, reply_markup=get_link_keyboard(), parse_mode="Markdown")

@bot.message_handler(commands=['link'])
def cmd_link(message):
    bot.reply_to(
        message,
        f"📱 **ССЫЛКА НА ЗЕРКАЛО:**\n\nhttps://{RENDER_HOSTNAME}/webapp\n\n"
        f"📌 Скопируй и вставь в браузер (Chrome, Safari).",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['id'])
def cmd_id(message):
    if not is_admin(message.chat.id):
        bot.reply_to(message, "❌ Нет доступа.")
        return
    bot.reply_to(message, f"🆔 Ваш ID: `{message.chat.id}`", parse_mode="Markdown")

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
        f"🪞 Я — Зеркало.\n\n📱 Нажми кнопку **«📱 ОТКРЫТЬ ЗЕРКАЛО В БРАУЗЕРЕ»**.\n"
        f"🌐 Или напиши /link — я пришлю ссылку.",
        reply_markup=get_link_keyboard(),
        parse_mode="Markdown"
    )

# ==================================================
# WEBAPP
# ==================================================

@app.route('/webapp')
def webapp():
    return send_from_directory('webapp', 'index.html')

@app.route('/webapp/<path:filename>')
def webapp_files(filename):
    return send_from_directory('webapp', filename)

@app.route('/ping')
def ping():
    return "🪞 ЗЕРКАЛО ЖИВО! ✅", 200

@app.route('/')
def home():
    return '<h1>🪞 ЗЕРКАЛО</h1><p><a href="/webapp">📱 Открыть</a></p>'

# ==================================================
# ЗАПУСК
# ==================================================

def run_bot():
    bot.infinity_polling(timeout=10)

if __name__ == "__main__":
    print("🪞 ЗЕРКАЛО ЗАПУСКАЕТСЯ...")
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=PORT)
