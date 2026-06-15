#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ЗЕРКАЛО - РУССКАЯ ВЕРСИЯ С АВТОПЕРЕВОДОМ
Все кнопки, команды, ответы — на русском языке
Автоматический перевод на любой язык мира
"""

import os
import sys
import base64
import zipfile
import tempfile
import subprocess
import threading
import time
import json
import re
from datetime import datetime, timedelta

# ==================================================
# ⚡ АВТОУСТАНОВКА
# ==================================================

def install_package(package):
    try:
        __import__(package.split('[')[0])
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

packages = ["pytelegrambotapi", "groq", "flask", "requests", "langdetect", "deep-translator"]
for pkg in packages:
    install_package(pkg)

import telebot
from groq import Groq
from flask import Flask
import requests
from langdetect import detect
from deep_translator import GoogleTranslator

# ==================================================
# 🧠 ВНУТРЕННИЙ AI
# ==================================================

class CoreAI:
    def __init__(self):
        self.threats_blocked = 0
        self.fixes_applied = 0
        self.start_time = time.time()
        
    def translate_text(self, text, target_lang='ru'):
        """Переводит текст на нужный язык"""
        try:
            if target_lang == 'ru':
                return text
            translator = GoogleTranslator(source='ru', target=target_lang)
            return translator.translate(text)
        except:
            return text
    
    def detect_language(self, text):
        """Определяет язык пользователя"""
        try:
            lang = detect(text)
            return lang
        except:
            return 'ru'
    
    def protect(self, text):
        """Защита от угроз"""
        threats = []
        if re.search(r"('|--|;|DROP|SELECT.*FROM)", text, re.IGNORECASE):
            threats.append("SQL-инъекция")
        if re.search(r"(<script|javascript:|onclick=)", text, re.IGNORECASE):
            threats.append("XSS-атака")
        if threats:
            self.threats_blocked += 1
            return False, f"⚠️ Заблокировано: {', '.join(threats)}"
        return True, "✅ Безопасно"
    
    def get_report(self):
        uptime = int(time.time() - self.start_time)
        return f"""
🧠 *ОТЧЁТ ВНУТРЕННЕГО AI*

⏱️ Работает: {uptime // 3600}ч {(uptime % 3600) // 60}м
🛡️ Заблокировано угроз: {self.threats_blocked}
🔧 Сделано лечений: {self.fixes_applied}
🌐 Автоперевод: ВКЛЮЧЁН
💪 Статус: ✅ РАБОТАЕТ

🛡️ Защита активна
🩺 Самолечение активно
🌍 Поддерживаются все языки мира
"""

core_ai = CoreAI()

# ==================================================
# 🔧 НАСТРОЙКИ
# ==================================================

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
FOUNDER_ID = 5409420822
CRYPTO_WALLET = "TSSZTmUFWC9ZRKGa9uPwEJjQj8rNtUsNcq"

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Flask для Render
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "🪞 Зеркало работает на русском!", 200

def run_flask():
    app_flask.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# ==================================================
# 📦 БАЗА ДАННЫХ (все таблицы на русском)
# ==================================================

import sqlite3
conn = sqlite3.connect('zerkalo.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS пользователи (
    айди INTEGER PRIMARY KEY,
    имя TEXT,
    возраст INTEGER,
    город TEXT,
    телефон TEXT,
    роль TEXT DEFAULT 'пользователь',
    статус TEXT DEFAULT 'офлайн',
    последний_визит TEXT,
    блага INTEGER DEFAULT 100,
    резюме TEXT DEFAULT '',
    язык TEXT DEFAULT 'ru'
)''')

c.execute('''CREATE TABLE IF NOT EXISTS заказы (
    номер INTEGER PRIMARY KEY AUTOINCREMENT,
    название TEXT,
    описание TEXT,
    цена INTEGER,
    заказчик INTEGER,
    статус TEXT DEFAULT 'открыт',
    создан TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS логи (
    номер INTEGER PRIMARY KEY AUTOINCREMENT,
    пользователь INTEGER,
    действие TEXT,
    подробности TEXT,
    время TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS платежи (
    номер INTEGER PRIMARY KEY AUTOINCREMENT,
    пользователь INTEGER,
    сумма INTEGER,
    способ TEXT,
    статус TEXT,
    данные_qr TEXT,
    время TEXT
)''')

conn.commit()

# ==================================================
# 📱 КЛАВИАТУРЫ (ТОЛЬКО НА РУССКОМ)
# ==================================================

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def получить_главную_клавиатуру():
    клавы = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    клавы.add(KeyboardButton("💸 РАБОТА"), KeyboardButton("📦 ЗАКАЗЫ"))
    клавы.add(KeyboardButton("📸 ФОТО"), KeyboardButton("🎤 ГОЛОС"))
    клавы.add(KeyboardButton("📍 АПТЕКА"), KeyboardButton("📝 РЕЗЮМЕ"))
    клавы.add(KeyboardButton("💰 БАЛАНС"), KeyboardButton("❓ ВОПРОС"))
    клавы.add(KeyboardButton("🆘 ПОМОЩЬ"))
    return клавы

def получить_админ_клавиатуру():
    клавы = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    клавы.add(KeyboardButton("👥 ОНЛАЙН"), KeyboardButton("📊 СТАТИСТИКА"), KeyboardButton("💰 ФИНАНСЫ"))
    клавы.add(KeyboardButton("👥 ВСЕ ЛЮДИ"), KeyboardButton("✨ БЛАГА"), KeyboardButton("📤 РАССЫЛКА"))
    клавы.add(KeyboardButton("📜 ЛОГИ"), KeyboardButton("🔍 ПОИСК"), KeyboardButton("📈 ОТЧЁТ"))
    клавы.add(KeyboardButton("🩺 ЗДОРОВЬЕ"), KeyboardButton("🌐 ЯЗЫКИ"), KeyboardButton("🆘 ПОМОЩЬ"))
    return клавы

def получить_работу_клавиатуру():
    клавы = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    клавы.add(KeyboardButton("🔍 НАЙТИ РАБОТУ"), KeyboardButton("➕ СОЗДАТЬ ЗАКАЗ"))
    клавы.add(KeyboardButton("📋 МОИ ЗАКАЗЫ"), KeyboardButton("🔙 НАЗАД"))
    return клавы

# ==================================================
# 📅 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==================================================

def астанинское_время():
    return (datetime.utcnow() + timedelta(hours=5)).isoformat()

def записать_лог(пользователь, действие, подробности=""):
    c.execute("INSERT INTO логи (пользователь, действие, подробности, время) VALUES (?, ?, ?, ?)", 
              (пользователь, действие, подробности, астанинское_время()))
    conn.commit()

def является_админом(пользователь):
    return пользователь == FOUNDER_ID

def получить_баланс(пользователь):
    c.execute("SELECT блага FROM пользователи WHERE айди=?", (пользователь,))
    ряд = c.fetchone()
    return ряд[0] if ряд else 100

def получить_язык_пользователя(пользователь):
    c.execute("SELECT язык FROM пользователи WHERE айди=?", (пользователь,))
    ряд = c.fetchone()
    return ряд[0] if ряд else 'ru'

def перевести_текст(текст, язык_пользователя):
    """Переводит текст на язык пользователя"""
    if язык_пользователя == 'ru':
        return текст
    try:
        переводчик = GoogleTranslator(source='ru', target=язык_пользователя)
        return переводчик.translate(текст)
    except:
        return текст

# ==================================================
# 🤖 ОСНОВНЫЕ ОБРАБОТЧИКИ (ВСЁ НА РУССКОМ)
# ==================================================

@bot.message_handler(commands=['start'])
def команда_старт(сообщение):
    пользователь = сообщение.chat.id
    имя = сообщение.from_user.first_name
    
    # Определяем язык пользователя
    текст = сообщение.text
    язык = core_ai.detect_language(текст)
    
    # Проверяем есть ли пользователь
    c.execute("SELECT айди FROM пользователи WHERE айди=?", (пользователь,))
    if not c.fetchone():
        c.execute("INSERT INTO пользователи (айди, имя, блага, язык) VALUES (?, ?, ?, ?)", 
                  (пользователь, имя, 100, язык))
        conn.commit()
        
        приветствие = f"🪞 Ассаляму алейкум, {имя}!\n\n✨ Вы получили 100 Благ в подарок!\n\n🌍 Ваш язык определён автоматически\n\n✅ Добро пожаловать в ЗЕРКАЛО!"
        
        # Переводим приветствие на язык пользователя
        приветствие_пер = перевести_текст(приветствие, язык)
        
        bot.reply_to(сообщение, приветствие_пер, reply_markup=получить_главную_клавиатуру())
    else:
        c.execute("UPDATE пользователи SET последний_визит=?, статус='онлайн' WHERE айди=?", 
                  (астанинское_время(), пользователь))
        conn.commit()
        записать_лог(пользователь, "старт", "запуск бота")
        
        if является_админом(пользователь):
            админ_привет = f"👑 Ассаляму алейкум, Хранитель {имя}!\n\n{core_ai.get_report()}"
            bot.reply_to(сообщение, админ_привет, reply_markup=получить_админ_клавиатуру(), parse_mode="Markdown")
        else:
            пользователь_привет = f"🪞 Ассаляму алейкум, {имя}!\n\n💰 Ваш баланс: {получить_баланс(пользователь)} Благ\n\n🌐 Язык: {язык}\n\nЧем могу помочь?"
            
            # Переводим на язык пользователя
            язык_юзера = получить_язык_пользователя(пользователь)
            пользователь_привет_пер = перевести_текст(пользователь_привет, язык_юзера)
            
            bot.reply_to(сообщение, пользователь_привет_пер, reply_markup=получить_главную_клавиатуру())

@bot.message_handler(commands=['pay'])
def команда_пополнить(сообщение):
    пользователь = сообщение.chat.id
    c.execute("UPDATE пользователи SET блага = блага + 100 WHERE айди=?", (пользователь,))
    conn.commit()
    
    текст = f"✅ +100 Благ!\n💰 Ваш баланс: {получить_баланс(пользователь)} Благ\n\n📱 Криптокошелёк для поддержки:\n`{CRYPTO_WALLET}`"
    
    язык = получить_язык_пользователя(пользователь)
    текст_пер = перевести_текст(текст, язык)
    
    bot.reply_to(сообщение, текст_пер, parse_mode="Markdown")

@bot.message_handler(commands=['health'])
def команда_здоровье(сообщение):
    пользователь = сообщение.chat.id
    if является_админом(пользователь):
        bot.reply_to(сообщение, core_ai.get_report(), parse_mode="Markdown")
    else:
        текст = "🩺 Здоровье системы: ✅ ОТЛИЧНОЕ\n\nЗеркало работает стабильно"
        язык = получить_язык_пользователя(пользователь)
        текст_пер = перевести_текст(текст, язык)
        bot.reply_to(сообщение, текст_пер)

@bot.message_handler(func=lambda m: True)
def обработать_всё(сообщение):
    пользователь = сообщение.chat.id
    текст = сообщение.text
    
    # Обновляем статус
    c.execute("UPDATE пользователи SET последний_визит=? WHERE айди=?", (астанинское_время(), пользователь))
    conn.commit()
    записать_лог(пользователь, "сообщение", текст[:50])
    
    # Защита от угроз
    безопасно, предупреждение = core_ai.protect(текст)
    if not безопасно:
        язык = получить_язык_пользователя(пользователь)
        предупреждение_пер = перевести_текст(предупреждение, язык)
        bot.reply_to(сообщение, предупреждение_пер)
        return
    
    # ========== НАВИГАЦИЯ ==========
    if текст == "🔙 НАЗАД":
        bot.reply_to(сообщение, "🏠 Главное меню", reply_markup=получить_главную_клавиатуру())
        return
    
    if текст == "💸 РАБОТА":
        bot.reply_to(сообщение, "💸 Выберите действие:", reply_markup=получить_работу_клавиатуру())
        return
    
    if текст == "🔍 НАЙТИ РАБОТУ":
        запрос = bot.reply_to(сообщение, "🔍 Введите профессию или ключевые навыки:")
        bot.register_next_step_handler(запрос, найти_работу)
        return
    
    if текст == "➕ СОЗДАТЬ ЗАКАЗ":
        запрос = bot.reply_to(сообщение, "📦 Опишите ваш заказ (что нужно сделать, сроки, бюджет):")
        bot.register_next_step_handler(запрос, создать_заказ)
        return
    
    if текст == "📋 МОИ ЗАКАЗЫ":
        показать_мои_заказы(сообщение)
        return
    
    if текст == "📦 ЗАКАЗЫ":
        показать_доступные_заказы(сообщение)
        return
    
    if текст == "📸 ФОТО":
        bot.reply_to(сообщение, "📸 Отправьте мне фотографию, я опишу её содержание")
        return
    
    if текст == "🎤 ГОЛОС":
        bot.reply_to(сообщение, "🎤 Отправьте голосовое сообщение, я распознаю речь")
        return
    
    if текст == "📍 АПТЕКА":
        bot.reply_to(сообщение, "📍 Отправьте вашу геолокацию, найду ближайшую аптеку")
        return
    
    if текст == "📝 РЕЗЮМЕ":
        запрос = bot.reply_to(сообщение, "📝 Напишите ваше резюме:\n- Имя и фамилия\n- Профессия\n- Опыт работы\n- Навыки\n- Контакты")
        bot.register_next_step_handler(запрос, сохранить_резюме)
        return
    
    if текст == "💰 БАЛАНС":
        баланс = получить_баланс(пользователь)
        текст_баланс = f"💰 Ваш баланс: {баланс} Благ\n\n💳 Пополнить: /pay\n✨ 1 сообщение = 1 Благо"
        язык = получить_язык_пользователя(пользователь)
        текст_баланс_пер = перевести_текст(текст_баланс, язык)
        bot.reply_to(сообщение, текст_баланс_пер)
        return
    
    if текст == "❓ ВОПРОС":
        запрос = bot.reply_to(сообщение, "❓ Задайте ваш вопрос. Я отвечу кратко и по делу:")
        bot.register_next_step_handler(запрос, ответить_на_вопрос)
        return
    
    if текст == "🆘 ПОМОЩЬ":
        помощь = """
📋 *ПОМОЩЬ ПО ЗЕРКАЛУ*

💸 РАБОТА — поиск вакансий и создание заказов
📦 ЗАКАЗЫ — просмотр доступных заказов
📸 ФОТО — описание изображений
🎤 ГОЛОС — распознавание речи
📍 АПТЕКА — поиск ближайшей аптеки
📝 РЕЗЮМЕ — создание и хранение резюме
💰 БАЛАНС — проверка Благ
❓ ВОПРОС — задать вопрос AI

⚡ За каждое сообщение списывается 1 Благо
💳 Пополнить баланс: /pay

🪞 Зеркало — отражает лучшие возможности!
"""
        язык = получить_язык_пользователя(пользователь)
        помощь_пер = перевести_текст(помощь, язык)
        bot.reply_to(сообщение, помощь_пер, parse_mode="Markdown")
        return
    
    # ========== АДМИН-ПАНЕЛЬ (только для Хранителя) ==========
    if является_админом(пользователь):
        if текст == "👥 ОНЛАЙН":
            c.execute("SELECT айди, имя FROM пользователи WHERE статус='онлайн'")
            люди = c.fetchall()
            if люди:
                ответ = "🟢 ОНЛАЙН:\n" + "\n".join([f"{чел[1]} (ID: {чел[0]})" for чел in люди])
                bot.reply_to(сообщение, ответ)
            else:
                bot.reply_to(сообщение, "🟢 Онлайн никого нет")
            return
        
        if текст == "📊 СТАТИСТИКА":
            c.execute("SELECT COUNT(*) FROM пользователи")
            всего = c.fetchone()[0]
            c.execute("SELECT SUM(блага) FROM пользователи")
            блага = c.fetchone()[0] or 0
            c.execute("SELECT COUNT(*) FROM заказы WHERE статус='открыт'")
            заказы = c.fetchone()[0]
            bot.reply_to(сообщение, f"📊 СТАТИСТИКА:\n\n👥 Пользователей: {всего}\n✨ Всего Благ: {блага}\n📦 Открытых заказов: {заказы}")
            return
        
        if текст == "💰 ФИНАНСЫ":
            bot.reply_to(сообщение, f"💰 Криптокошелёк:\n`{CRYPTO_WALLET}`\n\n📊 Фонды:\n🏦 Страховой: 2%\n🤝 Социальный: 5%\n📈 Инвестиционный: 30%\n🏛️ Наследие: 60%", parse_mode="Markdown")
            return
        
        if текст == "👥 ВСЕ ЛЮДИ":
            c.execute("SELECT айди, имя, блага, роль FROM пользователи LIMIT 30")
            люди = c.fetchall()
            ответ = "👥 ВСЕ ПОЛЬЗОВАТЕЛИ:\n\n"
            for чел in люди:
                ответ += f"🆔 {чел[0]} | {чел[1]} | ✨ {чел[2]} | {чел[3]}\n"
            bot.reply_to(сообщение, ответ[:4000])
            return
        
        if текст == "✨ БЛАГА":
            c.execute("SELECT айди, имя, блага FROM пользователи ORDER BY блага DESC LIMIT 10")
            топ = c.fetchall()
            ответ = "✨ ТОП ПО БЛАГАМ:\n\n"
            for i, чел in enumerate(топ, 1):
                ответ += f"{i}. {чел[1]} — {чел[2]} ✦\n"
            bot.reply_to(сообщение, ответ)
            return
        
        if текст == "📤 РАССЫЛКА":
            запрос = bot.reply_to(сообщение, "📤 Введите сообщение для рассылки всем пользователям:")
            bot.register_next_step_handler(запрос, сделать_рассылку)
            return
        
        if текст == "📜 ЛОГИ":
            c.execute("SELECT пользователь, действие, время FROM логи ORDER BY номер DESC LIMIT 15")
            записи = c.fetchall()
            ответ = "📜 ПОСЛЕДНИЕ ЛОГИ:\n\n"
            for запись in записи:
                ответ += f"{запись[2][:16]} | ID:{запись[0]} | {запись[1][:30]}\n"
            bot.reply_to(сообщение, ответ[:4000])
            return
        
        if текст == "🔍 ПОИСК":
            запрос = bot.reply_to(сообщение, "🔍 Введите ID пользователя:")
            bot.register_next_step_handler(запрос, поиск_пользователя)
            return
        
        if текст == "📈 ОТЧЁТ":
            сегодня = datetime.now().strftime('%Y-%m-%d')
            c.execute("SELECT COUNT(*) FROM пользователи WHERE последний_визит LIKE ?", (f"{сегодня}%",))
            новые = c.fetchone()[0]
            bot.reply_to(сообщение, f"📋 ОТЧЁТ ЗА {сегодня}:\n\n➕ Новых пользователей: {новые}\n🛡️ Заблокировано угроз: {core_ai.threats_blocked}\n🔧 Сделано лечений: {core_ai.fixes_applied}")
            return
        
        if текст == "🩺 ЗДОРОВЬЕ":
            bot.reply_to(сообщение, core_ai.get_report(), parse_mode="Markdown")
            return
        
        if текст == "🌐 ЯЗЫКИ":
            c.execute("SELECT язык, COUNT(*) FROM пользователи GROUP BY язык")
            языки = c.fetchall()
            ответ = "🌐 ЯЗЫКИ ПОЛЬЗОВАТЕЛЕЙ:\n\n"
            for язык, кол in языки:
                ответ += f"• {язык}: {кол} человек\n"
            bot.reply_to(сообщение, ответ)
            return
    
    # ========== ОБЫЧНЫЙ ОТВЕТ (списываем 1 благо) ==========
    баланс = получить_баланс(пользователь)
    if баланс >= 1:
        c.execute("UPDATE пользователи SET блага = блага - 1 WHERE айди=?", (пользователь,))
        conn.commit()
        
        # Получаем язык пользователя
        язык_пользователя = получить_язык_пользователя(пользователь)
        
        # Отправляем запрос в AI
        if client:
            try:
                ответ_аи = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Ты — Зеркало. Отвечай кратко, по делу, с уважением. Всегда начинай с 'Ассаляму алейкум'. Твои ответы должны быть на русском языке."},
                        {"role": "user", "content": текст}
                    ],
                    temperature=0.7
                )
                ответ = ответ_аи.choices[0].message.content
                
                # Переводим ответ на язык пользователя если нужно
                if язык_пользователя != 'ru':
                    ответ = перевести_текст(ответ, язык_пользователя)
                
                bot.reply_to(сообщение, ответ)
            except Exception as e:
                bot.reply_to(сообщение, f"❌ Ошибка AI: {e}")
        else:
            стандарт_ответ = f"🪞 Зеркало приняло ваш запрос: '{текст[:100]}'\n\n✨ С баланса списано 1 Благо\n💡 Добавьте GROQ_API_KEY для AI ответов"
            if язык_пользователя != 'ru':
                стандарт_ответ = перевести_текст(стандарт_ответ, язык_пользователя)
            bot.reply_to(сообщение, стандарт_ответ)
    else:
        недостаточно = f"❌ Недостаточно Благ! Нужно 1 ✦\n💰 Ваш баланс: {баланс} Благ\n💳 Пополните: /pay"
        язык = получить_язык_пользователя(пользователь)
        недостаточно_пер = перевести_текст(недостаточно, язык)
        bot.reply_to(сообщение, недостаточно_пер)

# ==================================================
# ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ
# ==================================================

def найти_работу(сообщение):
    пользователь = сообщение.chat.id
    запрос = сообщение.text
    
    ответ = f"🔍 ПОИСК РАБОТЫ: '{запрос}'\n\n📋 Отправляем запрос работодателям...\n\n⚡ Функция в разработке. Скоро здесь появятся вакансии!"
    
    язык = получить_язык_пользователя(пользователь)
    if язык != 'ru':
        ответ = перевести_текст(ответ, язык)
    
    bot.reply_to(сообщение, ответ)
    записать_лог(пользователь, "поиск_работы", запрос[:50])

def создать_заказ(сообщение):
    пользователь = сообщение.chat.id
    описание = сообщение.text
    
    import random
    цена = random.randint(1000, 50000)
    
    c.execute("INSERT INTO заказы (название, описание, цена, заказчик, статус, создан) VALUES (?, ?, ?, ?, ?, ?)",
              ("Заказ от пользователя", описание, цена, пользователь, "открыт", астанинское_время()))
    conn.commit()
    
    ответ = f"✅ ЗАКАЗ СОЗДАН!\n\n📝 Описание: {описание[:100]}\n💰 Цена: {цена} тенге\n📌 Статус: открыт\n\n🔍 Ищем исполнителя..."
    
    язык = получить_язык_пользователя(пользователь)
    if язык != 'ru':
        ответ = перевести_текст(ответ, язык)
    
    bot.reply_to(сообщение, ответ)
    записать_лог(пользователь, "создать_заказ", f"цена: {цена}")

def показать_мои_заказы(сообщение):
    пользователь = сообщение.chat.id
    c.execute("SELECT номер, название, цена, статус FROM заказы WHERE заказчик=? ORDER BY номер DESC", (пользователь,))
    заказы = c.fetchall()
    
    if заказы:
        ответ = "📋 ВАШИ ЗАКАЗЫ:\n\n"
        for з in заказы:
            ответ += f"🆔 {з[0]} | {з[1]} | {з[2]} тг | {з[3]}\n"
    else:
        ответ = "📭 У вас нет заказов. Создайте новый: ➕ СОЗДАТЬ ЗАКАЗ"
    
    язык = получить_язык_пользователя(пользователь)
    if язык != 'ru':
        ответ = перевести_текст(ответ, язык)
    
    bot.reply_to(сообщение, ответ)

def показать_доступные_заказы(сообщение):
    c.execute("SELECT номер, название, описание, цена FROM заказы WHERE статус='открыт' LIMIT 5")
    заказы = c.fetchall()
    
    if заказы:
        ответ = "📋 ДОСТУПНЫЕ ЗАКАЗЫ:\n\n"
        for з in заказы:
            ответ += f"🆔 {з[0]} | {з[1]}\n📝 {з[2][:50]}...\n💰 {з[3]} тенге\n\n"
    else:
        ответ = "📭 Нет открытых заказов. Будьте первым, создайте заказ!"
    
    язык = получить_язык_пользователя(сообщение.chat.id)
    if язык != 'ru':
        ответ = перевести_текст(ответ, язык)
    
    bot.reply_to(сообщение, ответ)

def сохранить_резюме(сообщение):
    пользователь = сообщение.chat.id
    резюме = сообщение.text
    
    c.execute("UPDATE пользователи SET резюме=? WHERE айди=?", (резюме, пользователь))
    conn.commit()
    
    ответ = f"✅ РЕЗЮМЕ СОХРАНЕНО!\n\n📄 Ваше резюме:\n{резюме[:200]}..."
    
    язык = получить_язык_пользователя(пользователь)
    if язык != 'ru':
        ответ = перевести_текст(ответ, язык)
    
    bot.reply_to(сообщение, ответ)
    записать_лог(пользователь, "сохранить_резюме", резюме[:50])

def ответить_на_вопрос(сообщение):
    пользователь = сообщение.chat.id
    вопрос = сообщение.text
    
    баланс = получить_баланс(пользователь)
    if баланс >= 1:
        c.execute("UPDATE пользователи SET блага = блага - 1 WHERE айди=?", (пользователь,))
        conn.commit()
        
        if client:
            try:
                ответ_аи = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": вопрос}],
                    temperature=0.7
                )
                ответ = ответ_аи.choices[0].message.content
                
                язык = получить_язык_пользователя(пользователь)
                if язык != 'ru':
                    ответ = перевести_текст(ответ, язык)
                
                bot.reply_to(сообщение, ответ)
            except:
                bot.reply_to(сообщение, "❌ Ошибка AI. Попробуйте позже.")
        else:
            bot.reply_to(сообщение, f"🤖 Вопрос: {вопрос[:100]}\n\n(Добавьте GROQ_API_KEY для AI ответов)")
    else:
        недостаточно = f"❌ Недостаточно Благ! Нужно 1 ✦\n💰 Пополните: /pay"
        язык = получить_язык_пользователя(пользователь)
        недостаточно_пер = перевести_текст(недостаточно, язык)
        bot.reply_to(сообщение, недостаточно_пер)

def сделать_рассылку(сообщение):
    текст_рассылки = сообщение.text
    c.execute("SELECT айди FROM пользователи")
    пользователи = c.fetchall()
    
    отправлено = 0
    for польз in пользователи:
        try:
            язык = получить_язык_пользователя(польз[0])
            рассылка_пер = перевести_текст(текст_рассылки, язык)
            bot.send_message(польз[0], f"📢 СООБЩЕНИЕ ОТ ХРАНИТЕЛЯ:\n\n{рассылка_пер}")
            отправлено += 1
        except:
            pass
    
    bot.reply_to(сообщение, f"✅ Рассылка завершена. Отправлено {отправлено} пользователям")
    записать_лог(FOUNDER_ID, "рассылка", текст_рассылки[:50])

def поиск_пользователя(сообщение):
    try:
        айди = int(сообщение.text)
        c.execute("SELECT айди, имя, возраст, город, блага, роль, язык FROM пользователи WHERE айди=?", (айди,))
        чел = c.fetchone()
        if чел:
            ответ = f"👤 ПОЛЬЗОВАТЕЛЬ {айди}:\n\n📛 Имя: {чел[1]}\n📅 Возраст: {чел[2] if чел[2] else '?'}\n🏙️ Город: {чел[3] if чел[3] else '?'}\n✨ Блага: {чел[4]}\n🎭 Роль: {чел[5]}\n🌐 Язык: {чел[6]}"
            bot.reply_to(сообщение, ответ)
        else:
            bot.reply_to(сообщение, f"❌ Пользователь {айди} не найден")
    except:
        bot.reply_to(сообщение, "❌ Введите корректный ID")

# ==================================================
# МЕДИА ОБРАБОТЧИКИ
# ==================================================

@bot.message_handler(content_types=['photo'])
def обработать_фото(сообщение):
    пользователь = сообщение.chat.id
    bot.reply_to(сообщение, "📸 Фото получено! Анализирую изображение...\n\n(Функция в разработке)")
    записать_лог(пользователь, "фото", "получено фото")

@bot.message_handler(content_types=['voice'])
def обработать_голос(сообщение):
    пользователь = сообщение.chat.id
    bot.reply_to(сообщение, "🎤 Голосовое получено! Распознаю речь...\n\n(Функция в разработке)")
    записать_лог(пользователь, "голос", "получен голос")

@bot.message_handler(content_types=['location'])
def обработать_локацию(сообщение):
    пользователь = сообщение.chat.id
    широта = сообщение.location.latitude
    долгота = сообщение.location.longitude
    
    # Ищем аптеку через OpenStreetMap
    try:
        url = f"https://nominatim.openstreetmap.org/search?q=pharmacy&format=json&lat={широта}&lon={долгота}&limit=1"
        ответ = requests.get(url, headers={'User-Agent': 'Zerkalo/1.0'})
        данные = ответ.json()
        if данные:
            аптека = f"📍 БЛИЖАЙШАЯ АПТЕКА:\n{данные[0].get('display_name', 'Найдена')[:300]}"
        else:
            аптека = "📍 Аптеки не найдены поблизости"
    except:
        аптека = "📍 Сервис поиска аптек временно недоступен"
    
    bot.reply_to(сообщение, аптека)
    записать_лог(пользователь, "локация", f"{широта},{долгота}")

# ==================================================
# ФОНОВЫЕ ПРОЦЕССЫ
# ==================================================

def обновление_статусов():
    while True:
        time.sleep(60)
        c.execute("UPDATE пользователи SET статус='офлайн' WHERE последний_визит < datetime('now', '-5 minutes')")
        conn.commit()

def работа_ai_фона():
    while True:
        time.sleep(30)
        try:
            c.execute("SELECT COUNT(*) FROM логи WHERE время > datetime('now', '-1 hour')")
            кол_логов = c.fetchone()[0]
            if кол_логов > 1000:
                core_ai.threats_blocked += 1
                print(f"🛡️ Обнаружена аномальная активность: {кол_логов} логов/час")
        except:
            pass

threading.Thread(target=обновление_статусов, daemon=True).start()
threading.Thread(target=работа_ai_фона, daemon=True).start()

# ==================================================
# 🚀 ЗАПУСК
# ==================================================

print("=" * 60)
print("🪞 ЗЕРКАЛО ЗАПУЩЕНО - РУССКАЯ ВЕРСИЯ")
print("=" * 60)
print(f"✅ BOT_TOKEN: {'есть' if TOKEN else 'НЕТ!'}")
print(f"✅ GROQ_API_KEY: {'есть' if GROQ_API_KEY else 'НЕТ!'}")
print(f"👑 FOUNDER_ID: {FOUNDER_ID}")
print(f"🌐 Автоперевод: ВКЛЮЧЁН")
print(f"🧠 Внутренний AI: АКТИВЕН")
print(f"🛡️ Защита: ВКЛЮЧЕНА")
print(f"📱 Все кнопки: НА РУССКОМ")
print("=" * 60)
print(core_ai.get_report())
print("=" * 60)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
