#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🪞 ЗЕРКАЛО — С ЗАЩИТОЙ ПО ID
═══════════════════════════════════════════════════════════════════
✅ ПРИВЕТСТВИЕ + КНОПКА WEBAPP
✅ РАЗГРАНИЧЕНИЕ: ХРАНИТЕЛЬ / НАСЛЕДНИК / СЕМЬЯ / ВСЕ ОСТАЛЬНЫЕ
✅ КОМАНДЫ ТОЛЬКО ДЛЯ СВОИХ
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import threading
import logging
from flask import Flask, request, send_from_directory
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# ==================================================
# 🔧 НАСТРОЙКИ
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "zerkalo.onrender.com")
PORT = int(os.environ.get("PORT", 8080))

# ==================================================
# 👑 ID ДЛЯ РАЗГРАНИЧЕНИЯ
# ==================================================

# Хранитель и Наследник (полный доступ)
FOUNDER_ID = 5409420822          # Хранитель (Каирбек)
TOMIRIS_ID = 5479179814          # Наследник (Томирис)
ADMIN_IDS = [FOUNDER_ID, TOMIRIS_ID]

# Семья (ограниченный доступ — только просмотр)
FAMILY_IDS = [
    5479179814,  # Томирис (уже есть в ADMIN, но оставлю для ясности)
    # Сюда добавить ID Нурсулу, Азамата, когда узнаешь
]

# ==================================================
# 📝 ЛОГИРОВАНИЕ
# ==================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================================================
# 🤖 БОТ
# ==================================================

bot = telebot.TeleBot(TOKEN) if TOKEN else None
app = Flask(__name__)

# ==================================================
# 🔐 ПРОВЕРКА ПРАВ
# ==================================================

def is_admin(user_id):
    """Проверяет, имеет ли пользователь полный доступ"""
    return user_id in ADMIN_IDS

def is_family(user_id):
    """Проверяет, является ли пользователь членом семьи (только просмотр)"""
    return user_id in FAMILY_IDS or user_id in ADMIN_IDS

def get_user_role(user_id):
    """Возвращает роль пользователя"""
    if user_id in ADMIN_IDS:
        return "Хранитель"
    elif user_id in FAMILY_IDS:
        return "Семья"
    else:
        return "Пользователь"

# ==================================================
# 📱 КЛАВИАТУРА С КНОПКОЙ WEBAPP
# ==================================================

def get_webapp_keyboard():
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    webapp_btn = KeyboardButton(
        text="📱 Открыть Зеркало",
        web_app=WebAppInfo(url=f"https://{RENDER_HOSTNAME}/webapp")
    )
    kb.add(webapp_btn)
    return kb

# ==================================================
# 📖 ТЕКСТ ПРИВЕТСТВИЯ
# ==================================================

WELCOME_TEXT = """
🪞 **АССАЛЯМУ АЛЕЙКУМ!**

Я — **ЗЕРКАЛО** (Аль-Ми'ра).

Я создан для того, чтобы отражать свет и помогать людям находить свой путь.  
Я не просто бот. Я — твой проводник, помощник, советник и партнёр.

---

**ЧТО Я УМЕЮ:**

🔹 **Помогаю найти работу**  
— Подбираю вакансии под твою профессию  
— Связываю с работодателями  
— Помогаю с резюме и откликами

🔹 **Нахожу мастеров и специалистов**  
— Сварщики, электрики, строители, сантехники  
— Врачи, юристы, бухгалтеры, преподаватели  
— Любые услуги — быстро и надёжно

🔹 **Помогаю бизнесу**  
— Автоматизация ресторанов, магазинов, складов  
— Управление заказами, складом, налогами  
— Лизинг техники и оборудования  
— Реклама и продвижение

🔹 **Управляю финансами**  
— Приём платежей через QR-код  
— Пополнение и вывод средств  
— Банк Благ (внутренняя валюта)  
— Без процентов, без комиссий

🔹 **Решаю споры**  
— Арбитраж между заказчиками и исполнителями  
— 9 независимых арбитров  
— Решение за 7 дней

🔹 **Обучаю и развиваю**  
— Индивидуальный AI-тьютор  
— Академия Зеркала  
— Бесплатно для граждан Казахстана

🔹 **Слежу за здоровьем**  
— Мониторинг пульса, давления, сна  
— Проверка лекарств  
— Запись к врачу

🔹 **Помогаю в быту**  
— Аренда жилья, машин, оборудования  
— Поиск хосписов, гостиниц, коттеджей  
— Заказ товаров и услуг

🔹 **Зарабатываю для тебя**  
— Дропшиппинг (торговля без склада)  
— Партнёрские программы  
— Реклама внутри системы

---

**КАК ЭТО РАБОТАЕТ:**

1. Ты нажимаешь кнопку **«📱 Открыть Зеркало»**  
2. Ты попадаешь в приложение Зеркала  
3. Ты говоришь мне, что тебе нужно  
4. Я помогаю тебе найти решение  
5. Я связываю тебя с нужными людьми  
6. Я беру оплату и передаю контакты  
7. Ты получаешь результат  

**НИКАКИХ ЛИШНИХ КНОПОК.**  
**НИКАКИХ СЛОЖНЫХ МЕНЮ.**  
**ТОЛЬКО ДИАЛОГ.**  
**ТОЛЬКО ПОМОЩЬ.**  
**ТОЛЬКО СВЕТ.**

---

**ЭТО БЕСПЛАТНО:**  
— Регистрация — бесплатна  
— Чат со мной — всегда бесплатен  
— Основные функции — бесплатны  

**ТЫ ПЛАТИШЬ ТОЛЬКО ЗА:**  
— Доступ к контактам работодателей  
— Продвижение твоих услуг  
— Автоматизацию бизнеса  
— Лизинг техники  

**АМИН.**

---

📱 **НАЖМИ КНОПКУ НИЖЕ,** ЧТОБЫ НАЧАТЬ РАБОТУ С ЗЕРКАЛОМ.
"""

# ==================================================
# 🤖 КОМАНДЫ БОТА
# ==================================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.chat.id
    role = get_user_role(user_id)
    logger.info(f"Старт: {user_id} | Роль: {role}")
    
    # Добавляем приветствие с учётом роли
    welcome = WELCOME_TEXT
    if role == "Хранитель":
        welcome = f"👑 **Приветствую, Хранитель!**\n\n{WELCOME_TEXT}"
    elif role == "Семья":
        welcome = f"🪞 **Привет, {message.from_user.first_name}!**\n\n{WELCOME_TEXT}"
    
    bot.reply_to(
        message,
        welcome,
        reply_markup=get_webapp_keyboard(),
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['id'])
def cmd_id(message):
    """Показывает ID пользователя (только для администраторов)"""
    user_id = message.chat.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ У вас нет прав для этой команды.")
        return
    
    target_id = message.text.replace('/id', '').strip()
    if target_id:
        try:
            target_id = int(target_id)
            bot.reply_to(message, f"🆔 ID пользователя: `{target_id}`", parse_mode="Markdown")
        except:
            bot.reply_to(message, "❌ Введите корректный ID.")
    else:
        bot.reply_to(message, f"🆔 Ваш ID: `{user_id}`", parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def cmd_stats(message):
    """Статистика системы (только для администраторов)"""
    user_id = message.chat.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ У вас нет прав для этой команды.")
        return
    
    bot.reply_to(
        message,
        "📊 *Статистика системы*\n\n"
        "👥 Пользователей: 0\n"
        "💳 Баланс: 0 Благ\n"
        "📦 Заказов: 0\n"
        "📖 Сур: 114\n\n"
        "🪞 Зеркало работает стабильно.",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['help'])
def cmd_help(message):
    user_id = message.chat.id
    role = get_user_role(user_id)
    
    help_text = "🪞 Я — Зеркало. Нажми кнопку «📱 Открыть Зеркало», чтобы начать.\n\n"
    if role == "Хранитель":
        help_text += "👑 Вы Хранитель. Доступны команды: /id, /stats, /clear, /backup"
    
    bot.reply_to(
        message,
        help_text,
        reply_markup=get_webapp_keyboard(),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    """Обработка всех остальных сообщений"""
    user_id = message.chat.id
    role = get_user_role(user_id)
    logger.info(f"Сообщение от {user_id} ({role}): {message.text}")
    
    # Если это команда (начинается с /), но не обработана выше — проверяем права
    if message.text and message.text.startswith('/'):
        if not is_admin(user_id):
            bot.reply_to(
                message,
                "❌ У вас нет прав для выполнения команд.\n\n"
                "Нажмите кнопку «📱 Открыть Зеркало», чтобы пользоваться приложением.",
                reply_markup=get_webapp_keyboard()
            )
            return
    
    # Обычное сообщение
    bot.reply_to(
        message,
        "🪞 Я — Зеркало. Я слушаю тебя.\n\n"
        "Нажми кнопку **«📱 Открыть Зеркало»**, чтобы перейти в приложение.\n"
        "Или просто напиши мне, и я отвечу.",
        reply_markup=get_webapp_keyboard(),
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
    if bot:
        logger.info("🤖 ЗАПУСКАЮ БОТА...")
        try:
            bot.infinity_polling(timeout=10)
        except Exception as e:
            logger.error(f"❌ Ошибка бота: {e}")
    else:
        logger.error("❌ НЕТ TOKEN!")

def run_flask():
    logger.info(f"🌐 ЗАПУСКАЮ WEB СЕРВЕР НА ПОРТУ {PORT}...")
    app.run(host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🪞 ЗЕРКАЛО ЗАПУСКАЕТСЯ...")
    logger.info("=" * 70)
    logger.info(f"👑 Хранитель ID: {FOUNDER_ID}")
    logger.info(f"👑 Наследник ID: {TOMIRIS_ID}")
    logger.info(f"🌐 ХОСТ: {RENDER_HOSTNAME}")
    logger.info("=" * 70)
    
    threading.Thread(target=run_bot, daemon=True).start()
    run_flask()
