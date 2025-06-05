import asyncio
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
import time
from datetime import datetime, date
import os
from dotenv import load_dotenv
import ssl
import certifi
import warnings
import re

# Подавляем предупреждения SSL
warnings.filterwarnings('ignore')

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


async def init_database():
    """Инициализация пула соединений с БД"""
    return await asyncpg.create_pool(
        **DB_CONFIG,
        min_size=1,
        max_size=10
    )


async def clear_database(pool):
    """Очистка таблиц перед новым парсингом"""
    async with pool.acquire() as conn:
        await conn.execute('TRUNCATE TABLE tournaments CASCADE')
        await conn.execute('TRUNCATE TABLE teams CASCADE')
        await conn.execute('TRUNCATE TABLE sport_schools CASCADE')
        await conn.execute('TRUNCATE TABLE seasons CASCADE')

    print("База данных очищена перед новым парсингом")


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


def parse_team_info(soup, url):
    """Общая функция парсинга, которая выбирает подходящий парсер"""
    if 'nhl.com' in url:
        return parse_nhl_teams(soup)
    elif 'eliteprospects' in url:
        return parse_eliteprospects_teams(soup)
    elif 'tsn.ca' in url or 'sportsnet.ca' in url:
        # Используем общий подход для других сайтов
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

    return []


async def print_parsed_data(pool):
    """Вывод подробной информации о спарсенных данных"""
    print("\n===== СПАРСЕННЫЕ ДАННЫЕ =====")

    async with pool.acquire() as conn:
        # Получаем и выводим данные о командах
        teams = await conn.fetch("""
                                 SELECT t.name as team_name, t.city, t.country, t.additional_info, s.name as school_name
                                 FROM teams t
                                          JOIN sport_schools s ON t.school_id = s.school_id
                                 ORDER BY t.country, t.city
                                 """)

        print(f"\n--- КОМАНДЫ ({len(teams)}) ---")
        for i, team in enumerate(teams, 1):
            print(f"{i}. {team['team_name']} ({team['city']}, {team['country']})")
            print(f"   Школа: {team['school_name']}")
            print(f"   Инфо: {team['additional_info']}")

        tournaments = await conn.fetch("""
                                       SELECT t.name, t.tournament_type, t.description, s.year
                                       FROM tournaments t
                                                JOIN seasons s ON t.season_id = s.season_id
                                       ORDER BY t.name
                                       """)

        print(f"\n--- ТУРНИРЫ ({len(tournaments)}) ---")
        for i, tournament in enumerate(tournaments, 1):
            print(f"{i}. {tournament['name']} ({tournament['year']})")
            print(f"   Тип: {tournament['tournament_type']}")
            print(f"   Описание: {tournament['description']}")


async def parse_and_save_async(session, pool, url_info, task_id):
    url = url_info['url']
    data_type = url_info['type']

    try:
        # Создаем SSL контекст с сертификатами
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/'
        }

        async with session.get(url, headers=headers, ssl=ssl_context, timeout=15) as response:
            if response.status == 200:
                text = await response.text()

                soup = BeautifulSoup(text, 'html.parser')

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

                        # Сохраняем в БД
                        async with pool.acquire() as conn:
                            user_id = await conn.fetchval("""
                                                          INSERT INTO users (username, email, password_hash, status)
                                                          VALUES ($1, $2, $3, $4) ON CONFLICT (username) DO
                                                          UPDATE
                                                              SET username = EXCLUDED.username
                                                              RETURNING user_id
                                                          """, 'parser_user', 'parser@example.com', 'hashed_password',
                                                          'active')

                            # Создаем спортивные школы и команды
                            for team in unique_teams:
                                school_id = await conn.fetchval("""
                                                                INSERT INTO sport_schools (name, country, city, contact_info)
                                                                VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING
                                    RETURNING school_id
                                                                """, f"{team['name']} Academy", team['country'],
                                                                team['city'],
                                                                f"Youth program for {team['name']}")

                                if school_id:
                                    await conn.execute("""
                                                       INSERT INTO teams (user_id, school_id, name, coach, country, city, additional_info)
                                                       VALUES ($1, $2, $3, $4, $5, $6, $7) ON CONFLICT DO NOTHING
                                                       """, user_id, school_id, team['name'], team['coach'],
                                                       team['country'], team['city'], team['additional_info'])

                            # Добавляем сезон
                            season_id = await conn.fetchval("""
                                                            INSERT INTO seasons (year)
                                                            VALUES ($1) ON CONFLICT (year) DO
                                                            UPDATE
                                                                SET year = EXCLUDED.year
                                                                RETURNING season_id
                                                            """, '2023/2024')

                            # Добавляем турнир
                            await conn.execute("""
                                               INSERT INTO tournaments (season_id, name, tournament_type, description)
                                               VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING
                                               """, season_id, 'NHL Regular Season', 'league',
                                               f'Data parsed from {url}')

                        print(f"Task {task_id}: Saved {len(unique_teams)} teams from {url}")
                    else:
                        print(f"Task {task_id}: No teams found on {url}")
                    return True
                return None
            else:
                print(f"Task {task_id}: HTTP {response.status} for {url}")
                return False

    except Exception as e:
        print(f"Task {task_id}: Error parsing {url}: {e}")
        return False


async def async_parser(url_list):
    start_time = time.time()

    pool = await init_database()

    try:
        await clear_database(pool)

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(ssl=ssl_context)

        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for i, url_info in enumerate(url_list):
                task = parse_and_save_async(session, pool, url_info, i)
                tasks.append(task)

            results = await asyncio.gather(*tasks)

        end_time = time.time()
        print(f"\nAsync completed in {end_time - start_time:.2f} seconds")

        async with pool.acquire() as conn:
            teams_count = await conn.fetchval('SELECT COUNT(*) FROM teams')
            schools_count = await conn.fetchval('SELECT COUNT(*) FROM sport_schools')
            tournaments_count = await conn.fetchval('SELECT COUNT(*) FROM tournaments')

        print(f"Total teams parsed: {teams_count}")
        print(f"Total sport schools created: {schools_count}")
        print(f"Total tournaments created: {tournaments_count}")

        await print_parsed_data(pool)

    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(async_parser(URLS))