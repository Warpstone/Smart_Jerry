# -*- coding: utf-8 -*- 
# pylint: disable=non-ascii-bytes

from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

# Импорт модулей
from weather_module import get_weather
from greetings_module import get_motivational_greeting
from exchange_module import get_exchange_rates
from birthday_module import get_birthday_reminder

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
    birthday_reminder = get_birthday_reminder()
    
    # Формируем полное сообщение
    full_message = f"""{greeting}

🌤️ {weather}

{exchange_rates}"""
    
    # Добавляем напоминание о дне рождения, если есть
    if birthday_reminder:
        full_message += f"\n\n{birthday_reminder}"
    
    full_message += "\n\nХорошего дня! 😊"
    
    bot.send_message(chat_id=USER_CHAT_ID, text=full_message)
    print(f"[{datetime.now()}] Утреннее сообщение отправлено")

# Планировщик задач
scheduler = BlockingScheduler(timezone="Europe/Moscow")
scheduler.add_job(send_morning_message, 'cron', hour=9, minute=0)

print("✅ Умный Джери запущен и ждёт 9:00 ...")
scheduler.start()