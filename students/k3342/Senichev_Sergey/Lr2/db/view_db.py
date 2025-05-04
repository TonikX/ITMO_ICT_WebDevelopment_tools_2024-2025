import sqlite3
from typing import List, Tuple
import sys
import os

def connect_db() -> sqlite3.Connection:
    """Подключается к базе данных."""
    try:
        # Создаем папку db, если она не существует
        os.makedirs('db', exist_ok=True)
        return sqlite3.connect('db/web_pages.db')
    except sqlite3.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        sys.exit(1)

def get_all_pages(conn: sqlite3.Connection) -> List[Tuple]:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, url, title, content, parsing_method, parsing_time 
        FROM web_pages
    """)
    return cursor.fetchall()

def search_pages(conn: sqlite3.Connection, query: str) -> List[Tuple]:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, url, title, content, parsing_method, parsing_time 
        FROM web_pages 
        WHERE url LIKE ? OR title LIKE ?
    """, (f'%{query}%', f'%{query}%'))
    return cursor.fetchall()

def get_statistics(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            parsing_method,
            COUNT(*) as count,
            AVG(parsing_time) as avg_time,
            MIN(parsing_time) as min_time,
            MAX(parsing_time) as max_time
        FROM web_pages
        WHERE parsing_method IS NOT NULL
        GROUP BY parsing_method
    """)
    return cursor.fetchall()

def print_pages(pages: List[Tuple]):
    """Выводит страницы в удобном формате."""
    if not pages:
        print("Записи не найдены")
        return

    print("\nНайденные страницы:")
    print("-" * 80)
    for page in pages:
        id, url, title, content, method, time = page
        print(f"ID: {id}")
        print(f"URL: {url}")
        print(f"Заголовок: {title}")
        if method:
            print(f"Метод парсинга: {method}")
        if time is not None:
            print(f"Время парсинга: {time:.2f} сек")
        if content:
            print(f"Контент: {content[:100]}...")
        print("-" * 80)

def print_statistics(stats: List[Tuple]):
    """Выводит статистику по методам парсинга."""
    if not stats:
        print("Статистика недоступна")
        return

    print("\nСтатистика по методам парсинга:")
    print("-" * 80)
    for method, count, avg_time, min_time, max_time in stats:
        print(f"Метод: {method}")
        print(f"Количество страниц: {count}")
        print(f"Среднее время: {avg_time:.2f} сек")
        print(f"Минимальное время: {min_time:.2f} сек")
        print(f"Максимальное время: {max_time:.2f} сек")
        print("-" * 80)

def main():
    conn = connect_db()
    
    while True:
        print("\nМеню:")
        print("1. все страницы")
        print("2. статистика по методам парсинга")
        print("3. выход")
        
        choice = input()
        
        if choice == "1":
            pages = get_all_pages(conn)
            print_pages(pages)
        
        elif choice == "2":
            stats = get_statistics(conn)
            print_statistics(stats)
        
        elif choice == "3":
            break
        
        else:
            break

    conn.close()

if __name__ == "__main__":
    main() 