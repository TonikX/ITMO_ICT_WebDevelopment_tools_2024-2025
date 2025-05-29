from bs4 import BeautifulSoup


URLS = [
    "https://www.tourradar.com/srp/d-bulgaria",
    "https://www.tourradar.com/srp/d-benin",
    "https://www.tourradar.com/srp/d-kenya",
    "https://www.tourradar.com/srp/d-andorra",
    "https://www.tourradar.com/srp/d-japan",
    "https://www.tourradar.com/srp/d-greenland"
]

def extract_tours_from_html(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    tour_cards = soup.find_all("div", class_="js-ao-serp-tour-card")
    results = []

    for card in tour_cards:
        try:
            title_tag = card.find("h3", class_="ao-serp-tour-card__title")
            title = title_tag.get_text(strip=True) if title_tag else "N/A"

            destination_tag = card.find("dt", string="Destinations")
            destination = destination_tag.find_next("dd").get_text(strip=True).split(",")[0] if destination_tag else "N/A"

            age_tag = card.find("dt", string="Age Range")
            age_range = age_tag.find_next("dd").get_text(strip=True) if age_tag else "N/A"

            duration_block = card.find("dl", class_="ao-serp-tour-card__detail-item--duration")
            duration_days = duration_block.find("dd").get_text(strip=True) if duration_block else "N/A"
            results.append({
                "title": title,
                "destination": destination,
                "age": age_range,
                "duration": duration_days
            })
        except Exception as inner_e:
            print(f"Ошибка при парсинге: {inner_e}")
    return results
