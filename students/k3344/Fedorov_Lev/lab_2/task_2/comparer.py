import subprocess
import sys
import time
import psycopg2
import os
from dotenv import load_dotenv
import warnings
import urllib3

warnings.simplefilter('ignore', urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'hockey_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'tochange'),
}


def clear_database():
    """Очистка таблиц перед каждым парсером"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute('TRUNCATE TABLE tournaments CASCADE')
        cursor.execute('TRUNCATE TABLE teams CASCADE')
        cursor.execute('TRUNCATE TABLE sport_schools CASCADE')
        cursor.execute('TRUNCATE TABLE seasons CASCADE')
        conn.commit()
        cursor.close()
        conn.close()
        print("База данных очищена перед новым запуском")
    except Exception as e:
        print(f"Error cleaning database: {e}")


def get_stats():
    """Получение статистики из БД"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM teams')
        teams_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM sport_schools')
        schools_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM tournaments')
        tournaments_count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return teams_count, schools_count, tournaments_count
    except Exception as e:
        print(f"Error getting stats: {e}")
        return 0, 0, 0


def run_parser(name, filename):
    """Запускает парсер и измеряет время"""
    print(f"\n{'=' * 60}")
    print(f"Запуск {name} парсера...")
    print('=' * 60)

    clear_database()

    start_time = time.time()
    result = subprocess.run([sys.executable, filename], capture_output=True, text=True)
    end_time = time.time()

    print(result.stdout)

    if result.stderr:
        print(f"Ошибки{name}:")
        print(result.stderr)

    teams, schools, tournaments = get_stats()

    execution_time = end_time - start_time
    print(f"\n{name} завершен за {execution_time:.2f} секунд")
    print(f"Результаты: {teams} команд, {schools} школ, {tournaments} турниров")

    return {
        'time': execution_time,
        'teams': teams,
        'schools': schools,
        'tournaments': tournaments
    }


def main():
    print("\nСРАВНЕНИЕ ПОДХОДОВ ")
    print("=" * 70)

    # Словарь с парсерами
    parsers = {
        "Threading": "threading_parser_sports.py",
        "Multiprocessing": "multiprocessing_parser_sports.py",
        "Async": "async_parser_sports.py"
    }

    results = {}

    for name, filename in parsers.items():
        try:
            print(f"\n🔄 Запуск {name} парсера...")
            stats = run_parser(name, filename)
            results[name] = stats
            time.sleep(2)
        except Exception as e:
            print(f"Ошибка при запуске {name}: {e}")
            results[name] = {'time': None, 'teams': 0, 'schools': 0, 'tournaments': 0}

    print("\n" + "=" * 70)
    print("ИТОГОВОЕ СРАВНЕНИЕ")
    print("=" * 70)

    print(f"\n{'Подход':<20} {'Время (сек)':<15} {'Команды':<10} {'Школы':<10} {'Турниры':<10}")
    print("-" * 65)
    for name, data in results.items():
        time_str = f"{data['time']:.2f}" if data['time'] else "N/A"
        print(f"{name:<20} {time_str:<15} {data['teams']:<10} {data['schools']:<10} {data['tournaments']:<10}")

    valid_results = {k: v for k, v in results.items() if v['time'] is not None}
    if valid_results:
        fastest = min(valid_results.items(), key=lambda x: x[1]['time'])
        slowest = max(valid_results.items(), key=lambda x: x[1]['time'])

        print(f"Самый быстрый: {fastest[0]} ({fastest[1]['time']:.2f} секунд)")
        print(f"Самый медленный: {slowest[0]} ({slowest[1]['time']:.2f} секунд)")
        print(
            f"Разница: {slowest[1]['time'] - fastest[1]['time']:.2f} секунд ({slowest[1]['time'] / fastest[1]['time']:.2f}x)")


if __name__ == "__main__":
    main()