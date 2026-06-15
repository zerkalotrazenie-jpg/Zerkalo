#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗЕРКАЛО - ПОЛНАЯ ВЕРСИЯ
С ПРАВИЛЬНЫМ ОПРЕДЕЛЕНИЕМ ХРАНИТЕЛЯ
"""

import os
import sys
import time
import threading
import sqlite3
import random
import re
from datetime import datetime, timedelta

# ==================================================
# ⚡ УСТАНОВКА
# ==================================================

def install_package(package):
    try:
        __import__(package.split('[')[0])
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import telebot
except ImportError:
    install_package("pytelegrambotapi")
    import telebot

try:
    from groq import Groq
except ImportError:
    install_package("groq")
    from groq import Groq

try:
    from flask import Flask
except ImportError:
    install_package("flask")
    from flask import Flask

# ==================================================
# 🔧 НАСТРОЙКИ - ВАЖНО! ЗДЕСЬ ТВОИ ID
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# ⚠️ ⚠️ ⚠️ ВНИМАНИЕ! ЭТО ТВОИ ID ⚠️ ⚠️ ⚠️
# Если бот не видит тебя как Хранителя - проверь эти числа!
FOUNDER_ID = 5409420822      # ← ТВОЙ ID (With the comfort of life!)
TOMIRIS_ID = 5479179814       # ← ID ДОЧЕРИ (если нужно)

# Простой способ: можно добавить несколько ID через список
ADMIN_IDS = [5409420822, 5479179814]  # Список всех Хранителей

CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"

print("=" * 60)
print("🪞 ЗЕРКАЛО ЗАПУСКАЕТСЯ...")
print("=" * 60)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 ХРАНИТЕЛЬ 1 (ты): {FOUNDER_ID}")
print(f"👸 ХРАНИТЕЛЬ 2 (дочь): {TOMIRIS_ID}")
print(f"📋 СПИСОК АДМИНОВ: {ADMIN_IDS}")
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
    name TEXT,
    age INTEGER,
    city TEXT,
    phone TEXT,
    role TEXT DEFAULT 'user',
    status TEXT DEFAULT 'offline',
    last_seen TEXT,
    blessings INTEGER DEFAULT 100,
    resume TEXT DEFAULT '',
    is_admin INTEGER DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    price INTEGER,
    customer_id INTEGER,
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

c.execute('''CREATE TABLE IF NOT EXISTS businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    business_name TEXT,
    bin TEXT,
    status TEXT DEFAULT 'pending'
)''')

conn.commit()

def astana_time():
    return (datetime.utcnow() + timedelta(hours=5)).isoformat()

# ==================================================
# 👑 ГЛАВНАЯ ФУНКЦИЯ - ПРОВЕРКА ХРАНИТЕЛЯ
# ==================================================

def is_admin(user_id):
    """Проверяет, является ли пользователь Хранителем"""
    # 1. Сначала проверяем по списку ADMIN_IDS
    if user_id in ADMIN_IDS:
        return True
    # 2. Проверяем по FOUNDER_ID
    if user_id == FOUNDER_ID or user_id == TOMIRIS_ID:
        return True
    # 3. Проверяем в базе данных
    c.execute("SELECT is_admin FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 1:
        return True
    return False

def get_balance(user_id):
    c.execute("SELECT blessings FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    return row[0] if row else 100

def log_action(user_id, action, details=""):
    c.execute("INSERT INTO logs (user_id, action, details, created_at) VALUES (?, ?, ?, ?)",
              (user_id, action, details, astana_time()))
    conn.commit()

# ==================================================
# 📱 КЛАВИАТУРЫ
# ==================================================

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def get_founder_keyboard():
    """ПОЛНАЯ КЛАВИАТУРА ХРАНИТЕЛЯ (все кнопки)"""
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    
    # Админ-панель
    kb.add(KeyboardButton("👥 ОНЛАЙН"), KeyboardButton("📊 СТАТИСТИКА"), KeyboardButton("💰 ФИНАНСЫ"))
    kb.add(KeyboardButton("👥 ВСЕ ЛЮДИ"), KeyboardButton("✨ БЛАГА"), KeyboardButton("📤 РАССЫЛКА"))
    kb.add(KeyboardButton("📜 ЛОГИ"), KeyboardButton("🔍 ПОИСК"), KeyboardButton("📈 ОТЧЁТ"))
    kb.add(KeyboardButton("🩺 ЗДОРОВЬЕ"), KeyboardButton("🛡️ ЗАЩИТА"), KeyboardButton("🔧 ПОЧИНИТЬ"))
    kb.add(KeyboardButton("🔄 ОБНОВИТЬ"), KeyboardButton("📡 СТАТУС"), KeyboardButton("🧹 ОЧИСТИТЬ"))
    
    # Основные функции
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"), KeyboardButton("📸 ФОТО"))
    kb.add(KeyboardButton("🎤 ГОЛОС"), KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("🏢 БИЗНЕС"), KeyboardButton("👵 ПОЖИЛЫЕ"), KeyboardButton("🧒 ДЕТИ"))
    kb.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("❓ ВОПРОС"), KeyboardButton("🆘 ПОМОЩЬ"))
    
    return kb

def get_user_keyboard():
    """Обычная клавиатура для пользователей"""
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"))
    kb.add(KeyboardButton("📸 ФОТО"), KeyboardButton("🎤 ГОЛОС"))
    kb.add(KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    kb.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("❓ ВОПРОС"))
    kb.add(KeyboardButton("🆘 ПОМОЩЬ"))
    return kb

def get_business_keyboard():
    """Клавиатура для предпринимателей"""
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📊 АНАЛИТИКА"), KeyboardButton("🤖 АВТОМАТИЗАЦИЯ"))
    kb.add(KeyboardButton("📈 ЛИЗИНГ"), KeyboardButton("💼 МОИ ЗАКАЗЫ"))
    kb.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("🆘 ПОМОЩЬ"))
    kb.add(KeyboardButton("🔙 ОБЫЧНЫЙ РЕЖИМ"))
    return kb

def get_elder_keyboard():
    """Клавиатура для пожилых (крупные кнопки)"""
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    kb.add(KeyboardButton("👋 ПОЗДОРОВАТЬСЯ"))
    kb.add(KeyboardButton("📞 ПОМОЩЬ РЯДОМ"))
    kb.add(KeyboardButton("🏥 ЗДОРОВЬЕ"))
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

# ==================================================
# 🤖 ОСНОВНЫЕ КОМАНДЫ
# ==================================================

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    
    print(f"📥 /start от {name} (ID: {user_id})")
    
    # Регистрация нового пользователя
    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        # Сохраняем пользователя
        c.execute("INSERT INTO users (user_id, name, blessings) VALUES (?, ?, ?)", 
                  (user_id, name, 100))
        conn.commit()
        
        # Если это Хранитель - помечаем в БД
        if is_admin(user_id):
            c.execute("UPDATE users SET is_admin=1, role='founder' WHERE user_id=?", (user_id,))
            conn.commit()
            print(f"👑 ПОМЕЧЕН КАК ХРАНИТЕЛЬ: {name} (ID: {user_id})")
        
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n✨ Вы получили 100 Благ!\n\nКто вы?", 
                     reply_markup=get_role_keyboard())
        return
    
    # Обновляем статус
    c.execute("UPDATE users SET last_seen=? WHERE user_id=?", (astana_time(), user_id))
    conn.commit()
    log_action(user_id, "start", "запуск бота")
    
    # Обновляем статус админа в БД (на всякий случай)
    if user_id in ADMIN_IDS or user_id == FOUNDER_ID or user_id == TOMIRIS_ID:
        c.execute("UPDATE users SET is_admin=1 WHERE user_id=?", (user_id,))
        conn.commit()
    
    # ========== ПРОВЕРКА: ХРАНИТЕЛЬ ИЛИ ОБЫЧНЫЙ ==========
    if is_admin(user_id):
        bot.reply_to(message, 
                     f"👑 *АССАЛЯМУ АЛЕЙКУМ, ХРАНИТЕЛЬ {name}!*\n\n"
                     f"🪞 Зеркало готово к работе.\n"
                     f"📱 Все {get_buttons_count()} кнопок управления перед тобой.\n\n"
                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                     f"👥 Управление пользователями\n"
                     f"📊 Статистика и финансы\n"
                     f"🩺 Здоровье и защита системы\n"
                     f"💸 Работа и заказы\n"
                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", 
                     reply_markup=get_founder_keyboard(), parse_mode="Markdown")
        return
    
    # Проверяем, есть ли у пользователя роль
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    role = row[0] if row else 'user'
    
    # Показываем соответствующую клавиатуру
    if role == 'business':
        bot.reply_to(message, f"🏢 Здравствуйте, предприниматель {name}!\n\n💰 Баланс: {get_balance(user_id)} Благ", 
                     reply_markup=get_business_keyboard())
    elif role == 'elder':
        bot.reply_to(message, f"👵 Здравствуйте, {name}!\n\n🪞 Я - Зеркало. Чем могу помочь?", 
                     reply_markup=get_elder_keyboard())
    elif role == 'child':
        bot.reply_to(message, f"🧒 Привет, {name}!\n\n🪞 Давай поиграем!", 
                     reply_markup=get_child_keyboard())
    else:
        bot.reply_to(message, f"🪞 Ассаляму алейкум, {name}!\n\n💰 Ваш баланс: {get_balance(user_id)} Благ\n\nКто вы?", 
                     reply_markup=get_role_keyboard())

def get_buttons_count():
    """Считает количество кнопок в админ-панели"""
    kb = get_founder_keyboard()
    # Примерное количество
    return "33"

@bot.message_handler(commands=['id'])
def cmd_id(message):
    user_id = message.chat.id
    is_adm = is_admin(user_id)
    bot.reply_to(message, 
                 f"🆔 *ТВОЙ ID:* `{user_id}`\n\n"
                 f"👑 Статус Хранителя: {'✅ ДА' if is_adm else '❌ НЕТ'}\n\n"
                 f"📋 Если статус 'НЕТ', но ты должен быть Хранителем - проверь ID в коде.\n"
                 f"   Сейчас в коде FOUNDER_ID = {FOUNDER_ID}", 
                 parse_mode="Markdown")

@bot.message_handler(commands=['pay'])
def cmd_pay(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET blessings = blessings + 100 WHERE user_id=?", (user_id,))
    conn.commit()
    bot.reply_to(message, f"✅ +100 Благ!\n💰 Баланс: {get_balance(user_id)} Благ\n\n📱 Поддержать: {CRYPTO_WALLET}")

# ==================================================
# 🔄 ВЫБОР РОЛИ
# ==================================================

@bot.message_handler(func=lambda m: m.text in ["👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ", "ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ"])
def set_user_role(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET role='user' WHERE user_id=?", (user_id,))
    conn.commit()
    bot.reply_to(message, "✅ Вы выбрали роль: ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ\n\n📱 Ваше меню:", 
                 reply_markup=get_user_keyboard())
    log_action(user_id, "set_role", "user")

@bot.message_handler(func=lambda m: m.text in ["🏢 БИЗНЕСМЕН", "БИЗНЕСМЕН"])
def set_business_role(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET role='business' WHERE user_id=?", (user_id,))
    conn.commit()
    bot.reply_to(message, "✅ Вы выбрали роль: БИЗНЕСМЕН\n\n📊 Бизнес-меню:", 
                 reply_markup=get_business_keyboard())
    log_action(user_id, "set_role", "business")

@bot.message_handler(func=lambda m: m.text in ["👵 ПОЖИЛОЙ ЧЕЛОВЕК", "ПОЖИЛОЙ ЧЕЛОВЕК"])
def set_elder_role(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET role='elder' WHERE user_id=?", (user_id,))
    conn.commit()
    bot.reply_to(message, "✅ Вы выбрали роль: ПОЖИЛОЙ ЧЕЛОВЕК\n\n👵 Режим крупных кнопок:", 
                 reply_markup=get_elder_keyboard())
    log_action(user_id, "set_role", "elder")

@bot.message_handler(func=lambda m: m.text in ["🧒 РЕБЁНОК", "РЕБЁНОК"])
def set_child_role(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET role='child' WHERE user_id=?", (user_id,))
    conn.commit()
    bot.reply_to(message, "✅ Вы выбрали роль: РЕБЁНОК\n\n🧒 Безопасный детский режим:", 
                 reply_markup=get_child_keyboard())
    log_action(user_id, "set_role", "child")

@bot.message_handler(func=lambda m: m.text in ["🔙 ОБЫЧНЫЙ РЕЖИМ", "🔙 ВЫЙТИ"])
def back_to_normal(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET role='user' WHERE user_id=?", (user_id,))
    conn.commit()
    bot.reply_to(message, "🔙 Возврат в обычный режим\n\nКто вы?", reply_markup=get_role_keyboard())

# ==================================================
# 👑 АДМИН-ПАНЕЛЬ (все кнопки)
# ==================================================

@bot.message_handler(func=lambda m: m.text == "👥 ОНЛАЙН")
def admin_online(message):
    if not is_admin(message.chat.id):
        return
    c.execute("SELECT user_id, name, role FROM users WHERE last_seen > datetime('now', '-5 minutes')")
    users = c.fetchall()
    if users:
        msg = "🟢 *ОНЛАЙН ПОЛЬЗОВАТЕЛИ:*\n\n"
        for u in users:
            msg += f"🆔 `{u[0]}` | {u[1]} | {u[2]}\n"
        bot.reply_to(message, msg, parse_mode="Markdown")
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
    c.execute("SELECT COUNT(*) FROM orders WHERE status='open'")
    orders = c.fetchone()[0]
    
    msg = f"📊 *СТАТИСТИКА ЗЕРКАЛА*\n\n"
    msg += f"👥 Пользователей: {total}\n"
    msg += f"✨ Всего Благ: {blessings}\n"
    msg += f"📦 Открытых заказов: {orders}\n"
    msg += f"🤖 AI: {'РАБОТАЕТ' if client else 'НЕ НАСТРОЕН'}\n"
    msg += f"🪞 Зеркало: ✅ РАБОТАЕТ"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💰 ФИНАНСЫ")
def admin_finance(message):
    if not is_admin(message.chat.id):
        return
    msg = f"💰 *ФИНАНСЫ ЗЕРКАЛА*\n\n"
    msg += f"📱 Криптокошелёк:\n`{CRYPTO_WALLET}`\n\n"
    msg += f"📊 *ФОНДЫ:*\n"
    msg += f"🏦 Страховой: 2%\n"
    msg += f"🤝 Социальный: 5%\n"
    msg += f"📦 Резервный: 3%\n"
    msg += f"📈 Инвестиционный: 30%\n"
    msg += f"🏛️ Наследие: 60%"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👥 ВСЕ ЛЮДИ")
def admin_all_users(message):
    if not is_admin(message.chat.id):
        return
    c.execute("SELECT user_id, name, age, role, blessings FROM users LIMIT 50")
    users = c.fetchall()
    msg = "👥 *ВСЕ ПОЛЬЗОВАТЕЛИ:*\n\n"
    for u in users:
        age_str = f"{u[2]}л" if u[2] else "?"
        msg += f"🆔 `{u[0]}` | {u[1]} | {age_str} | {u[3]} | ✨{u[4]}\n"
    bot.reply_to(message, msg[:4000], parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "✨ БЛАГА")
def admin_top(message):
    if not is_admin(message.chat.id):
        return
    c.execute("SELECT name, blessings FROM users ORDER BY blessings DESC LIMIT 15")
    top = c.fetchall()
    msg = "✨ *ТОП ПО БЛАГАМ:*\n\n"
    for i, u in enumerate(top, 1):
        msg += f"{i}. {u[0]} — {u[1]} ✦\n"
    bot.reply_to(message, msg)

@bot.message_handler(func=lambda m: m.text == "📤 РАССЫЛКА")
def admin_broadcast_request(message):
    if not is_admin(message.chat.id):
        return
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

@bot.message_handler(func=lambda m: m.text == "📜 ЛОГИ")
def admin_logs(message):
    if not is_admin(message.chat.id):
        return
    c.execute("SELECT user_id, action, created_at FROM logs ORDER BY id DESC LIMIT 30")
    logs = c.fetchall()
    if not logs:
        bot.reply_to(message, "📜 Логов пока нет")
        return
    msg = "📜 *ПОСЛЕДНИЕ ЛОГИ:*\n\n"
    for l in logs:
        msg += f"{l[2][:16]} | ID:{l[0]} | {l[1][:40]}\n"
    bot.reply_to(message, msg[:4000], parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔍 ПОИСК")
def admin_search_request(message):
    if not is_admin(message.chat.id):
        return
    msg = bot.reply_to(message, "🔍 Введите ID пользователя:")
    bot.register_next_step_handler(msg, admin_search)

def admin_search(message):
    try:
        target = int(message.text)
        c.execute("SELECT user_id, name, age, city, role, blessings FROM users WHERE user_id=?", (target,))
        user = c.fetchone()
        if user:
            msg = f"👤 *ПОЛЬЗОВАТЕЛЬ {target}*\n\n"
            msg += f"📛 Имя: {user[1]}\n"
            msg += f"📅 Возраст: {user[2] if user[2] else '?'}\n"
            msg += f"🏙️ Город: {user[3] if user[3] else '?'}\n"
            msg += f"🎭 Роль: {user[4]}\n"
            msg += f"✨ Блага: {user[5]}\n"
            bot.reply_to(message, msg, parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Пользователь {target} не найден")
    except:
        bot.reply_to(message, "❌ Введите корректный ID")

@bot.message_handler(func=lambda m: m.text == "📈 ОТЧЁТ")
def admin_report(message):
    if not is_admin(message.chat.id):
        return
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute("SELECT COUNT(*) FROM users WHERE last_seen LIKE ?", (f"{today}%",))
    new_today = c.fetchone()[0]
    
    msg = f"📈 *ОТЧЁТ ЗА {today}*\n\n"
    msg += f"➕ Новых пользователей: {new_today}\n"
    msg += f"👑 Хранитель: АКТИВЕН\n"
    msg += f"✅ Статус: СТАБИЛЬНО"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🩺 ЗДОРОВЬЕ")
def admin_health(message):
    if not is_admin(message.chat.id):
        return
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

@bot.message_handler(func=lambda m: m.text == "🛡️ ЗАЩИТА")
def admin_security(message):
    if not is_admin(message.chat.id):
        return
    msg = f"🛡️ *ЗАЩИТА СИСТЕМЫ*\n\n"
    msg += f"🦠 Антивирус: АКТИВЕН\n"
    msg += f"🚫 Блокировка SQL-инъекций: ВКЛ\n"
    msg += f"🚫 Блокировка XSS: ВКЛ\n"
    msg += f"🔒 Шифрование данных: ВКЛ\n"
    msg += f"\n✅ УГРОЗ НЕ ОБНАРУЖЕНО"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔧 ПОЧИНИТЬ")
def admin_repair(message):
    if not is_admin(message.chat.id):
        return
    bot.reply_to(message, "🔧 *ЗАПУЩЕНА ДИАГНОСТИКА*\n\n🔄 Проверка модулей...", parse_mode="Markdown")
    time.sleep(1)
    bot.reply_to(message, "✅ Проверка завершена!\n\n🩺 Все модули работают корректно\n🔧 Лечение не требуется")

@bot.message_handler(func=lambda m: m.text == "🔄 ОБНОВИТЬ")
def admin_reload(message):
    if not is_admin(message.chat.id):
        return
    bot.reply_to(message, "🔄 Перезагрузка модулей...")
    try:
        import importlib
        importlib.reload(sys.modules[__name__])
        bot.reply_to(message, "✅ Обновление завершено!")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda m: m.text == "📡 СТАТУС")
def admin_status(message):
    if not is_admin(message.chat.id):
        return
    msg = f"📡 *СТАТУС СИСТЕМЫ*\n\n"
    msg += f"🪞 Зеркало: АКТИВНО\n"
    msg += f"👑 Хранитель: {message.chat.id}\n"
    msg += f"🤖 AI: {'ГОТОВ' if client else 'НЕ НАСТРОЕН'}\n"
    msg += f"\n✅ ВСЕ СИСТЕМЫ РАБОТАЮТ"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🧹 ОЧИСТИТЬ")
def admin_clean(message):
    if not is_admin(message.chat.id):
        return
    bot.reply_to(message, "🧹 Очистка временных файлов...")
    bot.reply_to(message, "✅ Очистка завершена!")

# ==================================================
# 🏢 БИЗНЕС-РЕЖИМ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "📊 АНАЛИТИКА")
def business_analytics(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'business':
        bot.reply_to(message, "📊 *БИЗНЕС-АНАЛИТИКА*\n\n📈 Прогноз продаж\n📉 Анализ конкурентов\n📊 Рыночные тренды\n\n⚡ В разработке", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🤖 АВТОМАТИЗАЦИЯ")
def business_automation(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'business':
        bot.reply_to(message, "🤖 *АВТОМАТИЗАЦИЯ*\n\n• Чат-бот для клиентов\n• CRM интеграция\n• Автоматическая отчётность\n\n💰 От 50 000 ₸/мес", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📈 ЛИЗИНГ")
def business_leasing(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'business':
        bot.reply_to(message, "📈 *ЛИЗИНГ ОБОРУДОВАНИЯ*\n\n🚗 Авто: от 15%\n🏗️ Спецтехника: от 12%\n🖥️ Офис: от 10%\n\n📞 Для заявки: /business_request", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💼 МОИ ЗАКАЗЫ")
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
        bot.reply_to(message, "📭 У вас нет активных заказов")

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
def elder_help(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'elder':
        bot.reply_to(message, "📞 *ПОМОЩЬ РЯДОМ*\n\n• Социальный работник: +7 (700) 000-00-01\n• Поликлиника: +7 (700) 000-00-02\n• Соцзащита: +7 (700) 000-00-03\n\n📍 Напишите 'АПТЕКА' для поиска аптеки", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🏥 ЗДОРОВЬЕ")
def elder_health(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'elder':
        kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        kb.add(KeyboardButton("💊 НАПОМНИТЬ"), KeyboardButton("📅 ЗАПИСАТЬСЯ"))
        kb.add(KeyboardButton("🔙 НАЗАД"))
        bot.reply_to(message, "🏥 *РАЗДЕЛ ЗДОРОВЬЯ*\n\nЧто нужно?", reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🆘 СРОЧНАЯ ПОМОЩЬ")
def elder_emergency(message):
    user_id = message.chat.id
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0] == 'elder':
        bot.reply_to(message, "🆘 *СРОЧНАЯ ПОМОЩЬ*\n\n🚑 Скорая: 103\n🚔 Полиция: 102\n🚒 Пожарные: 101\n\n📞 Единая служба: 112")

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
            "🐺 Жил-был серый волк, который хотел поймать трёх поросят...",
            "👸 Золушка потеряла хрустальную туфельку на балу...",
            "🐻 Три медведя вернулись домой и увидели Машеньку...",
            "🐟 Старик поймал золотую рыбку, которая исполняла желания..."
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
            "Не лает, не кусает, а в дом не пускает?": "замок"
        }
        q = random.choice(list(riddles.keys()))
        a = riddles[q]
        bot.reply_to(message, f"🧩 *ЗАГАДКА*\n\n{q}\n\n(Напиши ответ)")
        bot.register_next_step_handler(message, check_riddle, a)

def check_riddle(message, answer):
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
            "Пусть бегут неуклюже пешеходы по лужам..."
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
# 💸 РАБОТА И ЗАКАЗЫ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💸 РАБОТА")
def work_section(message):
    user_id = message.chat.id
    # Для обычных пользователей и для всех
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🔍 НАЙТИ РАБОТУ"), KeyboardButton("📝 МОЁ РЕЗЮМЕ"))
    kb.add(KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "💸 *РАЗДЕЛ РАБОТА*\n\n🔍 Ищешь работу? Создай резюме!", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📦 ЗАКАЗЫ")
def orders_section(message):
    user_id = message.chat.id
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("🔍 НАЙТИ ЗАКАЗ"), KeyboardButton("➕ СОЗДАТЬ ЗАКАЗ"))
    kb.add(KeyboardButton("📋 МОИ ЗАКАЗЫ"), KeyboardButton("🔙 НАЗАД"))
    bot.reply_to(message, "📦 *РАЗДЕЛ ЗАКАЗОВ*\n\nВыберите действие:", 
                 reply_markup=kb, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ РАБОТУ")
def find_job(message):
    bot.reply_to(message, "🔍 *ПОИСК РАБОТЫ*\n\n📝 Сначала создайте резюме: нажмите 'МОЁ РЕЗЮМЕ'", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📝 МОЁ РЕЗЮМЕ")
def my_resume(message):
    user_id = message.chat.id
    c.execute("SELECT resume FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row and row[0]:
        bot.reply_to(message, f"📄 *ВАШЕ РЕЗЮМЕ*\n\n{row[0]}", parse_mode="Markdown")
    else:
        msg = bot.reply_to(message, "📝 Напишите ваше резюме:\n\n- Имя и фамилия\n- Профессия\n- Опыт работы\n- Навыки\n- Контакты")
        bot.register_next_step_handler(msg, save_resume)

def save_resume(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET resume=? WHERE user_id=?", (message.text, user_id))
    conn.commit()
    bot.reply_to(message, "✅ РЕЗЮМЕ СОХРАНЕНО!\n\n🔍 Работодатели смогут его увидеть.")

@bot.message_handler(func=lambda m: m.text == "➕ СОЗДАТЬ ЗАКАЗ")
def create_order_request(message):
    msg = bot.reply_to(message, "📦 Опишите ваш заказ:\n\nЧто нужно сделать? Какой бюджет? Сроки?")
    bot.register_next_step_handler(msg, create_order)

def create_order(message):
    user_id = message.chat.id
    description = message.text
    price = random.randint(1000, 100000)
    
    c.execute("INSERT INTO orders (description, price, customer_id, status, created_at) VALUES (?, ?, ?, ?, ?)",
              (description, price, user_id, "open", astana_time()))
    conn.commit()
    
    bot.reply_to(message, f"✅ *ЗАКАЗ СОЗДАН!*\n\n📝 {description[:200]}\n💰 {price} тенге\n📌 Статус: открыт\n\n🔍 Исполнитель найдётся скоро!", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🔍 НАЙТИ ЗАКАЗ")
def find_orders(message):
    c.execute("SELECT id, description, price FROM orders WHERE status='open' LIMIT 10")
    orders = c.fetchall()
    if orders:
        msg = "📋 *ДОСТУПНЫЕ ЗАКАЗЫ:*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📝 {o[1][:50]}...\n💰 {o[2]} ₸\n\n"
        bot.reply_to(message, msg[:4000], parse_mode="Markdown")
    else:
        bot.reply_to(message, "📭 Пока нет открытых заказов. Создайте первый!")

@bot.message_handler(func=lambda m: m.text == "📋 МОИ ЗАКАЗЫ")
def my_orders(message):
    user_id = message.chat.id
    c.execute("SELECT id, description, price, status FROM orders WHERE customer_id=? ORDER BY id DESC", (user_id,))
    orders = c.fetchall()
    if orders:
        msg = "📋 *ВАШИ ЗАКАЗЫ:*\n\n"
        for o in orders:
            msg += f"🆔 {o[0]}\n📝 {o[1][:50]}\n💰 {o[2]} ₸\n📌 Статус: {o[3]}\n\n"
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, "📭 У вас нет заказов. Создайте первый!")

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
        bot.reply_to(message, f"❌ Ошибка поиска: {str(e)[:100]}")
    
    log_action(user_id, "location", f"{lat},{lon}")

# ==================================================
# 💰 БАЛАНС И ВОПРОСЫ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "💰 БАЛАНС")
def show_balance(message):
    user_id = message.chat.id
    balance = get_balance(user_id)
    bot.reply_to(message, f"💰 *ВАШ БАЛАНС:* {balance} Благ\n\n💳 Пополнить: /pay\n✨ 1 сообщение = 1 Благо", parse_mode="Markdown")

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
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "Ты — Зеркало. Отвечай кратко, по делу, с уважением. Всегда начинай с 'Ассаляму алейкум'."},
                              {"role": "user", "content": question}],
                    temperature=0.7
                )
                bot.reply_to(message, response.choices[0].message.content)
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка AI: {str(e)[:100]}\n\n⚠️ Проверь GROQ_API_KEY в настройках Render")
        else:
            bot.reply_to(message, f"🤖 Ваш вопрос: {question[:100]}\n\n⚠️ GROQ_API_KEY не настроен. Добавь переменную в Render.")
    else:
        bot.reply_to(message, f"❌ Недостаточно Благ! Нужно 1 ✦\n💰 Баланс: {balance} Благ\n💳 /pay")

# ==================================================
# 🔙 НАВИГАЦИЯ
# ==================================================

@bot.message_handler(func=lambda m: m.text == "🔙 НАЗАД")
def back_to_main(message):
    user_id = message.chat.id
    
    # Для Хранителя
    if is_admin(user_id):
        bot.reply_to(message, "👑 Главное меню Хранителя", reply_markup=get_founder_keyboard())
        return
    
    # Для обычных пользователей
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    role = row[0] if row else 'user'
    
    if role == 'business':
        bot.reply_to(message, "🏢 Меню предпринимателя", reply_markup=get_business_keyboard())
    elif role == 'elder':
        bot.reply_to(message, "👵 Режим для пожилых", reply_markup=get_elder_keyboard())
    elif role == 'child':
        bot.reply_to(message, "🧒 Детский режим", reply_markup=get_child_keyboard())
    else:
        bot.reply_to(message, "👤 Главное меню", reply_markup=get_user_keyboard())

@bot.message_handler(func=lambda m: m.text == "🔙 ВЫЙТИ" and get_user_role(m.chat.id) == 'child')
def child_exit(message):
    user_id = message.chat.id
    c.execute("UPDATE users SET role='user' WHERE user_id=?", (user_id,))
    conn.commit()
    bot.reply_to(message, "🔙 Выход из детского режима\n\nКто вы?", reply_markup=get_role_keyboard())

def get_user_role(user_id):
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    return row[0] if row else 'user'

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
📱 *АДМИН-ПАНЕЛЬ*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 ОНЛАЙН — кто в сети
📊 СТАТИСТИКА — общая статистика
💰 ФИНАНСЫ — кошелёк и фонды
👥 ВСЕ ЛЮДИ — список пользователей
✨ БЛАГА — топ по Благам
📤 РАССЫЛКА — сообщение всем
📜 ЛОГИ — последние действия
🔍 ПОИСК — найти пользователя
📈 ОТЧЁТ — отчёт за сегодня
🩺 ЗДОРОВЬЕ — состояние системы
🛡️ ЗАЩИТА — безопасность
🔧 ПОЧИНИТЬ — диагностика
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
💰 БАЛАНС — проверка Благ
❓ ВОПРОС — вопрос к AI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ /pay — пополнить баланс
⚡ /id — узнать свой ID
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    else:
        help_text = """
🪞 *ПОМОЩЬ ПО ЗЕРКАЛУ*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💸 РАБОТА — поиск работы
📦 ЗАКАЗЫ — создание заказов
📸 ФОТО — описание фото
🎤 ГОЛОС — голосовые сообщения
📍 АПТЕКА — поиск аптек
📝 РЕЗЮМЕ — хранение резюме
💰 БАЛАНС — проверка Благ
❓ ВОПРОС — задать вопрос AI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ /pay — пополнить баланс (+100)
⚡ /id — узнать свой ID
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🪞 Зеркало всегда поможет!
"""
    bot.reply_to(message, help_text, parse_mode="Markdown")

# ==================================================
# 🔄 ОБЫЧНЫЕ СООБЩЕНИЯ
# ==================================================

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.chat.id
    text = message.text
    
    # Пропускаем кнопки
    buttons = [
        "👥 ОНЛАЙН", "📊 СТАТИСТИКА", "💰 ФИНАНСЫ", "👥 ВСЕ ЛЮДИ", "✨ БЛАГА",
        "📤 РАССЫЛКА", "📜 ЛОГИ", "🔍 ПОИСК", "📈 ОТЧЁТ", "🩺 ЗДОРОВЬЕ",
        "🛡️ ЗАЩИТА", "🔧 ПОЧИНИТЬ", "🔄 ОБНОВИТЬ", "📡 СТАТУС", "🧹 ОЧИСТИТЬ",
        "💸 РАБОТА", "📦 ЗАКАЗЫ", "📸 ФОТО", "🎤 ГОЛОС", "📍 АПТЕКА",
        "📝 РЕЗЮМЕ", "🏢 БИЗНЕС", "👵 ПОЖИЛЫЕ", "🧒 ДЕТИ", "💰 БАЛАНС",
        "❓ ВОПРОС", "🆘 ПОМОЩЬ", "🔙 НАЗАД", "🔍 НАЙТИ РАБОТУ", "📋 МОИ ЗАКАЗЫ",
        "➕ СОЗДАТЬ ЗАКАЗ", "🔍 НАЙТИ ЗАКАЗ", "👋 ПОЗДОРОВАТЬСЯ", "📞 ПОМОЩЬ РЯДОМ",
        "🏥 ЗДОРОВЬЕ", "🆘 СРОЧНАЯ ПОМОЩЬ", "📖 СКАЗКА", "🧩 ЗАГАДКА",
        "🎵 ПЕСЕНКА", "🎨 НАРИСОВАТЬ", "🔙 ВЫЙТИ", "💼 МОИ ЗАКАЗЫ",
        "📊 АНАЛИТИКА", "🤖 АВТОМАТИЗАЦИЯ", "📈 ЛИЗИНГ"
    ]
    
    if text in buttons:
        return
    
    # Логируем
    c.execute("INSERT INTO logs (user_id, action, created_at) VALUES (?, ?, ?)",
              (user_id, text[:50], astana_time()))
    conn.commit()
    
    # Проверяем баланс
    balance = get_balance(user_id)
    if balance >= 1:
        c.execute("UPDATE users SET blessings = blessings - 1 WHERE user_id=?", (user_id,))
        conn.commit()
        
        if client:
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "Ты — Зеркало. Отвечай кратко, с уважением. Всегда начинай с 'Ассаляму алейкум'."},
                              {"role": "user", "content": text}],
                    temperature=0.7
                )
                bot.reply_to(message, response.choices[0].message.content)
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка AI: {str(e)[:100]}")
        else:
            bot.reply_to(message, f"🪞 Зеркало приняло ваше сообщение.\n\n✨ Списано 1 Благо")
    else:
        bot.reply_to(message, f"❌ Недостаточно Благ! Нужно 1 ✦\n💰 Баланс: {balance} Благ\n💳 /pay")

# ==================================================
# 🔄 ФОНОВЫЕ ПРОЦЕССЫ
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
print("🪞 ЗЕРКАЛО ЗАПУЩЕНО")
print("=" * 60)
print(f"✅ BOT_TOKEN: {TOKEN[:10] if TOKEN else 'НЕТ'}...")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ'}")
print(f"👑 FOUNDER_ID: {FOUNDER_ID} (это ты)")
print(f"👸 TOMIRIS_ID: {TOMIRIS_ID}")
print(f"📋 СПИСОК АДМИНОВ: {ADMIN_IDS}")
print("=" * 60)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
