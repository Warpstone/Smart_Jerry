# -*- coding: utf-8 -*-
# pylint: disable=non-ascii-bytes

import os
import sys
import argparse
import logging
from datetime import datetime
from telegram.ext import Application, ContextTypes  # Для асинхронного API
import asyncio

# Импорт модулей (предполагаю, они в той же папке или импортируемы)
from weather_module import get_weather
from greetings_module import get_motivational_greeting
from exchange_module import get_exchange_rates, get_currency_analysis, get_crypto_analysis, get_weekly_currency_summary, get_weekly_crypto_summary
from birthday_module import get_birthday_reminder
from memorial_module import get_memorial_reminder
from investment_module import get_investment_wisdom
from book_week_module import get_book_of_the_week_with_api

# Конфигурация бота
# Конфигурация бота
TELEGRAM_TOKEN = '7627055581:AAHtAlEKgbjhQYid8I-bUBul6UKqjFQAxFo'
USER_CHAT_ID = '94476735'

# Инициализация приложения (замена Bot)
application = Application.builder().token(TELEGRAM_TOKEN).build()

async def send_morning_message(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет утреннее информационное сообщение в Telegram"""
    try:
        logging.info("Начинаю формирование утреннего сообщения...")
        print("Начинаю формирование утреннего сообщения...")

        today = datetime.now()
        is_sunday = today.weekday() == 6
        logging.info(f"Сегодня {today.strftime('%A')} (weekday={today.weekday()}), is_sunday={is_sunday}")

        greeting = get_motivational_greeting()
        logging.info("Получено приветствие")

        weather = get_weather()
        logging.info("Получена погода")

        exchange_rates = get_exchange_rates()
        logging.info("Получены курсы валют")

        currency_analysis = get_currency_analysis()
        logging.info("Получен анализ валют")

        crypto_analysis = get_crypto_analysis()
        logging.info("Получен анализ криптовалют")

        investment_wisdom = get_investment_wisdom()
        logging.info("Получена инвестиционная мудрость")

        birthday_reminder = get_birthday_reminder()
        logging.info("Проверены дни рождения")

        memorial_reminder = get_memorial_reminder()
        logging.info("Проверены дни памяти")

        full_message = f"""{greeting}

🌤️ {weather}

{exchange_rates}

{currency_analysis}

{crypto_analysis}

{investment_wisdom}"""
        
        # Добавляем книгу недели только по воскресеньям
        if is_sunday:
            try:
                logging.info("Получаю книгу недели...")
                book_of_week = get_book_of_the_week_with_api()
                full_message += f"\n\n{book_of_week}"
                logging.info("Книга недели получена")
            except Exception as e:
                logging.error(f"Ошибка при получении книги недели: {e}")
                full_message += "\n\n📚 *Книга недели*\n\nК сожалению, сейчас нет доступных рекомендаций."
        
        # Добавляем напоминание о дне рождения, если есть
        if birthday_reminder:
            full_message += f"\n\n{birthday_reminder}"
        
        # Добавляем напоминание о дне памяти, если есть
        if memorial_reminder:
            full_message += f"\n\n{memorial_reminder}"
        
        full_message += "\n\nХорошего дня! 😊"
        
        # Отправка сообщения асинхронно
        logging.info("Отправляю сообщение...")
        async def send_msg():
            await bot.send_message(chat_id=USER_CHAT_ID, text=full_message, parse_mode='Markdown')
        asyncio.run(send_msg())
        logging.info("Утреннее сообщение отправлено успешно")
        
    except Exception as e:
        error_message = f"❌ Ошибка при формировании утреннего сообщения: {e}"
        logging.error(error_message)
        try:
            async def send_error_msg():
                await bot.send_message(chat_id=USER_CHAT_ID, text=error_message)
            asyncio.run(send_error_msg())
        except Exception as send_error:
            logging.error(f"Не удалось отправить сообщение об ошибке: {send_error}")

def send_weekly_summary():
    """Отправляет еженедельную сводку по рынку валют и криптовалют"""
    try:
        # Проверяем, воскресенье ли (если task запускается ежедневно)
        today = datetime.now()
        if today.weekday() != 6:  # Не воскресенье — выходим
            logging.info("Сегодня не воскресенье — пропускаем еженедельную сводку")
            return
        
        logging.info("Начинаю формирование еженедельной сводки...")
        
        greeting = get_motivational_greeting()
        logging.info("Получено приветствие")
        
        weekly_currency_summary = get_weekly_currency_summary()
        logging.info("Получена еженедельная сводка по валютам")
        
        weekly_crypto_summary = get_weekly_crypto_summary()
        logging.info("Получена еженедельная сводка по криптовалютам")
        
        investment_wisdom = get_investment_wisdom()
        logging.info("Получена инвестиционная мудрость")
        
        # Формируем еженедельное сообщение
        weekly_message = f"""{greeting}

📊 *ЕЖЕНЕДЕЛЬНАЯ СВОДКА ПО РЫНКУ*

{weekly_currency_summary}

{weekly_crypto_summary}

{investment_wisdom}

Хорошего воскресенья! 😊"""
        
        # Отправка
        logging.info("Отправляю еженедельную сводку...")
        async def send_weekly_msg():
            await bot.send_message(chat_id=USER_CHAT_ID, text=weekly_message, parse_mode='Markdown')
        asyncio.run(send_weekly_msg())
        logging.info("Еженедельная сводка отправлена")
        
    except Exception as e:
        error_message = f"❌ Ошибка при формировании еженедельной сводки: {e}"
        logging.error(error_message)
        try:
            async def send_error_msg():
                await bot.send_message(chat_id=USER_CHAT_ID, text=error_message)
            asyncio.run(send_error_msg())
        except Exception as send_error:
            logging.error(f"Не удалось отправить сообщение об ошибке: {send_error}")

if __name__ == "__main__":
    # Меняем working directory на папку скрипта (фикс PA)
    os.chdir(script_dir)
    
    parser = argparse.ArgumentParser(description="Запуск бота Jerry")
    parser.add_argument('--mode', type=str, default='morning', choices=['morning', 'weekly'], help="Режим: morning или weekly")
    args = parser.parse_args()
    
    logging.info(f"Запуск скрипта в режиме: {args.mode}")
    
    if args.mode == 'morning':
        send_morning_message()
    elif args.mode == 'weekly':
        send_weekly_summary()