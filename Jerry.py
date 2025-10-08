# -*- coding: utf-8 -*-
# pylint: disable=non-ascii-bytes

import os
import argparse
import logging
import asyncio
from datetime import datetime
from telegram.ext import Application

# Импорт модулей
from weather_module import get_weather
from greetings_module import get_motivational_greeting
from exchange_module import get_exchange_rates, get_currency_analysis, get_crypto_analysis, get_weekly_currency_summary, get_weekly_crypto_summary
from birthday_module import get_birthday_reminder
from memorial_module import get_memorial_reminder
from investment_module import get_investment_wisdom
from book_week_module import get_book_of_the_week_with_api

# Конфигурация
TELEGRAM_TOKEN = '7627055581:AAHtAlEKgbjhQYid8I-bUBul6UKqjFQAxFo'
USER_CHAT_ID = '94476735'

# Логирование
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(script_dir, 'bot.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='[%(asctime)s] %(message)s')

# Инициализация приложения
application = Application.builder().token(TELEGRAM_TOKEN).build()

async def send_morning_message(update=None, context=None):
    try:
        logging.info("Начинаю утреннее сообщение...")
        today = datetime.now()
        is_sunday = today.weekday() == 6

        greeting = get_motivational_greeting()
        weather = get_weather()
        exchange_rates = get_exchange_rates()
        currency_analysis = get_currency_analysis()
        crypto_analysis = get_crypto_analysis()
        investment_wisdom = get_investment_wisdom()
        birthday_reminder = get_birthday_reminder()
        memorial_reminder = get_memorial_reminder()

        full_message = f"""{greeting}

🌤️ {weather}

{exchange_rates}

{currency_analysis}

{crypto_analysis}

{investment_wisdom}"""

        if is_sunday:
            book_of_week = get_book_of_the_week_with_api()
            full_message += f"\n\n{book_of_week}"

        if birthday_reminder:
            full_message += f"\n\n{birthday_reminder}"

        if memorial_reminder:
            full_message += f"\n\n{memorial_reminder}"

        full_message += "\n\nХорошего дня! 😊"

        logging.info("Отправляю сообщение...")
        await context.bot.send_message(chat_id=USER_CHAT_ID, text=full_message, parse_mode='Markdown')
        logging.info("Сообщение отправлено")

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await context.bot.send_message(chat_id=USER_CHAT_ID, text=f"❌ Ошибка: {e}")

async def send_weekly_summary(update=None, context=None):
    try:
        today = datetime.now()
        if today.weekday() != 6:
            logging.info("Не воскресенье — пропускаю")
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

        logging.info("Отправляю сводку...")
        await context.bot.send_message(chat_id=USER_CHAT_ID, text=weekly_message, parse_mode='Markdown')
        logging.info("Сводка отправлена")

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await context.bot.send_message(chat_id=USER_CHAT_ID, text=f"❌ Ошибка: {e}")

if __name__ == "__main__":
    os.chdir(script_dir)
    
    parser = argparse.ArgumentParser(description="Jerry Bot")
    parser.add_argument('--mode', type=str, default='morning', choices=['morning', 'weekly'])
    args = parser.parse_args()
    
    logging.info(f"Запуск в режиме: {args.mode}")

    async def main():
        if args.mode == 'morning':
            await send_morning_message()
        elif args.mode == 'weekly':
            await send_weekly_summary()

    asyncio.run(main())