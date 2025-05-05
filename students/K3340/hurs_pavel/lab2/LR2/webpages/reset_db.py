import sqlite3
import os
import time

DB_PATH = "parsed_data.db"
WAL_PATH = "parsed_data.db-wal"
SHM_PATH = "parsed_data.db-shm"

def reset_database():
    # Удаляем все файлы, связанные с базой данных
    for file_path in [DB_PATH, WAL_PATH, SHM_PATH]:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except PermissionError:
                time.sleep(0.1)  # Небольшая задержка
                os.remove(file_path)
    
    # Создаем новую базу данных
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.close()
    print(f"Database {DB_PATH} reset successfully.")

if __name__ == "__main__":
    reset_database()
