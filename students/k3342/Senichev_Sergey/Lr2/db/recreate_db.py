import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db_utils import init_db

def recreate_database():
    db_path = 'web_pages.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Старая база данных удалена")
    
    session = init_db()
    session.close()
    print("Новая база данных создана")

if __name__ == "__main__":
    recreate_database() 