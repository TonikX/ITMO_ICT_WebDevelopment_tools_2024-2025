import requests


def run_parser_logic(urls: list[str]):
    results = []
    for url in urls:
        try:
            response = requests.post("http://web:8000/parse", json={"url": url})
            results.append(response.json())
        except Exception as e:
            results.append({"url": url, "status": "error", "error": str(e)})
    return results
