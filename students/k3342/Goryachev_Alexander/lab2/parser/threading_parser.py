import threading
import time
import requests
from name_grabber import grab_name
urls = [
"https://habr.com/ru/articles/842210/",
"https://habr.com/ru/articles/825532/",
"https://habr.com/ru/companies/productivity_inside/articles/818533/",
"https://habr.com/ru/articles/870254/",
"https://habr.com/ru/articles/828004/",
"https://habr.com/ru/articles/838288/"
]

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
        print(f"Response Text: {response.text}")  # <- see what's actually returned

        # Only try to parse JSON if response looks OK
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
    threads = []

    for url in urls:
        t = threading.Thread(target=worker, args=(url,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")

#1.01