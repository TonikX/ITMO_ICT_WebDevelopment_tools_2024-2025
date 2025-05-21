import asyncio
import aiohttp
import time
import random
import re
from bs4 import BeautifulSoup
from sqlalchemy.future import select
from async_connection import async_session_factory
from models import Skill
from typing import List, Dict, Any, Optional

async def get_http_session():
    """Создает асинхронную HTTP сессию с настройками повторных попыток"""
    timeout = aiohttp.ClientTimeout(total=30)
    connector = aiohttp.TCPConnector(limit_per_host=10)
    session = aiohttp.ClientSession(
        timeout=timeout,
        connector=connector,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    )
    return session

def extract_skills_from_job(job_data: Dict[str, Any]) -> List[Dict[str, str]]:
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

async def save_skills(skills: List[Dict[str, str]]) -> List[str]:
    """Асинхронно сохраняет навыки в базу данных используя asyncpg"""
    saved_skills = []
    
    # Используем асинхронную сессию SQLAlchemy
    async with async_session_factory() as session:
        for skill_data in skills:
            # Проверяем, существует ли уже такой навык
            result = await session.execute(
                select(Skill).where(Skill.name.ilike(f"%{skill_data['name']}%"))
            )
            existing_skill = result.scalars().first()
            
            if not existing_skill:
                skill = Skill(
                    name=skill_data['name'],
                    description=skill_data['description'],
                    category=skill_data['category']
                )
                session.add(skill)
                await session.commit()
                saved_skills.append(skill_data['name'])
                print(f"Асинхронно добавлен навык: {skill_data['name']}")
    
    return saved_skills

async def parse_job(http_session: aiohttp.ClientSession, job_id: int) -> Optional[Dict[str, Any]]:
    """Асинхронно парсит вакансию по ID и сохраняет навыки в базу данных"""
    try:
        url = f"https://jobs.yourcodereview.com/api/jobs/{job_id}"
        
        async with http_session.get(url) as response:
            # Если вакансия не найдена, просто возвращаем None
            if response.status == 404:
                print(f"Вакансия с ID {job_id} не найдена")
                return None
            
            response.raise_for_status()
            job_data = await response.json()
            
            # Если вакансия не активна, пропускаем
            if not job_data.get('active', False):
                print(f"Вакансия с ID {job_id} не активна")
                return None
            
            # Извлекаем навыки из данных о вакансии
            skills = extract_skills_from_job(job_data)
            
            # Сохраняем навыки в базу данных
            saved_skills = await save_skills(skills)
            
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

async def process_jobs(start_id: int, end_id: int):
    """Асинхронно обрабатывает диапазон вакансий"""
    # Создаем асинхронную HTTP сессию
    async with await get_http_session() as http_session:
        # Создаем список задач для всех вакансий
        tasks = []
        for job_id in range(start_id, end_id + 1):
            # Добавляем случайную задержку между запросами
            await asyncio.sleep(random.uniform(0.05, 0.1))
            task = asyncio.create_task(parse_job(http_session, job_id))
            tasks.append(task)
        
        # Запускаем все задачи и ждем их завершения
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Фильтруем результаты, исключая None и исключения
        valid_results = [r for r in results if r is not None and not isinstance(r, Exception)]
        
        return valid_results

async def main():
    start_time = time.time()
    
    # Диапазон ID вакансий для парсинга
    start_id = 90001
    end_id = 140570
    
    # Обрабатываем вакансии асинхронно
    results = await process_jobs(start_id, end_id)
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Время выполнения (asyncio): {execution_time:.2f} секунд")
    print(f"Всего обработано вакансий: {len(results)}")
    print(f"Всего найдено уникальных навыков: {sum(len(r['skills']) for r in results)}")

if __name__ == "__main__":
    # Запускаем асинхронную функцию main
    asyncio.run(main())