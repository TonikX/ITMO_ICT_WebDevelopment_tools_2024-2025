import threading
import requests
from bs4 import BeautifulSoup
import psycopg2
import time
from datetime import datetime
import os
from dotenv import load_dotenv
import ssl
import certifi
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
import warnings
import urllib3
import re

# Подавляем предупреждения SSL
warnings.simplefilter('ignore', urllib3.exceptions.InsecureRequestWarning)

# Загружаем переменные окружения
load_dotenv()

# URLs спортивных сайтов для парсинга
URLS = [
    {'url': 'https://www.nhl.com/teams', 'type': 'teams'},
    {'url': 'https://www.eliteprospects.com/league/nhl', 'type': 'teams'},
    {'url': 'https://www.hockeydb.com/ihdb/stats/leagues/nhl2024', 'type': 'stats'},
    {'url': 'https://www.tsn.ca/nhl/teams', 'type': 'teams'},
    {'url': 'https://www.sportsnet.ca/hockey/nhl/teams/', 'type': 'teams'},
]

# Параметры подключения к БД
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'hockey_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'tochange'),
}

# Блокировка для потокобезопасной работы с БД
db_lock = threading.Lock()


# Класс для обхода SSL проблем
class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)


def get_db_connection():
    """Получение соединения с БД"""
    return psycopg2.connect(**DB_CONFIG)


def init_database():
    """Инициализация базы данных"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database init error: {e}")


def clear_database():
    """Очистка таблиц перед новым парсингом"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('TRUNCATE TABLE tournaments CASCADE')
        cursor.execute('TRUNCATE TABLE teams CASCADE')
        cursor.execute('TRUNCATE TABLE sport_schools CASCADE')
        cursor.execute('TRUNCATE TABLE seasons CASCADE')
        conn.commit()
        cursor.close()
        conn.close()
        print("База данных очищена перед новым парсингом")
    except Exception as e:
        print(f"Error cleaning database: {e}")


def parse_nhl_teams(soup):
    """Улучшенный парсер для NHL.com"""
    teams = []

    # Метод 1: Ищем ссылки на команды (чистый подход)
    team_links = soup.find_all('a', href=lambda h: h and '/teams/' in h and not h.endswith('/teams/'))

    for link in team_links:
        # Извлекаем название из ссылки или текста
        team_name = None
        if link.get_text(strip=True):
            team_name = link.get_text(strip=True)
        elif 'title' in link.attrs:
            team_name = link['title']
        elif link.find('img') and 'alt' in link.find('img').attrs:
            team_name = link.find('img')['alt']

        # Очищаем название от лишнего (навигация, нетекстовые элементы)
        if team_name:
            # Удаляем служебные слова и суффиксы
            team_name = re.sub(r'(Roster|Schedule|Tickets|Stats|north_east|Homepage|Go to)', '', team_name)
            team_name = team_name.strip()

            # Если имя команды слишком короткое или длинное, пропускаем
            if len(team_name) < 3 or len(team_name) > 30 or team_name.lower() == 'nhl':
                continue

            # Извлекаем город - обычно первое слово или слова перед последним словом
            parts = team_name.split()
            city = ' '.join(parts[:-1]) if len(parts) > 1 else team_name

            # Добавляем команду если её ещё нет
            if any(t['name'] == team_name for t in teams):
                continue

            teams.append({
                'name': team_name,
                'country': 'USA/Canada',
                'city': city,
                'additional_info': 'NHL official data',
                'coach': 'NHL Coach'
            })

    # Метод 2: Ищем конкретные элементы с классами команд
    if not teams:
        team_containers = soup.find_all(['div', 'li'],
                                        class_=lambda c: c and ('team' in c.lower() or 'club' in c.lower()))

        for container in team_containers:
            # Ищем название команды в разных элементах
            name_element = container.find(['h3', 'h4', 'h5', 'span', 'strong', 'a'],
                                          class_=lambda c: c and 'title' in c.lower())

            if name_element:
                team_name = name_element.get_text(strip=True)
                # Очистка названия
                team_name = re.sub(r'(Roster|Schedule|Tickets|Stats|north_east)', '', team_name)
                team_name = team_name.strip()

                if len(team_name) < 3 or len(team_name) > 30 or team_name.lower() == 'nhl':
                    continue

                # Извлекаем город
                parts = team_name.split()
                city = ' '.join(parts[:-1]) if len(parts) > 1 else team_name

                # Добавляем команду если её ещё нет
                if any(t['name'] == team_name for t in teams):
                    continue

                teams.append({
                    'name': team_name,
                    'country': 'USA/Canada',
                    'city': city,
                    'additional_info': 'NHL official data',
                    'coach': 'NHL Coach'
                })

    return teams


def parse_eliteprospects_teams(soup):
    """Улучшенный парсер для EliteProspects"""
    teams = []

    # Ищем таблицу с командами
    tables = soup.find_all('table')

    for table in tables:
        if table.find('th') and 'Team' in table.find('th').get_text():
            rows = table.find_all('tr')[1:]  # Пропускаем заголовок

            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    # Команда обычно во втором столбце
                    team_cell = cols[1]

                    # Пробуем извлечь через разные методы
                    team_name = None
                    if team_cell.find('a'):
                        team_name = team_cell.find('a').get_text(strip=True)
                    else:
                        team_name = team_cell.get_text(strip=True)

                    if team_name and len(team_name) > 2 and team_name.lower() != 'team':
                        # Определяем город - обычно первое слово
                        parts = team_name.split()
                        city = ' '.join(parts[:-1]) if len(parts) > 1 else team_name

                        teams.append({
                            'name': team_name,
                            'country': 'International',
                            'city': city,
                            'additional_info': 'EliteProspects data',
                            'coach': 'International Coach'
                        })

    return teams


def parse_other_sites_teams(soup, url):
    """Парсер для других спортивных сайтов"""
    teams = []

    # Ищем ссылки на страницы команд
    team_links = soup.find_all('a', href=lambda h: h and ('/team/' in h or '/teams/' in h))

    for link in team_links:
        team_name = link.get_text(strip=True)

        if team_name and len(team_name) > 3 and len(team_name) < 30:
            # Извлекаем город
            parts = team_name.split()
            city = ' '.join(parts[:-1]) if len(parts) > 1 else team_name

            teams.append({
                'name': team_name,
                'country': 'North America',
                'city': city,
                'additional_info': f'Parsed from {url}',
                'coach': 'TBD'
            })

    return teams


def parse_team_info(soup, url):
    """Общая функция парсинга, которая выбирает подходящий парсер"""
    if 'nhl.com' in url:
        return parse_nhl_teams(soup)
    elif 'eliteprospects' in url:
        return parse_eliteprospects_teams(soup)
    elif 'tsn.ca' in url or 'sportsnet.ca' in url:
        return parse_other_sites_teams(soup, url)

    return []


def print_parsed_data():
    """Вывод подробной информации о спарсенных данных"""
    print("\n===== СПАРСЕННЫЕ ДАННЫЕ =====")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем и выводим данные о командах
    cursor.execute("""
                   SELECT t.name as team_name, t.city, t.country, t.additional_info, s.name as school_name
                   FROM teams t
                            JOIN sport_schools s ON t.school_id = s.school_id
                   ORDER BY t.country, t.city
                   """)
    teams = cursor.fetchall()

    print(f"\n--- КОМАНДЫ ({len(teams)}) ---")
    for i, team in enumerate(teams, 1):
        print(f"{i}. {team[0]} ({team[1]}, {team[2]})")
        print(f"   Школа: {team[4]}")
        print(f"   Инфо: {team[3]}")

    # Получаем и выводим данные о турнирах
    cursor.execute("""
                   SELECT t.name, t.tournament_type, t.description, s.year
                   FROM tournaments t
                            JOIN seasons s ON t.season_id = s.season_id
                   ORDER BY t.name
                   """)
    tournaments = cursor.fetchall()

    print(f"\n--- ТУРНИРЫ ({len(tournaments)}) ---")
    for i, tournament in enumerate(tournaments, 1):
        print(f"{i}. {tournament[0]} ({tournament[3]})")
        print(f"   Тип: {tournament[1]}")
        print(f"   Описание: {tournament[2]}")

    cursor.close()
    conn.close()


def parse_and_save_threading(url_info, thread_id):
    """Парсинг страницы и сохранение в БД"""
    url = url_info['url']
    data_type = url_info['type']

    try:
        # Создаем сессию с SSL адаптером
        session = requests.Session()
        session.mount('https://', SSLAdapter())

        # Получаем страницу
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/'
        }
        response = session.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()

        # Парсим HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        if data_type == 'teams':
            teams = parse_team_info(soup, url)

            if teams:
                # Удаляем дубликаты команд
                unique_teams = []
                team_names = set()
                for team in teams:
                    if team['name'] not in team_names:
                        team_names.add(team['name'])
                        unique_teams.append(team)

                # Сохраняем в БД (потокобезопасно)
                with db_lock:
                    conn = get_db_connection()
                    cursor = conn.cursor()

                    try:
                        # Создаем пользователя для команд
                        cursor.execute("""
                                       INSERT INTO users (username, email, password_hash, status)
                                       VALUES (%s, %s, %s, %s) ON CONFLICT (username) DO
                                       UPDATE
                                           SET username = EXCLUDED.username
                                           RETURNING user_id
                                       """, ('parser_user', 'parser@example.com', 'hashed_password', 'active'))
                        user_id = cursor.fetchone()[0]

                        for team in unique_teams:
                            # Создаем спортивную школу
                            cursor.execute("""
                                           INSERT INTO sport_schools (name, country, city, contact_info)
                                           VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING
                                RETURNING school_id
                                           """, (f"{team['name']} Academy", team['country'], team['city'],
                                                 f"Youth program for {team['name']}"))

                            result = cursor.fetchone()
                            if result:
                                school_id = result[0]

                                # Создаем команду
                                cursor.execute("""
                                               INSERT INTO teams (user_id, school_id, name, coach, country, city, additional_info)
                                               VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
                                               """, (user_id, school_id, team['name'], team['coach'],
                                                     team['country'], team['city'], team['additional_info']))

                        # Добавляем сезон
                        cursor.execute("""
                                       INSERT INTO seasons (year)
                                       VALUES (%s) ON CONFLICT (year) DO
                                       UPDATE
                                           SET year = EXCLUDED.year
                                           RETURNING season_id
                                       """, ('2023/2024',))
                        season_id = cursor.fetchone()[0]

                        # Добавляем турнир
                        cursor.execute("""
                                       INSERT INTO tournaments (season_id, name, tournament_type, description)
                                       VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING
                                       """, (season_id, 'NHL Regular Season', 'league', f'Data parsed from {url}'))

                        conn.commit()
                        print(f"Thread {thread_id}: Saved {len(unique_teams)} teams from {url}")

                    except Exception as e:
                        conn.rollback()
                        print(f"Thread {thread_id}: DB error: {e}")
                    finally:
                        cursor.close()
                        conn.close()
            else:
                print(f"Thread {thread_id}: No teams found on {url}")

        return True

    except Exception as e:
        print(f"Thread {thread_id}: Error parsing {url}: {e}")
        return False


def threading_parser(url_list, num_threads=3):
    """Основная функция для threading подхода"""
    init_database()
    clear_database()
    start_time = time.time()

    # Разделяем URL между потоками
    chunk_size = max(1, len(url_list) // num_threads)
    threads = []

    for i in range(min(num_threads, len(url_list))):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < num_threads - 1 else len(url_list)
        thread_urls = url_list[start_idx:end_idx]

        if thread_urls:  # Проверяем, что есть URL для обработки
            # Создаем поток для обработки URL
            thread = threading.Thread(
                target=lambda urls, tid: [parse_and_save_threading(url, tid) for url in urls],
                args=(thread_urls, i)
            )
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    print(f"\nThreading completed in {end_time - start_time:.2f} seconds")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM teams')
    teams_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM sport_schools')
    schools_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM tournaments')
    tournaments_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    print(f"Total teams parsed: {teams_count}")
    print(f"Total sport schools created: {schools_count}")
    print(f"Total tournaments created: {tournaments_count}")

    print_parsed_data()


if __name__ == "__main__":
    threading_parser(URLS)