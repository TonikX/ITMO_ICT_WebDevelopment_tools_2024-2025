import threading
import requests
import time
import random
import json
from sqlmodel import Session, select
from connection import engine
from models import Skill
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import queue
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
                    print(f"Поток: {threading.current_thread().name}, Добавлен навык: {skill_data['name']}")
        
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

def worker(job_queue):
    """Функция работы потока, обрабатывающего очередь вакансий"""
    while not job_queue.empty():
        try:
            job_id = job_queue.get(block=False)
            parse_job(job_id)
            # Случайная задержка между запросами
            time.sleep(random.uniform(0.2, 0.5))
        except queue.Empty:
            break
        except Exception as e:
            print(f"Ошибка в потоке {threading.current_thread().name}: {e}")
        finally:
            job_queue.task_done()

def main():
    start_time = time.time()
    
    # Диапазон ID вакансий для парсинга
    start_id = 0
    end_id = 45000
    
    # Создаем очередь вакансий для обработки
    job_queue = queue.Queue()
    for job_id in range(start_id, end_id + 1):
        job_queue.put(job_id)
    
    # Создаем пул потоков для обработки вакансий
    num_threads = 10  # Используем 10 потоков
    threads = []
    
    for i in range(num_threads):
        thread = threading.Thread(target=worker, args=(job_queue,))
        thread.daemon = True
        threads.append(thread)
        thread.start()
        # Небольшая задержка между запуском потоков
        time.sleep(0.1)
    
    # Ожидаем завершения всех задач в очереди
    job_queue.join()
    
    # Ожидаем завершения всех потоков
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Время выполнения (threading): {execution_time:.2f} секунд")
    print(f"Всего обработано вакансий: {end_id - start_id + 1}")

if __name__ == "__main__":
    main()