# -*- coding: utf-8 -*-
# pylint: disable=non-ascii-bytes

from datetime import datetime, timedelta

# Список дней памяти (месяц, день, год, имя)
MEMORIAL_DATES = {
    (8, 4, 2025): "Миша Воски"
}

def get_memorial_reminder():
    """Проверяет дни памяти и возвращает напоминание"""
    today = datetime.now()
    current_month = today.month
    current_day = today.day
    
    # Проверяем день памяти сегодня
    memorial_today = check_memorial_today(current_month, current_day)
    if memorial_today:
        return memorial_today
    
    # Проверяем напоминания за 3 дня и каждый день до дня памяти
    reminder = check_upcoming_memorials(current_month, current_day)
    if reminder:
        return reminder
    
    return None

def check_memorial_today(month, day):
    """Проверяет, есть ли день памяти сегодня"""
    today = datetime.now()
    current_year = today.year
    
    # Проверяем все годы для этого дня
    for (mem_month, mem_day, mem_year), name in MEMORIAL_DATES.items():
        if month == mem_month and day == mem_day:
            years_passed = current_year - mem_year
            return f"🕊️ Сегодня день памяти ({years_passed} лет) - {name}. Помним и чтим."
    return None

def check_upcoming_memorials(current_month, current_day):
    """Проверяет предстоящие дни памяти (только за 3 дня и ближе)"""
    today = datetime.now()
    current_year = today.year
    
    for (month, day, year), name in MEMORIAL_DATES.items():
        # Создаем дату дня памяти в текущем году
        memorial_this_year = datetime(current_year, month, day)
        
        # Если день памяти уже прошел в этом году, берем следующий год
        if memorial_this_year < today:
            memorial_next_year = datetime(current_year + 1, month, day)
            days_until = (memorial_next_year - today).days
            years_passed = current_year + 1 - year
        else:
            days_until = (memorial_this_year - today).days
            years_passed = current_year - year
        
        # Показываем напоминания только за 3 дня и ближе
        if days_until == 3:
            return f"🕊️ Через 3 дня день памяти ({years_passed} лет) - {name}. Подготовься к поминовению."
        elif days_until == 2:
            return f"🕊️ Завтра день памяти ({years_passed} лет) - {name}. Время для поминовения."
        elif days_until == 1:
            return f"🕊️ Послезавтра день памяти ({years_passed} лет) - {name}. Последний день для подготовки."
        elif days_until == 0:
            return f"🕊️ Сегодня день памяти ({years_passed} лет) - {name}. Помним и чтим."
        # Если дней больше 3, не показываем напоминание
    
    return None

def get_all_memorials():
    """Возвращает список всех дней памяти для отладки"""
    result = "🕊️ Все дни памяти:\n"
    for (month, day, year), name in sorted(MEMORIAL_DATES.items()):
        month_names = {
            1: "января", 2: "февраля", 3: "марта", 4: "апреля",
            5: "мая", 6: "июня", 7: "июля", 8: "августа",
            9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
        }
        result += f"• {day} {month_names[month]} {year} - {name}\n"
    return result
