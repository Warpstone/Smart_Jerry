# -*- coding: utf-8 -*- 
# pylint: disable=non-ascii-bytes

from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

# Импорт модулей
from weather_module import get_weather
from greetings_module import get_motivational_greeting
from exchange_module import get_exchange_rates, get_currency_analysis, get_crypto_analysis, get_weekly_currency_summary, get_weekly_crypto_summary
from birthday_module import get_birthday_reminder
from memorial_module import get_memorial_reminder
from investment_module import get_investment_wisdom
from book_week_module import get_book_of_the_week_with_api

# Конфигурация бота
TELEGRAM_TOKEN = '7627055581:AAHtAlEKgbjhQYid8I-bUBul6UKqjFQAxFo'
USER_CHAT_ID = '94476735'

# Инициализация бота
bot = Bot(token=TELEGRAM_TOKEN)

def send_morning_message():
    """Отправляет утреннее информационное сообщение в Telegram"""
    greeting = get_motivational_greeting()
    weather = get_weather()
    exchange_rates = get_exchange_rates()
    currency_analysis = get_currency_analysis()
    crypto_analysis = get_crypto_analysis()
    investment_wisdom = get_investment_wisdom()
    birthday_reminder = get_birthday_reminder()
    memorial_reminder = get_memorial_reminder()
    
    # Проверяем, воскресенье ли сегодня
    today = datetime.now()
    is_sunday = today.weekday() == 6  # 6 = воскресенье
    
    # Формируем полное сообщение
    full_message = f"""{greeting}

🌤️ {weather}

{exchange_rates}

{currency_analysis}

{crypto_analysis}

{investment_wisdom}"""
    
    # Добавляем книгу недели только по воскресеньям
    if is_sunday:
        book_of_week = get_book_of_the_week_with_api()
        full_message += f"\n\n{book_of_week}"
    
    # Добавляем напоминание о дне рождения, если есть
    if birthday_reminder:
        full_message += f"\n\n{birthday_reminder}"
    
    # Добавляем напоминание о дне памяти, если есть
    if memorial_reminder:
        full_message += f"\n\n{memorial_reminder}"
    
    full_message += "\n\nХорошего дня! 😊"
    
    # Используем синхронный метод для отправки сообщения
    import asyncio
    asyncio.run(bot.send_message(chat_id=USER_CHAT_ID, text=full_message, parse_mode='Markdown'))
    print(f"[{datetime.now()}] Утреннее сообщение отправлено")

def send_weekly_summary():
    """Отправляет еженедельную сводку по рынку валют и криптовалют"""
    greeting = get_motivational_greeting()
    weekly_currency_summary = get_weekly_currency_summary()
    weekly_crypto_summary = get_weekly_crypto_summary()
    investment_wisdom = get_investment_wisdom()
    
    # Формируем еженедельное сообщение
    weekly_message = f"""{greeting}

📊 *ЕЖЕНЕДЕЛЬНАЯ СВОДКА ПО РЫНКУ*

{weekly_currency_summary}

{weekly_crypto_summary}

{investment_wisdom}

Хорошего воскресенья! 😊"""
    
    # Используем синхронный метод для отправки сообщения
    import asyncio
    asyncio.run(bot.send_message(chat_id=USER_CHAT_ID, text=weekly_message, parse_mode='Markdown'))
    print(f"[{datetime.now()}] Еженедельная сводка отправлена")

# Планировщик задач
scheduler = BlockingScheduler(timezone="Europe/Moscow")
scheduler.add_job(send_morning_message, 'cron', hour=9, minute=0)  # Ежедневно в 9:00
scheduler.add_job(send_weekly_summary, 'cron', day_of_week=6, hour=10, minute=0)  # Воскресенье в 10:00

print("✅ Умный Джери запущен и ждёт:")
print("   📅 Ежедневные сообщения в 9:00")
print("   📊 Еженедельные сводки по воскресеньям в 10:00")
scheduler.start()