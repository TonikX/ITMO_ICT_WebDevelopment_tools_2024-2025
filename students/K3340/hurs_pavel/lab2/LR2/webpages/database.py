import sqlite3


class Database:
    def __init__(self, db_name="parsed_data.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                title TEXT
            )
        ''')
        self.conn.commit()

    def insert_page(self, url: str, title: str):
        self.cursor.execute('''
            INSERT INTO pages (url, title)
            VALUES (?, ?)
        ''', (url, title))
        self.conn.commit()

    def close(self):
        self.conn.close()
