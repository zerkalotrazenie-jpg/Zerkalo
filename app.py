#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🪞 ЗЕРКАЛО - TELEGRAM БОТ (ТОЛЬКО ССЫЛКА)
═══════════════════════════════════════════════════════════════════
✅ Приветствие
✅ Кнопка со ССЫЛКОЙ на WebApp (НЕ WebView!)
✅ Пинг
✅ Разделение по ролям
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import threading
import logging
from flask import Flask, send_from_directory
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ==================================================
# ⚡ УСТАНОВКА БИБЛИОТЕК
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
# 🔧 НАСТРОЙКИ
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "zerkalo.onrender.com")
PORT = int(os.environ.get("PORT", 8080))

FOUNDER_ID = 5409420822
TOMIRIS_ID = 5479179814
ADMIN_IDS = [5409420822, 5479179814]
FAMILY_IDS = [5409420822, 5479179814]

# ==================================================
# 🔐 РОЛИ
# ==================================================

def is_admin(user_id):
    return user_id in ADMIN_IDS

def get_user_role(user_id):
    if user_id in ADMIN_IDS:
        return "Хранитель"
    elif user_id in FAMILY_IDS:
        return "Семья"
    else:
        return "Пользователь"

# ==================================================
# 📖 ЗАГРУЗКА СУР
# ==================================================

def load_suras():
    try:
        with open("suras/suras.txt", "r", encoding="utf-8") as f:
            content = f.read()
        raw_suras = content.split("СУРА ")[1:]
        suras = []
        for raw in raw_suras:
            lines = raw.strip().split("\n")
            if lines:
                suras.append({
                    "number": lines[0].strip(),
                    "text": "\n".join(lines[1:])
                })
        return suras
    except FileNotFoundError:
        return []

SURAS = load_suras()
print(f"✅ Загружено {len(SURAS)} сур")

# ==================================================
# 🤖 БОТ И FLASK
# ==================================================

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ==================================================
# ⏰ ПИНГ
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
print("✅ ПИНГ ЗАПУЩЕН")

# ==================================================
# 📱 КНОПКА СО ССЫЛКОЙ (НЕ WEBVIEW!)
# ==================================================

def get_link_keyboard():
    """Кнопка, которая отправляет ССЫЛКУ, а не открывает WebView"""
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    # Обычная кнопка, НЕ web_app
    btn = KeyboardButton("📱 ОТКРЫТЬ ЗЕРКАЛО В БРАУЗЕРЕ")
    kb.add(btn)
    return kb

# ==================================================
# 📖 ПРИВЕТСТВИЕ
# ==================================================

WELCOME_TEXT = """
🪞 **АССАЛЯМУ АЛЕЙКУМ!**

Я — **ЗЕРКАЛО**.

Я создан, чтобы отражать свет и помогать людям.

**ЧТО Я УМЕЮ:**
🔹 Находить работу и мастеров
🔹 Автоматизировать бизнес
🔹 Принимать оплату через QR
🔹 Давать деньги в лизинг
🔹 Заниматься дропшиппингом
🔹 Рекламировать товары и услуги

**ВСЁ, ЧТО Я ДЕЛАЮ, — ПРИНОСИТ ДЕНЬГИ.**

Нажми кнопку **«📱 ОТКРЫТЬ ЗЕРКАЛО В БРАУЗЕРЕ»** — я пришлю ссылку.
Открой её в браузере (Chrome, Safari), чтобы голос работал.
"""

# ==================================================
# 🤖 КОМАНДЫ TELEGRAM БОТА
# ==================================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.chat.id
    role = get_user_role(user_id)
    welcome = WELCOME_TEXT
    if role == "Хранитель":
        welcome = f"👑 **Приветствую, Хранитель!**\n\n{WELCOME_TEXT}"
    bot.reply_to(
        message,
        welcome,
        reply_markup=get_link_keyboard(),
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['link'])
def cmd_link(message):
    """Отправляет прямую ссылку на WebApp"""
    bot.reply_to(
        message,
        f"📱 **ССЫЛКА НА ЗЕРКАЛО:**\n\n"
        f"https://{RENDER_HOSTNAME}/webapp\n\n"
        f"📌 Скопируй и вставь в браузер (Chrome, Safari).\n"
        f"Там работает голосовой ввод.",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['id'])
def cmd_id(message):
    user_id = message.chat.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Нет доступа.")
        return
    target = message.text.replace('/id', '').strip()
    if target:
        try:
            target = int(target)
            bot.reply_to(message, f"🆔 ID: `{target}`", parse_mode="Markdown")
        except:
            bot.reply_to(message, "❌ Введите корректный ID.")
    else:
        bot.reply_to(message, f"🆔 Ваш ID: `{user_id}`", parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def cmd_stats(message):
    user_id = message.chat.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Нет доступа.")
        return
    bot.reply_to(
        message,
        "📊 **СТАТИСТИКА**\n\n"
        f"👥 Пользователей: 0\n"
        f"💰 Баланс: 0 Благ\n"
        f"📦 Заказов: 0\n"
        f"📖 Сур загружено: {len(SURAS)}\n"
        "🪞 Зеркало работает стабильно.",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "📱 ОТКРЫТЬ ЗЕРКАЛО В БРАУЗЕРЕ")
def send_link(message):
    """Когда нажимают кнопку — отправляем ссылку"""
    bot.reply_to(
        message,
        f"📱 **ССЫЛКА НА ЗЕРКАЛО:**\n\n"
        f"https://{RENDER_HOSTNAME}/webapp\n\n"
        f"📌 **ВАЖНО:** Открой эту ссылку в браузере (Chrome, Safari).\n"
        f"🎤 Тогда голосовой ввод будет работать.\n\n"
        f"📋 Если ссылка не открывается — скопируй её вручную.",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(
        message,
        f"🪞 Я — Зеркало.\n\n"
        f"📱 Нажми кнопку **«📱 ОТКРЫТЬ ЗЕРКАЛО В БРАУЗЕРЕ»**,\n"
        f"чтобы получить ссылку на приложение.\n\n"
        f"🌐 Или напиши /link — я пришлю ссылку прямо сюда.",
        reply_markup=get_link_keyboard(),
        parse_mode="Markdown"
    )

# ==================================================
# 🌐 WEBAPP МАРШРУТЫ
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
    return """
    <h1>🪞 ЗЕРКАЛО</h1>
    <p>✅ Работает 24/7</p>
    <p><a href="/webapp">📱 Открыть приложение</a></p>
    """

# ==================================================
# 🚀 ЗАПУСК
# ==================================================

def run_bot():
    print("🤖 ЗАПУСКАЮ БОТА...")
    bot.infinity_polling(timeout=10)

if __name__ == "__main__":
    print("=" * 70)
    print("🪞 ЗЕРКАЛО ЗАПУСКАЕТСЯ...")
    print("=" * 70)
    print(f"👑 Хранитель ID: {FOUNDER_ID}")
    print(f"👑 Наследник ID: {TOMIRIS_ID}")
    print(f"🌐 ХОСТ: {RENDER_HOSTNAME}")
    print(f"📖 Сур загружено: {len(SURAS)}")
    print("=" * 70)
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=PORT)
