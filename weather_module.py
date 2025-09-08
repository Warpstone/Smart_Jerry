# -*- coding: utf-8 -*-
# pylint: disable=non-ascii-bytes

import requests

# Конфигурация для погоды
OW_API_KEY = '32820bd27cbe5240390b8e55a80c4ac5'
CITY = 'Saint Petersburg,RU'

def get_weather():
    """Получает текущую погоду и прогноз на завтра"""
    try:
        # Получаем текущую погоду
        current_weather = get_current_weather()
        # Получаем прогноз на завтра
        tomorrow_weather = get_tomorrow_weather()
        
        return f"{current_weather}\n\n{tomorrow_weather}"

    except Exception as e:
        return f"Не удалось получить погоду. Ошибка: {e}"

def get_current_weather():
    """Получает текущую погоду"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OW_API_KEY}&lang=ru&units=metric"
        response = requests.get(url)
        data = response.json()

        temp = data['main']['temp']
        description = data['weather'][0]['description']

        if 'дожд' in description:
            mood = "☔ Сегодня дождик, захвати зонт!"
        elif 'облачно' in description or 'пасмурно' in description:
            mood = "☁  Пасмурно, но ты не пасмурный!"
        elif 'ясно' in description or 'солнечно' in description:
            mood = "☀  Отличный солнечный день впереди!"
        elif 'снег' in description:
            mood = "❄  Снежок за окном — зима рядом!"
        else:
            mood = "🌡 Погода как погода. Главное — твое настроение!"

        return f"🌤️ Сегодня в Питере {int(temp)} °C, {description}. {mood}"

    except Exception as e:
        return f"Не удалось получить текущую погоду. Ошибка: {e}"

def get_tomorrow_weather():
    """Получает прогноз погоды на завтра"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={OW_API_KEY}&lang=ru&units=metric"
        response = requests.get(url)
        data = response.json()

        # Получаем прогноз на завтра (обычно это 8-й элемент в списке, что соответствует завтрашнему дню)
        tomorrow_data = data['list'][8]  # 8-й элемент = завтра в 12:00
        
        temp = tomorrow_data['main']['temp']
        description = tomorrow_data['weather'][0]['description']
        
        # Получаем минимальную и максимальную температуру на завтра
        temp_min = tomorrow_data['main']['temp_min']
        temp_max = tomorrow_data['main']['temp_max']

        if 'дожд' in description:
            forecast_mood = "☔ Завтра возможен дождь, подготовься!"
        elif 'облачно' in description or 'пасмурно' in description:
            forecast_mood = "☁  Завтра будет облачно, но настроение солнечное!"
        elif 'ясно' in description or 'солнечно' in description:
            forecast_mood = "☀  Завтра обещает быть солнечным днем!"
        elif 'снег' in description:
            forecast_mood = "❄  Завтра возможен снег, зима близко!"
        else:
            forecast_mood = "🌡  Завтра погода будет интересной!"

        return f"📅 Завтра в Питере: {int(temp)} °C ({int(temp_min)}°-{int(temp_max)}°), {description}. {forecast_mood}"

    except Exception as e:
        return f"Не удалось получить прогноз на завтра. Ошибка: {e}"
