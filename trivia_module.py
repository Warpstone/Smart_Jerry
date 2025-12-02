# -*- coding: utf-8 -*-
# pylint: disable=non-ascii-bytes

import requests
import logging
import random
import time
from datetime import datetime

# === Настройки API ===
NUMBERS_API_URL = "http://numbersapi.com"
HEADERS = {"User-Agent": "SmartJerryBot/1.0"}

def get_daily_trivia():
    """
    Получает случайный факт о числе, дате или математике через Numbers API.
    """
    try:
        # Выбираем случайный тип факта для разнообразия
        trivia_type = random.choice(['math', 'date'])

        # Строим URL для запроса
        # trivia_type='math': http://numbersapi.com/random/math
        # trivia_type='date': http://numbersapi.com/random/date
        url = f"{NUMBERS_API_URL}/random/{trivia_type}"

        # Получаем факт в виде обычного текста (text/plain)
        response = _http_get_with_retries(url)
        fact_text = response.text.strip()

        # Форматируем сообщение
        if trivia_type == 'math':
            title = "🔢 *Математический факт дня*"
        else:  # trivia_type == 'date'
            title = "🗓️ *Факт из истории (дата)"

        message = f"""
{title}

{fact_text}

_Утро начинается с когнитивной разминки!_
"""
        return message.strip()

    except Exception as e:
        logging.error(f"Ошибка при получении факта из Numbers API: {e}")
        # Заглушка на случай ошибки API
        return "🧠 *Упражнение для мозга:* Сегодняшний факт ушел пить кофе. Начните день с 10 приседаний, чтобы его заменить!"