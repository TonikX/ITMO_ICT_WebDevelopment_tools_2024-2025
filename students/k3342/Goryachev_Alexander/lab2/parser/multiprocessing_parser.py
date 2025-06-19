urls = [
"https://habr.com/ru/articles/905776/",
"https://habr.com/ru/articles/843898/",
"https://habr.com/ru/articles/860888/",
"https://habr.com/ru/articles/849116/",
"https://habr.com/ru/companies/timeweb/articles/819209/",
"https://habr.com/ru/articles/855580/"
]
import multiprocessing
import requests
import time
from name_grabber import grab_name

API_URL = "http://127.0.0.1:8000/auth/register"

def create_user(username):
    user_data = {
        "username": username,
        "email": f"{username.strip()}@example.com",
        "password": "defaultpassword123"
    }
    try:
        response = requests.post(API_URL, json=user_data)
        print(f"[{username}] Status: {response.status_code}")
        print(f"Response Text: {response.text}")

        if response.headers.get("content-type") == "application/json":
            print("Parsed JSON:", response.json())
        else:
            print("Non-JSON response received")

    except Exception as e:
        print(f"Error creating {username} : {e}")

def worker(url):
    try:
        username = grab_name(url)
        create_user(username)
    except Exception as e:
        print(f"Error processing {url}: {e}")

def main():
    processes = []

    for url in urls:
        p = multiprocessing.Process(target=worker, args=(url,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")

#1.77