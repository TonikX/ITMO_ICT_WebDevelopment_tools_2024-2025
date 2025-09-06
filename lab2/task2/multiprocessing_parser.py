import multiprocessing
import requests
import time

from sqlmodel import Session, select
from connection import engine
from models import Skill
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
from bs4 import BeautifulSoup

def get_session():
    """Создает сессию requests с настройками повторных попыток"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def extract_skills_from_job(job_data):
    """Извлекает навыки из данных о вакансии"""
    skills = []
    
    # Извлекаем специальность как основной навык
    if job_data.get('speciality'):
        skills.append({
            'name': job_data['speciality'].upper(),
            'category': 'Programming Language',
            'description': f"Programming language or technology: {job_data['speciality']}"
        })
    
    # Извлекаем навыки из описания вакансии
    description = job_data.get('description', '')
    if description:
        # Удаляем HTML-теги для анализа текста
        soup = BeautifulSoup(description, 'html.parser')
        text = soup.get_text()
        
        # Ищем технологии и навыки в тексте
        # Ищем списки технологий, часто они указаны после "стек:", "технологии:", "требования:" и т.д.
        stack_matches = re.findall(r'(?:стек|технологии|требования|навыки|опыт работы с|знание)(?:[:\s]+)([^\.]+)', text, re.IGNORECASE)
        for match in stack_matches:
            # Разбиваем на отдельные технологии
            techs = re.split(r'[,;\s]+', match)
            for tech in techs:
                tech = tech.strip()
                if tech and len(tech) > 1 and tech.lower() not in ['и', 'или', 'the', 'a', 'an', 'от', 'до', 'лет', 'года']:
                    skills.append({
                        'name': tech,
                        'category': 'Technology',
                        'description': f"Technology or skill mentioned in job description: {tech}"
                    })
        
        # Ищем конкретные технологии по шаблонам
        tech_patterns = [
            r'(?:C#|\.NET|ASP\.NET|JavaScript|TypeScript|Python|Java|Kotlin|Swift|Go|Rust|PHP|Ruby|SQL|NoSQL)',
            r'(?:React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|Hibernate|Laravel|Rails)',
            r'(?:PostgreSQL|MySQL|Oracle|MongoDB|Cassandra|Redis|Elasticsearch|DynamoDB)',
            r'(?:Docker|Kubernetes|AWS|Azure|GCP|Terraform|Ansible|Jenkins|GitLab CI|GitHub Actions)',
            r'(?:REST|GraphQL|gRPC|WebSocket|Kafka|RabbitMQ|NATS|ZeroMQ)',
            r'(?:HTML|CSS|SASS|LESS|Bootstrap|Tailwind|Material UI|Ant Design)',
            r'(?:TDD|BDD|CI/CD|Agile|Scrum|Kanban|DevOps|SRE)'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                skills.append({
                    'name': match,
                    'category': 'Technology',
                    'description': f"Technology or skill mentioned in job description: {match}"
                })
    
    # Удаляем дубликаты (по имени, регистронезависимо)
    unique_skills = {}
    for skill in skills:
        skill_name = skill['name'].lower()
        if skill_name not in unique_skills:
            unique_skills[skill_name] = skill
    
    return list(unique_skills.values())

def parse_job(job_id):
    """Парсит вакансию по ID и сохраняет навыки в базу данных"""
    try:
        url = f"https://jobs.yourcodereview.com/api/jobs/{job_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        
        session = get_session()
        response = session.get(url, headers=headers, timeout=10)
        
        # Если вакансия не найдена, просто возвращаем None
        if response.status_code == 404:
            print(f"Вакансия с ID {job_id} не найдена")
            return None
        
        response.raise_for_status()
        job_data = response.json()
        
        # Если вакансия не активна, пропускаем
        if not job_data.get('active', False):
            print(f"Вакансия с ID {job_id} не активна")
            return None
        
        # Извлекаем навыки из данных о вакансии
        skills = extract_skills_from_job(job_data)
        
        # Сохраняем навыки в базу данных
        saved_skills = []
        with Session(engine) as session:
            for skill_data in skills:
                # Проверяем, существует ли уже такой навык
                existing_skill = session.exec(
                    select(Skill).where(Skill.name.ilike(f"%{skill_data['name']}%"))
                ).first()
                
                if not existing_skill:
                    skill = Skill(
                        name=skill_data['name'],
                        description=skill_data['description'],
                        category=skill_data['category']
                    )
                    session.add(skill)
                    session.commit()
                    saved_skills.append(skill_data['name'])
                    print(f"Процесс: {multiprocessing.current_process().name}, Добавлен навык: {skill_data['name']}")
        
        print(f"Обработана вакансия {job_id}: {job_data.get('title', 'Без названия')} в {job_data.get('company_name', 'Неизвестная компания')}")
        return {
            'job_id': job_id,
            'title': job_data.get('title', ''),
            'company': job_data.get('company_name', ''),
            'skills': saved_skills
        }
    except Exception as e:
        print(f"Ошибка при парсинге вакансии {job_id}: {e}")
        return None

def process_batch(job_ids):
    """Обрабатывает пакет вакансий в отдельном процессе"""
    for job_id in job_ids:
        try:
            parse_job(job_id)
        except Exception as e:
            print(f"Ошибка в процессе {multiprocessing.current_process().name} при обработке вакансии {job_id}: {e}")

def main():
    start_time = time.time()
    
    # Диапазон ID вакансий для парсинга
    start_id = 0
    end_id = 1500
    
    # Получаем список всех ID вакансий
    job_ids = list(range(start_id, end_id + 1))
    
    # Определяем количество процессов и размер пакета
    num_processes = multiprocessing.cpu_count()  # Используем количество ядер CPU
    batch_size = len(job_ids) // num_processes
    
    # Разбиваем список ID вакансий на пакеты
    batches = []
    for i in range(0, len(job_ids), batch_size):
        batch = job_ids[i:i + batch_size]
        batches.append(batch)
    
    # Если количество пакетов меньше количества процессов, добавляем пустые пакеты
    while len(batches) < num_processes:
        batches.append([])
    
    # Если количество пакетов больше количества процессов, объединяем последние пакеты
    if len(batches) > num_processes:
        last_batch = []
        for i in range(num_processes - 1, len(batches)):
            last_batch.extend(batches[i])
        batches = batches[:num_processes - 1] + [last_batch]
    
    # Создаем и запускаем процессы
    processes = []
    for batch in batches:
        if batch:  # Пропускаем пустые пакеты
            process = multiprocessing.Process(target=process_batch, args=(batch,))
            processes.append(process)
            process.start()
    
    # Ожидаем завершения всех процессов
    for process in processes:
        process.join()
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Время выполнения (multiprocessing): {execution_time:.2f} секунд")
    print(f"Всего обработано вакансий: {end_id - start_id + 1}")

if __name__ == "__main__":
    main()