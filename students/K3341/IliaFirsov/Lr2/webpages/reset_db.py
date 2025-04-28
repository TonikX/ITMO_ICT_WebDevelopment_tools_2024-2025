import sqlite3
import os

DB_PATH = "parsed_data.db"

def reset_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Database {DB_PATH} deleted.")
    else:
        print(f"No database file found: {DB_PATH}")

if __name__ == "__main__":
    reset_database()
