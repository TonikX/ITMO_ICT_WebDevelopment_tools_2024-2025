import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


def fetch_vc_money_posts_selenium(desired_count=30, url="https://vc.ru/money"):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    SCROLL_PAUSE = 2
    posts_seen = set()
    posts = []

    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(posts) < desired_count:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

        soup = BeautifulSoup(driver.page_source, "html.parser")
        for post in soup.find_all("div", class_="content content--short"):
            title_tag = post.find("div", class_="content-title")
            link_tag = post.find("a", class_="content__link")
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                link = "https://vc.ru" + link_tag["href"]
                if link not in posts_seen:
                    posts_seen.add(link)
                    print(f"-- Post #{len(posts)+1} added")
                    posts.append({"title": title, "link": link})

        if len(posts) >= desired_count:
            break

    driver.quit()
    return posts[:desired_count]


if __name__ == "__main__":
    data = fetch_vc_money_posts_selenium(desired_count=400)

    with open("vc_money_posts.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(data)} posts to vc_money_posts.json")
