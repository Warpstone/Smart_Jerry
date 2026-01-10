# -*- coding: utf-8 -*-
# pylint: disable=non-ascii-bytes

from datetime import datetime

ANNIVERSARIES = {
    (11, 1): "Годовщина встречи с девушкой",
}


def get_anniversary_reminder():
    """Проверяет годовщины и возвращает напоминание"""
    today = datetime.now()
    current_month = today.month
    current_day = today.day

    # Проверяем годовщину сегодня
    anniversary_today = check_anniversary_today(current_month, current_day)
    if anniversary_today:
        return anniversary_today

    # Проверяем напоминания за месяц, 2 недели, неделю, 3 дня, 1 день
    reminder = check_upcoming_anniversaries(current_month, current_day)
    if reminder:
        return reminder

    return None


def check_anniversary_today(month, day):
    """Проверяет, есть ли годовщина сегодня"""
    if (month, day) in ANNIVERSARIES:
        name = ANNIVERSARIES[(month, day)]
        return f"🎉 Сегодня {name.lower()}! Поздравь её!"
    return None


def check_upcoming_anniversaries(current_month, current_day):
    """Проверяет предстоящие годовщины (только за месяц и ближе)"""
    today = datetime.now()

    for (month, day), name in ANNIVERSARIES.items():
        # Создаем дату годовщины в текущем году
        anniversary_this_year = datetime(today.year, month, day)

        # Если годовщина уже прошла в этом году, берем следующий год
        if anniversary_this_year < today:
            anniversary_next_year = datetime(today.year + 1, month, day)
            days_until = (anniversary_next_year - today).days
        else:
            days_until = (anniversary_this_year - today).days

        # Показываем напоминания только за указанные интервалы
        if days_until == 30:
            return f"📅 Через месяц {name.lower()}! Подготовься заранее!"
        elif days_until == 14:
            return f"📅 Через 2 недели {name.lower()}! Время подумать о подарке!"
        elif days_until == 7:
            return f"📅 Через неделю {name.lower()}! Не забудь!"
        elif days_until == 3:
            return f"📅 Через 3 дня {name.lower()}! Последние приготовления!"
        elif days_until == 1:
            return f"📅 Завтра {name.lower()}! Удачи!"
        elif days_until == 0:
            return f"🎉 Сегодня {name.lower()}! Поздравь её!"
        # Если дней больше 30 или не в интервалах, не показываем напоминание

    return None


def get_all_anniversaries():
    """Возвращает список всех годовщин для отладки (по аналогии с birthdays)"""
    result = "📅 Все годовщины:\n"
    for (month, day), name in sorted(ANNIVERSARIES.items()):
        month_names = {
            1: "января", 2: "февраля", 3: "марта", 4: "апреля",
            5: "мая", 6: "июня", 7: "июля", 8: "августа",
            9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
        }
        result += f"• {day} {month_names[month]} - {name}\n"
    return result