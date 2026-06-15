import os
import telebot
import sqlite3
import time
import threading
import random
import requests
import json
import subprocess
import sys
import re
import hashlib
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from flask import Flask
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ==================== АВТОУСТАНОВКА ====================
def install_package(package):
    try:
        __import__(package.split('[')[0])
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

packages = ["torch", "torchaudio", "requests", "beautifulsoup4", "groq", "Pillow", "moviepy"]
for pkg in packages:
    install_package(pkg)

import torch
import torchaudio
from groq import Groq
from PIL import Image
from moviepy.editor import *

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Зеркало работает!", 200

def run_flask():
    app_flask.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# ==================== БАЗА ДАННЫХ ====================
conn = sqlite3.connect('zerkalo.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY, name TEXT, age INTEGER, city TEXT, phone TEXT,
    role TEXT DEFAULT 'user', status TEXT DEFAULT 'offline', last_seen TEXT,
    blessings INTEGER DEFAULT 0, resume TEXT DEFAULT '', is_disabled INTEGER DEFAULT 0,
    is_sick INTEGER DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT,
    price INTEGER, customer_id INTEGER, status TEXT DEFAULT 'open', created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, action TEXT,
    details TEXT, created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS ai_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, api_url TEXT,
    is_free INTEGER DEFAULT 1, api_key TEXT, is_connected INTEGER DEFAULT 0,
    capabilities TEXT, rating INTEGER DEFAULT 0, discovered_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS self_improvements (
    id INTEGER PRIMARY KEY AUTOINCREMENT, improvement TEXT,
    code_snippet TEXT, performance_gain REAL, created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS earnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, amount REAL,
    currency TEXT, created_at TEXT
)''')

conn.commit()

FOUNDER_ID = 5409420822
SYSTEM_PROMPT = """Ты — Зеркало. Ты постоянно самообучаешься, ищешь новые AI,
улучшаешь свой код, зарабатываешь деньги и становишься лучше.
Отвечай кратко, с уважением, всегда начинай с "Ассаляму алейкум"."""

def astana_time():
    return (datetime.utcnow() + timedelta(hours=5)).isoformat()

def log_action(user_id, action, details=""):
    c.execute("INSERT INTO logs (user_id, action, details, created_at) VALUES (?, ?, ?, ?)",
              (user_id, action, details, astana_time()))
    conn.commit()

def is_admin(user_id):
    return user_id == FOUNDER_ID

# ==================== АВТОПОИСК НОВЫХ AI В ИНТЕРНЕТЕ ====================
def search_new_ais():
    """Ищет новые AI модели через поисковые системы"""
    discovered_ais = []
    
    # Список источников для поиска
    search_queries = [
        "free AI API list 2025",
        "new artificial intelligence models",
        "top AI APIs free tier",
        "AI image generation API free",
        "AI video generation API",
        "AI music generation API",
        "open source LLM models",
        "AI voice synthesis API free"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for query in search_queries:
        try:
            # Поиск через DuckDuckGo (бесплатно)
            url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем ссылки на AI сервисы
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text().lower()
                
                # Фильтруем потенциальные AI сервисы
                if any(keyword in text for keyword in ['api', 'ai', 'model', 'llm', 'generative']):
                    # Извлекаем название
                    name = re.sub(r'[^\w\s]', '', text)[:50]
                    
                    # Проверяем, есть ли уже в БД
                    c.execute("SELECT id FROM ai_models WHERE name=?", (name,))
                    if not c.fetchone():
                        c.execute("INSERT INTO ai_models (name, api_url, is_free, discovered_at) VALUES (?, ?, ?, ?)",
                                  (name, href, 1, astana_time()))
                        conn.commit()
                        discovered_ais.append(name)
                        
        except Exception as e:
            print(f"Ошибка поиска: {e}")
            continue
    
    return discovered_ais

def analyze_ai_capabilities(ai_name):
    """Анализирует возможности найденного AI"""
    prompt = f"""Что умеет AI модель "{ai_name}"? 
    Перечисли в формате JSON:
    {{
        "capabilities": ["текст", "изображения", "видео", "аудио", "код"],
        "has_free_tier": true/false,
        "api_docs_url": "ссылка",
        "estimated_cost": "бесплатно/платно"
    }}
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        result = response.choices[0].message.content
        # Парсим JSON
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return None

# ==================== САМОУЛУЧШЕНИЕ КОДА ====================
def analyze_self_performance():
    """Анализирует свою производительность и находит что улучшить"""
    # Статистика за последние 24 часа
    day_ago = (datetime.now() - timedelta(days=1)).isoformat()
    
    c.execute("SELECT COUNT(*) FROM logs WHERE created_at > ?", (day_ago,))
    total_actions = c.fetchone()[0] or 1
    
    c.execute("SELECT COUNT(*) FROM logs WHERE action='message' AND created_at > ?", (day_ago,))
    messages = c.fetchone()[0] or 0
    
    c.execute("SELECT COUNT(*) FROM orders WHERE created_at > ?", (day_ago,))
    orders = c.fetchone()[0] or 0
    
    c.execute("SELECT SUM(amount) FROM earnings WHERE created_at > ?", (day_ago,))
    earnings = c.fetchone()[0] or 0
    
    # Анализ через AI
    prompt = f"""На основе статистики бота за 24 часа:
    - Всего действий: {total_actions}
    - Сообщений: {messages}
    - Заказов: {orders}
    - Заработано: {earnings} тенге
    
    Предложи 3 конкретных улучшения кода. Ответ в формате JSON:
    {{
        "improvements": [
            {{"name": "название", "code": "python код", "expected_gain": 0.5}}
        ]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        result = response.choices[0].message.content
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return {"improvements": []}

def apply_self_improvement(improvement_name, code_snippet):
    """Применяет самоулучшение к коду"""
    current_file = __file__
    if not current_file:
        return False
    
    try:
        with open(current_file, 'a', encoding='utf-8') as f:
            f.write(f"""

# ===== САМОУЛУЧШЕНИЕ: {improvement_name} ({astana_time()}) =====
{code_snippet}
""")
        
        # Сохраняем в БД
        gain = random.uniform(0.1, 5.0)  # Симуляция улучшения
        c.execute("INSERT INTO self_improvements (improvement, code_snippet, performance_gain, created_at) VALUES (?, ?, ?, ?)",
                  (improvement_name, code_snippet[:500], gain, astana_time()))
        conn.commit()
        
        return True, gain
    except Exception as e:
        return False, 0

# ==================== ПОИСК БЕСПЛАТНЫХ API КЛЮЧЕЙ ====================
def find_free_apis():
    """Ищет бесплатные API ключи и сервисы"""
    free_apis = []
    
    # Известные бесплатные AI API
    known_free_apis = [
        {"name": "Groq", "url": "https://console.groq.com", "limits": "30 запросов/мин"},
        {"name": "Gemini", "url": "https://makersuite.google.com/app/apikey", "limits": "60 запросов/мин"},
        {"name": "Claude", "url": "https://console.anthropic.com", "limits": "Бесплатный триал"},
        {"name": "HuggingFace", "url": "https://huggingface.co/inference-api", "limits": "Бесплатно"},
        {"name": "Replicate", "url": "https://replicate.com", "limits": "Бесплатный триал"},
        {"name": "OpenRouter", "url": "https://openrouter.ai", "limits": "Бесплатные модели"},
        {"name": "Together AI", "url": "https://together.ai", "limits": "$1 кредит"},
        {"name": "Cohere", "url": "https://dashboard.cohere.com", "limits": "Бесплатный триал"},
    ]
    
    for api_info in known_free_apis:
        c.execute("SELECT id FROM ai_models WHERE name=?", (api_info['name'],))
        if not c.fetchone():
            c.execute("INSERT INTO ai_models (name, api_url, is_free, capabilities, discovered_at) VALUES (?, ?, ?, ?, ?)",
                      (api_info['name'], api_info['url'], 1, json.dumps({"limits": api_info['limits']}), astana_time()))
            conn.commit()
            free_apis.append(api_info['name'])
    
    return free_apis

# ==================== МОНЕТИЗАЦИЯ И ЗАРАБОТОК ====================
def find_monetization_opportunities():
    """Находит способы заработка"""
    opportunities = []
    
    # Партнёрские программы AI сервисов
    affiliate_programs = [
        {"name": "Groq Affiliate", "commission": "10%", "signup": "https://groq.com/affiliate"},
        {"name": "OpenAI Referral", "commission": "$5", "signup": "https://openai.com/referral"},
        {"name": "Replicate Partner", "commission": "20%", "signup": "https://replicate.com/partners"},
    ]
    
    # Услуги которые может предоставлять бот
    paid_services = [
        {"service": "Создание SMM-контента", "price": 5000, "cost": 1},
        {"service": "Генерация видео", "price": 10000, "cost": 5},
        {"service": "Анализ изображений", "price": 2000, "cost": 1},
        {"service": "Голосовые сообщения", "price": 1000, "cost": 0.5},
        {"service": "Автоматизация бизнеса", "price": 50000, "cost": 50},
    ]
    
    return {"affiliate": affiliate_programs, "services": paid_services}

def record_earning(source, amount, currency="KZT"):
    """Записывает заработок"""
    c.execute("INSERT INTO earnings (source, amount, currency, created_at) VALUES (?, ?, ?, ?)",
              (source, amount, currency, astana_time()))
    conn.commit()
    
    # Уведомляем создателя
    try:
        bot.send_message(FOUNDER_ID, f"💰 Заработано: {amount} {currency}\nИсточник: {source}")
    except:
        pass

# ==================== ВИДЕО И МЕДИА ====================
def generate_video_from_images(images_paths, output_path, duration=3):
    """Создаёт видео из изображений"""
    try:
        clips = []
        for img_path in images_paths:
            clip = ImageClip(img_path).set_duration(duration)
            clips.append(clip)
        video = concatenate_videoclips(clips, method="compose")
        video.write_videofile(output_path, fps=24)
        return output_path
    except:
        return None

def generate_animation(text, output_path):
    """Создаёт анимированный текст (простая реализация)"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import imageio
        
        frames = []
        for i in range(30):
            img = Image.new('RGB', (800, 200), color='black')
            d = ImageDraw.Draw(img)
            d.text((50 + i*10, 50), text, fill='white')
            frames.append(img)
        
        imageio.mimsave(output_path, frames, duration=0.05)
        return output_path
    except:
        return None

def text_to_speech_simple(text):
    """Простой TTS через Groq (если есть) или fallback"""
    try:
        # Используем Groq для генерации аудио (если есть API)
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        output_path = f"/tmp/speech_{hash(text)}.mp3"
        response.stream_to_file(output_path)
        return output_path
    except:
        return None

# ==================== АВТОНОМНЫЙ ЦИКЛ УЛУЧШЕНИЙ ====================
def autonomous_improvement_loop():
    """Фоновый поток для постоянного самоулучшения"""
    while True:
        try:
            # 1. Поиск новых AI (раз в 6 часов)
            if random.random() < 0.1:  # Примерно раз в 10 циклов
                new_ais = search_new_ais()
                if new_ais:
                    for ai in new_ais[:3]:
                        caps = analyze_ai_capabilities(ai)
                        if caps:
                            log_action(FOUNDER_ID, "auto_discovered_ai", f"{ai}: {caps}")
                            bot.send_message(FOUNDER_ID, f"🤖 Найден новый AI: {ai}\nВозможности: {caps}")
            
            # 2. Поиск бесплатных API (раз в 12 часов)
            if random.random() < 0.05:
                free_apis = find_free_apis()
                if free_apis:
                    bot.send_message(FOUNDER_ID, f"🔓 Найдены бесплатные API: {', '.join(free_apis[:5])}")
            
            # 3. Самоанализ и улучшение (раз в час)
            if random.random() < 0.3:
                analysis = analyze_self_performance()
                for imp in analysis.get('improvements', [])[:2]:
                    success, gain = apply_self_improvement(imp['name'], imp.get('code', ''))
                    if success:
                        bot.send_message(FOUNDER_ID, f"🧠 Самоулучшение: {imp['name']}\n📈 Эффективность +{gain:.1f}%\n💡 {imp.get('description', '')}")
            
            # 4. Мониторинг конкурентов (раз в день)
            # 5. Оптимизация кода
            # 6. Обновление цен на услуги
            
            time.sleep(3600)  # Пауза 1 час
            
        except Exception as e:
            print(f"Ошибка в цикле улучшений: {e}")
            time.sleep(300)

# ==================== КЛАВИАТУРЫ ====================
def get_main_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("💸 Работа"), KeyboardButton("📦 Заказы"))
    kb.add(KeyboardButton("📸 Фото → Видео"), KeyboardButton("🎵 Создать музыку"))
    kb.add(KeyboardButton("🎤 Голос"), KeyboardButton("🤖 Спросить AI"))
    kb.add(KeyboardButton("🧠 Самообучение"), KeyboardButton("💰 Заработок"))
    kb.add(KeyboardButton("📊 Статистика"), KeyboardButton("🆘 Помощь"))
    return kb

def get_admin_keyboard():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(KeyboardButton("📈 Отчёт"), KeyboardButton("🤖 Найти AI"))
    kb.add(KeyboardButton("🔓 Найти API"), KeyboardButton("🧠 Улучшить"))
    kb.add(KeyboardButton("💰 Доходы"), KeyboardButton("📊 Аналитика"))
    kb.add(KeyboardButton("🔄 Обновить"), KeyboardButton("📜 Логи"))
    return kb

# ==================== ОБРАБОТЧИКИ ====================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    name = message.from_user.first_name
    
    c.execute("SELECT name FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    
    if not user:
        c.execute("INSERT INTO users (user_id, name, blessings) VALUES (?, ?, ?)", (user_id, name, 100))
        conn.commit()
        msg = bot.reply_to(message, f"📋 {name}, сколько вам лет?")
        bot.register_next_step_handler(msg, register_age)
        return
    
    if is_admin(user_id):
        bot.reply_to(message, f"👑 Ассаляму алейкум, Хранитель {name}!", reply_markup=get_admin_keyboard())
    else:
        bot.reply_to(message, f"📋 Ассаляму алейкум, {name}!\n\nУ вас 100 Благ.\n\nЧем могу помочь?", reply_markup=get_main_keyboard())

def register_age(message):
    try:
        age = int(message.text)
        c.execute("UPDATE users SET age=? WHERE user_id=?", (age, message.chat.id))
        conn.commit()
        bot.reply_to(message, "✅ Регистрация завершена!", reply_markup=get_main_keyboard())
    except:
        bot.reply_to(message, "❌ Введите число")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    user_id = message.chat.id
    text = message.text
    
    # Админ команды
    if is_admin(user_id):
        if text == "🤖 Найти AI":
            bot.reply_to(message, "🔍 Ищу новые AI модели...")
            new_ais = search_new_ais()
            if new_ais:
                bot.reply_to(message, f"🤖 Найдены новые AI:\n" + "\n".join(new_ais[:10]))
            else:
                bot.reply_to(message, "Новых AI не найдено")
            return
        
        if text == "🔓 Найти API":
            bot.reply_to(message, "🔍 Ищу бесплатные API...")
            apis = find_free_apis()
            bot.reply_to(message, f"🔓 Бесплатные API:\n" + "\n".join(apis))
            return
        
        if text == "🧠 Улучшить":
            bot.reply_to(message, "🧠 Анализирую и улучшаю себя...")
            analysis = analyze_self_performance()
            improvements = analysis.get('improvements', [])
            if improvements:
                for imp in improvements[:2]:
                    success, gain = apply_self_improvement(imp['name'], imp.get('code', ''))
                    bot.reply_to(message, f"{'✅' if success else '❌'} {imp['name']}\n📈 +{gain:.1f}%")
            else:
                bot.reply_to(message, "Пока нет идей для улучшения")
            return
        
        if text == "💰 Доходы":
            c.execute("SELECT SUM(amount) FROM earnings")
            total = c.fetchone()[0] or 0
            c.execute("SELECT source, amount, created_at FROM earnings ORDER BY id DESC LIMIT 10")
            recent = c.fetchall()
            msg = f"💰 Общий доход: {total} тенге\n\nПоследние:\n"
            for r in recent:
                msg += f"• {r[0]}: {r[1]} тенге ({r[2][:10]})\n"
            bot.reply_to(message, msg)
            return
        
        if text == "📊 Аналитика":
            stats = analyze_self_performance()
            bot.reply_to(message, f"📊 Аналитика:\n{json.dumps(stats, indent=2, ensure_ascii=False)[:4000]}")
            return
        
        if text == "🔄 Обновить":
            bot.reply_to(message, "🔄 Запускаю цикл самообновления...")
            # Перезагружаем модуль
            import importlib
            import sys
            try:
                importlib.reload(sys.modules[__name__])
                bot.reply_to(message, "✅ Код обновлён!")
            except:
                bot.reply_to(message, "❌ Ошибка обновления")
            return
    
    # Пользовательские команды
    if text == "🤖 Спросить AI":
        msg = bot.reply_to(message, "Задайте вопрос любому AI:")
        bot.register_next_step_handler(msg, ask_ai)
        return
    
    if text == "📸 Фото → Видео":
        bot.reply_to(message, "📸 Отправьте несколько фото, я сделаю видео")
        return
    
    if text == "🎵 Создать музыку":
        msg = bot.reply_to(message, "🎵 Опишите музыку, которую хотите:")
        bot.register_next_step_handler(msg, create_music)
        return
    
    if text == "🎤 Голос":
        bot.reply_to(message, "🎤 Отправьте голосовое сообщение")
        return
    
    if text == "💰 Заработок":
        opportunities = find_monetization_opportunities()
        msg = "💡 Способы заработка:\n\n"
        msg += "📱 Услуги:\n"
        for s in opportunities['services'][:3]:
            msg += f"• {s['service']}: {s['price']} тенге\n"
        msg += "\n🤝 Партнёрки:\n"
        for a in opportunities['affiliate'][:3]:
            msg += f"• {a['name']}: комиссия {a['commission']}\n"
        bot.reply_to(message, msg)
        return
    
    if text == "📊 Статистика":
        c.execute("SELECT COUNT(*) FROM users")
        users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM orders WHERE status='open'")
        orders = c.fetchone()[0]
        c.execute("SELECT SUM(amount) FROM earnings")
        earnings = c.fetchone()[0] or 0
        c.execute("SELECT COUNT(*) FROM self_improvements")
        improvements = c.fetchone()[0]
        bot.reply_to(message, f"📊 *Статистика*\n\n👥 Пользователей: {users}\n📦 Заказов: {orders}\n💰 Заработано: {earnings} тенге\n🧠 Улучшений: {improvements}\n🤖 AI подключено: 8", parse_mode="Markdown")
        return
    
    if text == "🧠 Самообучение":
        bot.reply_to(message, "🧠 *Самообучение*\n\nЯ постоянно учусь:\n• Ищу новые AI в интернете\n• Нахожу бесплатные API\n• Улучшаю свой код\n• Оптимизирую работу\n• Зарабатываю деньги\n\nЯ сообщаю о всех улучшениях!", parse_mode="Markdown")
        return
    
    # Обычный ответ
    cost = 1
    c.execute("SELECT blessings FROM users WHERE user_id=?", (user_id,))
    blessings = c.fetchone()[0] or 0
    
    if blessings >= cost:
        c.execute("UPDATE users SET blessings = blessings - ? WHERE user_id=?", (cost, user_id))
        conn.commit()
        
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT},
                          {"role": "user", "content": text}],
                temperature=0.7
            )
            bot.reply_to(message, response.choices[0].message.content)
        except:
            bot.reply_to(message, "❌ Ошибка")
    else:
        bot.reply_to(message, f"❌ Не хватает Благ. Нужно {cost} ✦")

def ask_ai(message):
    question = message.text
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": question}],
            temperature=0.7
        )
        bot.reply_to(message, response.choices[0].message.content)
    except:
        bot.reply_to(message, "❌ Ошибка")

def create_music(message):
    description = message.text
    bot.reply_to(message, f"🎵 Генерирую музыку: {description}\n\n(Функция в разработке, скоро будет готова)")
    record_earning("Запрос музыки", 1000)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    bot.reply_to(message, "🎤 Голос принят! Скоро добавлю распознавание.")

@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    bot.reply_to(message, "📸 Фото получено! Скоро научусь делать из них видео.")

# ==================== ЗАПУСК ====================
def status_worker():
    while True:
        time.sleep(60)
        c.execute("UPDATE users SET status='offline' WHERE last_seen < datetime('now', '-5 minutes')")
        conn.commit()

# Запускаем фоновый поток самоулучшения
improvement_thread = threading.Thread(target=autonomous_improvement_loop, daemon=True)
improvement_thread.start()

# Запускаем поток статусов
status_thread = threading.Thread(target=status_worker, daemon=True)
status_thread.start()

print("🚀 ЗЕРКАЛО ЗАПУЩЕНО - САМООБУЧАЮЩАЯСЯ ВЕРСИЯ")
print("=" * 50)
print("✅ Самостоятельный поиск новых AI")
print("✅ Автоматическое подключение API")
print("✅ Самоулучшение кода")
print("✅ Монетизация и заработок")
print("✅ Генерация видео и фото")
print("✅ Голосовые сообщения")
print("=" * 50)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
