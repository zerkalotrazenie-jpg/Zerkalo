import sqlite3

conn = sqlite3.connect('zerkalo.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    role TEXT DEFAULT 'user',
    balance INTEGER DEFAULT 100,
    is_admin INTEGER DEFAULT 0,
    last_seen TEXT,
    phone TEXT DEFAULT '',
    city TEXT DEFAULT '',
    profession TEXT DEFAULT ''
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    price INTEGER,
    customer_id INTEGER,
    executor_id INTEGER DEFAULT 0,
    status TEXT DEFAULT 'open',
    created_at TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    method TEXT,
    status TEXT DEFAULT 'pending',
    transaction_id TEXT,
    created_at TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    details TEXT,
    created_at TEXT
)
''')

conn.commit()
print("✅ БАЗА ДАННЫХ ГОТОВА")
