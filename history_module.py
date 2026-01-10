# history_module.py
import requests
from datetime import datetime


def get_historical_events(language='ru', count=2):
    """
    Возвращает 1-2 интересных исторических события на сегодня
    language: 'ru' или 'en'
    count: сколько событий показать (1-3 оптимально)
    """
    today = datetime.now()
    month = today.strftime("%m")
    day = today.strftime("%d")

    url = f"https://api.wikimedia.org/feed/v1/wikipedia/{language}/onthisday/all/{month}/{day}"

    try:
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        data = response.json()

        events = data.get('events', [])
        if not events:
            return "Сегодня в истории ничего особо интересного не нашлось 😅"

        # Берём самые "главные" (обычно первые — самые значимые)
        selected = events[:count]

        result = "📜 Сегодня в истории:\n"
        for event in selected:
            year = event.get('year', '???')
            text = event.get('text', '').strip()
            result += f"• {year} — {text}\n"

        return result.rstrip()

    except Exception as e:
        print(f"Ошибка при получении исторических событий: {e}")
        return "Не удалось загрузить события из истории сегодня 🤷‍♂️"