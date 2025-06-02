async def fetch(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            return await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_title_author(full_title: str):
    parts = full_title.split("–")
    main_part = parts[0].strip() if parts else full_title.strip()

    if "," in main_part:
        title_part, author_part = main_part.split(",", 1)
        title = title_part.strip()
        author = author_part.strip()
    else:
        title = main_part
        author = ""

    return title, author
