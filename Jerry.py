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
    try:
        print(f"[{datetime.now()}] Начинаю формирование утреннего сообщения...")
        
        # Проверяем, воскресенье ли сегодня
        today = datetime.now()
        is_sunday = today.weekday() == 6  # 6 = воскресенье
        print(f"[{datetime.now()}] Сегодня {today.strftime('%A')} (weekday={today.weekday()}), is_sunday={is_sunday}")
        
        greeting = get_motivational_greeting()
        print(f"[{datetime.now()}] Получено приветствие")
        
        weather = get_weather()
        print(f"[{datetime.now()}] Получена погода")
        
        exchange_rates = get_exchange_rates()
        print(f"[{datetime.now()}] Получены курсы валют")
        
        currency_analysis = get_currency_analysis()
        print(f"[{datetime.now()}] Получен анализ валют")
        
        crypto_analysis = get_crypto_analysis()
        print(f"[{datetime.now()}] Получен анализ криптовалют")
        
        investment_wisdom = get_investment_wisdom()
        print(f"[{datetime.now()}] Получена инвестиционная мудрость")
        
        birthday_reminder = get_birthday_reminder()
        print(f"[{datetime.now()}] Проверены дни рождения")
        
        memorial_reminder = get_memorial_reminder()
        print(f"[{datetime.now()}] Проверены дни памяти")
        
        # Формируем полное сообщение
        full_message = f"""{greeting}

🌤️ {weather}

{exchange_rates}

{currency_analysis}

{crypto_analysis}

{investment_wisdom}"""
        
        # Добавляем книгу недели только по воскресеньям
        if is_sunday:
            try:
                print(f"[{datetime.now()}] Получаю книгу недели...")
                book_of_week = get_book_of_the_week_with_api()
                full_message += f"\n\n{book_of_week}"
                print(f"[{datetime.now()}] Книга недели получена")
            except Exception as e:
                print(f"[{datetime.now()}] Ошибка при получении книги недели: {e}")
                full_message += "\n\n📚 *Книга недели*\n\nК сожалению, сейчас нет доступных рекомендаций."
        
        # Добавляем напоминание о дне рождения, если есть
        if birthday_reminder:
            full_message += f"\n\n{birthday_reminder}"
        
        # Добавляем напоминание о дне памяти, если есть
        if memorial_reminder:
            full_message += f"\n\n{memorial_reminder}"
        
        full_message += "\n\nХорошего дня! 😊"
        
        # Используем асинхронный метод для отправки сообщения
        print(f"[{datetime.now()}] Отправляю сообщение...")
        import asyncio
        async def send_msg():
            return await bot.send_message(chat_id=USER_CHAT_ID, text=full_message, parse_mode='Markdown')
        asyncio.run(send_msg())
        print(f"[{datetime.now()}] Утреннее сообщение отправлено успешно")
        
    except Exception as e:
        error_message = f"❌ Ошибка при формировании утреннего сообщения: {e}"
        print(f"[{datetime.now()}] {error_message}")
        try:
            import asyncio
            async def send_error_msg():
                return await bot.send_message(chat_id=USER_CHAT_ID, text=error_message)
            asyncio.run(send_error_msg())
        except Exception as send_error:
            print(f"[{datetime.now()}] Критическая ошибка: не удалось отправить сообщение об ошибке: {send_error}")

def send_weekly_summary():
    """Отправляет еженедельную сводку по рынку валют и криптовалют"""
    try:
        print(f"[{datetime.now()}] Начинаю формирование еженедельной сводки...")
        
        greeting = get_motivational_greeting()
        print(f"[{datetime.now()}] Получено приветствие")
        
        weekly_currency_summary = get_weekly_currency_summary()
        print(f"[{datetime.now()}] Получена еженедельная сводка по валютам")
        
        weekly_crypto_summary = get_weekly_crypto_summary()
        print(f"[{datetime.now()}] Получена еженедельная сводка по криптовалютам")
        
        investment_wisdom = get_investment_wisdom()
        print(f"[{datetime.now()}] Получена инвестиционная мудрость")
        
        # Формируем еженедельное сообщение
        weekly_message = f"""{greeting}

📊 *ЕЖЕНЕДЕЛЬНАЯ СВОДКА ПО РЫНКУ*

{weekly_currency_summary}

{weekly_crypto_summary}

{investment_wisdom}

Хорошего воскресенья! 😊"""
        
        # Используем асинхронный метод для отправки сообщения
        print(f"[{datetime.now()}] Отправляю еженедельную сводку...")
        import asyncio
        async def send_weekly_msg():
            return await bot.send_message(chat_id=USER_CHAT_ID, text=weekly_message, parse_mode='Markdown')
        asyncio.run(send_weekly_msg())
        print(f"[{datetime.now()}] Еженедельная сводка отправлена")
        
    except Exception as e:
        error_message = f"❌ Ошибка при формировании еженедельной сводки: {e}"
        print(f"[{datetime.now()}] {error_message}")
        try:
            import asyncio
            async def send_error_msg():
                return await bot.send_message(chat_id=USER_CHAT_ID, text=error_message)
            asyncio.run(send_error_msg())
        except Exception as send_error:
            print(f"[{datetime.now()}] Критическая ошибка: не удалось отправить сообщение об ошибке: {send_error}")

# Планировщик задач
scheduler = BlockingScheduler(timezone="Europe/Moscow")

# Добавляем обработчики исключений для задач
def safe_send_morning_message():
    """Безопасная отправка утреннего сообщения с обработкой исключений"""
    try:
        print(f"[{datetime.now()}] ===== НАЧАЛО ОТПРАВКИ УТРЕННЕГО СООБЩЕНИЯ =====")
        send_morning_message()
        print(f"[{datetime.now()}] ===== УТРЕННЕЕ СООБЩЕНИЕ ОТПРАВЛЕНО УСПЕШНО =====")
    except Exception as e:
        print(f"[{datetime.now()}] КРИТИЧЕСКАЯ ОШИБКА в утреннем сообщении: {e}")
        try:
            import asyncio
            error_msg = f"❌ Критическая ошибка бота: {e}"
            async def send_critical_error():
                return await bot.send_message(chat_id=USER_CHAT_ID, text=error_msg)
            asyncio.run(send_critical_error())
            print(f"[{datetime.now()}] Сообщение об ошибке отправлено")
        except Exception as send_error:
            print(f"[{datetime.now()}] Не удалось отправить сообщение об ошибке: {send_error}")

def safe_send_weekly_summary():
    """Безопасная отправка еженедельной сводки с обработкой исключений"""
    try:
        send_weekly_summary()
    except Exception as e:
        print(f"[{datetime.now()}] Критическая ошибка в еженедельной сводке: {e}")
        try:
            import asyncio
            error_msg = f"❌ Критическая ошибка бота: {e}"
            async def send_critical_error():
                return await bot.send_message(chat_id=USER_CHAT_ID, text=error_msg)
            asyncio.run(send_critical_error())
        except:
            print(f"[{datetime.now()}] Не удалось отправить сообщение об ошибке")

# Планировщик задач
scheduler.add_job(safe_send_morning_message, 'cron', hour=9, minute=0)  # Ежедневно в 9:00
scheduler.add_job(safe_send_weekly_summary, 'cron', day_of_week=6, hour=10, minute=0)  # Воскресенье в 10:00

# Дополнительное логирование для диагностики
print(f"[{datetime.now()}] Планировщик настроен:")
print(f"[{datetime.now()}] - Ежедневные сообщения: каждый день в 09:00")
print(f"[{datetime.now()}] - Еженедельные сводки: воскресенье в 10:00")
print(f"[{datetime.now()}] - Текущий день недели: {datetime.now().strftime('%A')} (weekday={datetime.now().weekday()})")

print("✅ Умный Джери запущен и ждёт:")
print("   📅 Ежедневные сообщения в 9:00")
print("   📊 Еженедельные сводки по воскресеньям в 10:00")
print("   🛡️ Добавлена защита от зависаний")

try:
    scheduler.start()
except KeyboardInterrupt:
    print(f"[{datetime.now()}] Бот остановлен пользователем")
except Exception as e:
    print(f"[{datetime.now()}] Критическая ошибка планировщика: {e}")