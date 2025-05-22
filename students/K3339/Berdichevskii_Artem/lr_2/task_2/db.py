import sqlite3

def init_db():
    conn = sqlite3.connect("pages.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            title TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(url, title):
    conn = sqlite3.connect("pages.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pages (url, title) VALUES (?, ?)", (url, title))
    conn.commit()
    conn.close()
