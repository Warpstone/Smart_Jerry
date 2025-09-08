# -*- coding: utf-8 -*-
# pylint: disable=non-ascii-bytes

import requests

# Конфигурация для погоды
OW_API_KEY = '32820bd27cbe5240390b8e55a80c4ac5'
CITY = 'Saint Petersburg,RU'

def get_weather():
    """Получает погоду из OpenWeather"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OW_API_KEY}&lang=ru&units=metric"
        response = requests.get(url)
        data = response.json()

        temp = data['main']['temp']
        description = data['weather'][0]['description']

        if 'дожд' in description:
            mood = "☔  Сегодня дождик, захвати зонт!"
        elif 'облачно' in description or 'пасмурно' in description:
            mood = "☁  Пасмурно, но ты не пасмурный!"
        elif 'ясно' in description or 'солнечно' in description:
            mood = "☀  Отличный солнечный день впереди!"
        elif 'снег' in description:
            mood = "❄  Снежок за окном — зима рядом!"
        else:
            mood = "🌡 Погода как погода. Главное — твое настроение!"

        return f"Доброе утро! Сейчас в Питере {int(temp)} °C, {description}. {mood}"

    except Exception as e:
        return f"Не удалось получить погоду. Ошибка: {e}"
