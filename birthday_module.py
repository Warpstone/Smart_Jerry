# -*- coding: utf-8 -*-
# pylint: disable=non-ascii-bytes

from datetime import date

# Список дней рождения
BIRTHDAYS = {
    (1, 24): ["бабушка Люда (Аня)",
             "Андрей Анатольевич, Анин папа"],
    (1, 29): "Антон Павлович Чехов",
    (2, 4): ["т. Галя", "Макар, сын Светы (сестра)"],
    (2, 7): "Чарльз Диккенс",
    (2, 16): "Андрей, мч бабушки Люды",
    (2, 22): "т. Лена",
    (5, 26): "д. Петя", 
    (6, 9): "Стас Игнатов",
    (6, 16): "Мой",
    (6, 28): "Витя арт из Грузии",
    (7, 14): "Ирина Диговна",
    (7, 15): "двоюродный брат Дима",
    (7, 21): "Марк, сын двоюродной сестры Светы",
    (9, 15): "Агата Кристи",
    (10, 2): "Мама",
    (10, 3): "д. Женя",
    (10, 4): "двоюродная сестра Света",
    (10, 8): "Света Кожевникова",
    (10, 9): "Елена Анатольевна",
    (11, 21): "двоюродный брат Миша (ныне покойный)",
    (11, 30): "Уинстон Черчилль",
    (12, 10): "Анюта",
    (12, 24): "Родион"
}

def get_birthday_reminder():
    """Проверяет дни рождения и возвращает напоминание"""
    today = date.today()
    current_month = today.month
    current_day = today.day
    
    # Проверяем день рождения сегодня
    birthday_today = check_birthday_today(current_month, current_day)
    if birthday_today:
        return birthday_today
    
    # Проверяем напоминания за 3 дня и каждый день до дня рождения
    reminder = check_upcoming_birthdays(current_month, current_day)
    if reminder:
        return reminder
    
    return None

def check_birthday_today(month, day):
    """Проверяет, есть ли день рождения сегодня"""
    if (month, day) in BIRTHDAYS:
        name = BIRTHDAYS[(month, day)]
        return f"🎂 Сегодня день рождения у {name}!"
    return None

def check_upcoming_birthdays(current_month, current_day):
    """Проверяет предстоящие дни рождения (только за 3 дня и ближе)"""
    today = date.today()
    
    for (month, day), name in BIRTHDAYS.items():
        # Создаем дату дня рождения в текущем году
        birthday_this_year = date(today.year, month, day)
        
        # Если день рождения уже прошел в этом году, берем следующий год
        if birthday_this_year < today:
            birthday_next_year = date(today.year + 1, month, day)
            days_until = (birthday_next_year - today).days
        else:
            days_until = (birthday_this_year - today).days
        
        # Показываем напоминания только за 3 дня и ближе
        if days_until == 3:
            return f"📅 Через 3 дня день рождения у {name}! Не забудь поздравить!"
        elif days_until == 2:
            return f"📅 Послезавтра день рождения у {name}! Подготовь поздравление!"
        elif days_until == 1:
            return f"📅 Завтра день рождения у {name}! Последний день для подготовки!"
        elif days_until == 0:
            return f"🎂 Сегодня день рождения у {name}!"
        # Если дней больше 3, не показываем напоминание
    
    return None

def get_all_birthdays():
    """Возвращает список всех дней рождения для отладки"""
    result = "📅 Все дни рождения:\n"
    for (month, day), name in sorted(BIRTHDAYS.items()):
        month_names = {
            1: "января", 2: "февраля", 3: "марта", 4: "апреля",
            5: "мая", 6: "июня", 7: "июля", 8: "августа",
            9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
        }
        result += f"• {day} {month_names[month]} - {name}\n"
    return result
