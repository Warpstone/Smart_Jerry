# -*- coding: utf-8 -*-
# pylint: disable=non-ascii-bytes

import os
import sys
import argparse
import logging
import asyncio
from datetime import datetime
from telegram import Bot

# Импорт модулей
from weather_module import get_weather
from greetings_module import get_motivational_greeting
from exchange_module import (
    get_exchange_rates,
    get_currency_analysis,
    get_crypto_analysis,
    get_weekly_currency_summary,
    get_weekly_crypto_summary,
)
from birthday_module import get_birthday_reminder
from memorial_module import get_memorial_reminder
from investment_module import get_investment_wisdom
from book_week_module import get_book_of_the_week_with_api

# Конфигурация
TELEGRAM_TOKEN = '7627055581:AAHtAlEKgbjhQYid8I-bUBul6UKqjFQAxFo'
USER_CHAT_ID = '94476735'
USER_CITY = 'Nha Trang, VN'

# Логирование
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
log_file = os.path.join(script_dir, 'bot.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='[%(asctime)s] %(message)s')

bot = Bot(token=TELEGRAM_TOKEN)

# ============================
# УТРЕННЕЕ СООБЩЕНИЕ
# ============================
async def send_morning_message():
    """Отправляет утреннее сообщение"""
    try:
        logging.info("Начинаю утреннее сообщение...")
        today = datetime.now()
        is_sunday = today.weekday() == 6  # Воскресенье

        # Получаем все данные
        greeting = get_motivational_greeting()
        weather = get_weather(USER_CITY)
        exchange_rates = get_exchange_rates()
        currency_analysis = get_currency_analysis()
        crypto_analysis = get_crypto_analysis()
        investment_wisdom = get_investment_wisdom()
        birthday_reminder = get_birthday_reminder()
        memorial_reminder = get_memorial_reminder()

        # Получаем книгу дня
        book_of_day = get_book_of_the_week_with_api()
        
        # Собираем всё в единое сообщение
        full_message = f"""{greeting}

🌤️ {weather}

{exchange_rates}

{currency_analysis}

{crypto_analysis}

{investment_wisdom}

{book_of_day}"""

        # Добавляем еженедельную сводку по воскресеньям
        if is_sunday:
            logging.info("Воскресенье - добавляю еженедельную сводку...")
            weekly_currency = get_weekly_currency_summary()
            weekly_crypto = get_weekly_crypto_summary()
            
            full_message += f"""

📊 *ЕЖЕНЕДЕЛЬНАЯ СВОДКА ПО РЫНКУ*

{weekly_currency}

{weekly_crypto}"""

        if birthday_reminder:
            full_message += f"\n\n{birthday_reminder}"

        if memorial_reminder:
            full_message += f"\n\n{memorial_reminder}"

        # Финальное приветствие зависит от дня недели
        if is_sunday:
            full_message += "\n\nХорошего воскресенья! 😊"
        else:
            full_message += "\n\nХорошего дня! 😊"

        # Отправка сообщения
        logging.info("Отправляю сообщение в Telegram...")
        await bot.send_message(chat_id=USER_CHAT_ID, text=full_message, parse_mode='HTML')
        logging.info("Сообщение отправлено успешно")

    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")
        try:
            await bot.send_message(chat_id=USER_CHAT_ID, text=f"❌ Ошибка: {e}")
        except Exception as send_error:
            logging.error(f"Не удалось отправить сообщение об ошибке: {send_error}")

# ============================
# ЕЖЕНЕДЕЛЬНОЕ СООБЩЕНИЕ
# ============================
async def send_weekly_summary():
    """Отправляет еженедельную сводку"""
    try:
        today = datetime.now()
        if today.weekday() != 6:
            logging.info("Сегодня не воскресенье — пропускаю еженедельную сводку.")
            return

        logging.info("Начинаю еженедельную сводку...")
        greeting = get_motivational_greeting()
        weekly_currency_summary = get_weekly_currency_summary()
        weekly_crypto_summary = get_weekly_crypto_summary()
        investment_wisdom = get_investment_wisdom()

        weekly_message = f"""{greeting}

📊 *ЕЖЕНЕДЕЛЬНАЯ СВОДКА ПО РЫНКУ*

{weekly_currency_summary}

{weekly_crypto_summary}

{investment_wisdom}

Хорошего воскресенья! 😊"""

        logging.info("Отправляю еженедельную сводку...")
        await bot.send_message(chat_id=USER_CHAT_ID, text=weekly_message, parse_mode='Markdown')
        logging.info("Еженедельная сводка успешно отправлена")

    except Exception as e:
        logging.error(f"Ошибка при отправке сводки: {e}")
        try:
            await bot.send_message(chat_id=USER_CHAT_ID, text=f"❌ Ошибка: {e}")
        except Exception as send_error:
            logging.error(f"Не удалось отправить сообщение об ошибке: {send_error}")

# ============================
# ТОЧКА ВХОДА
# ============================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jerry Bot")
    parser.add_argument('--mode', type=str, default='morning', choices=['morning', 'weekly'])
    args = parser.parse_args()

    logging.info(f"Запуск Jerry в режиме: {args.mode}")

    if args.mode == 'morning':
        asyncio.run(send_morning_message())
    elif args.mode == 'weekly':
        asyncio.run(send_weekly_summary())
