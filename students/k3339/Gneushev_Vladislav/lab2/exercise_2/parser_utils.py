from bs4 import BeautifulSoup

def parse_car_types_from_html(html_content: str) -> list[str]:
    soup = BeautifulSoup(html_content, 'html.parser')
    model_links = soup.select('td.item_info a.mg_stop_link:not(.float-start)')
    model_names = [link.text.strip() for link in model_links]
    return model_names
