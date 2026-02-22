# db.py

import sqlite3

def init_db():
    conn = sqlite3.connect("ZAVot.db")
    c = conn.cursor()

    # таблицы
    c.execute("""CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      code TEXT UNIQUE, role TEXT, password TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS protocols (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      num INT, file_name TEXT,
      date_start TEXT, date_end TEXT,
      status TEXT, vote_type TEXT, folder TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS questions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      protocol_id INT, qnum INT,
      opt1 TEXT, opt2 TEXT, opt3 TEXT,
      default_vote TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS votes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      protocol_id INT, user_code TEXT,
      question_id INT, vote TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      participant_code TEXT, action TEXT, created_at TEXT
    )""")

    # ✅ если таблица questions уже существовала без default_vote — добавить
    cols = [row[1] for row in c.execute("PRAGMA table_info(questions)").fetchall()]
    if "default_vote" not in cols:
        c.execute("ALTER TABLE questions ADD COLUMN default_vote TEXT")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()