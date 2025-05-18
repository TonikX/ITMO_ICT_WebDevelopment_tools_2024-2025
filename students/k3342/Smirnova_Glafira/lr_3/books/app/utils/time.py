from datetime import datetime


def format_datetime(iso_string: str | datetime) -> str:
    """
    Преобразует datetime или ISO-строку в строку: "DD.MM.YYYY HH:MM".
    """
    if isinstance(iso_string, str):
        iso_string = datetime.fromisoformat(iso_string)
    return iso_string.strftime("%d.%m.%Y %H:%M")