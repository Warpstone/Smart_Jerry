# -*- coding: utf-8 -*- 
# pylint: disable=non-ascii-bytes

from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import traceback

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

def log_with_timestamp(message):
    """Логирует сообщение с временной меткой"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def send_debug_message(message):
    """Отправляет отладочное сообщение в Telegram"""
    try:
        import asyncio
        debug_msg = f"🐛 DEBUG: {message}"
        asyncio.run(bot.send_message(chat_id=USER_CHAT_ID, text=debug_msg))
        log_with_timestamp(f"Отладочное сообщение отправлено: {message}")
    except Exception as e:
        log_with_timestamp(f"Не удалось отправить отладочное сообщение: {e}")

def send_morning_message():
    """Отправляет утреннее информационное сообщение в Telegram"""
    start_time = datetime.now()
    log_with_timestamp("=" * 60)
    log_with_timestamp("НАЧАЛО ОТПРАВКИ УТРЕННЕГО СООБЩЕНИЯ")
    log_with_timestamp("=" * 60)
    
    try:
        # Проверяем, воскресенье ли сегодня
        today = datetime.now()
        is_sunday = today.weekday() == 6  # 6 = воскресенье
        log_with_timestamp(f"Сегодня {today.strftime('%A')} (weekday={today.weekday()}), is_sunday={is_sunday}")
        
        # Отправляем отладочное сообщение о начале работы
        send_debug_message(f"Начинаю формирование утреннего сообщения. День недели: {today.strftime('%A')}")
        
        greeting = get_motivational_greeting()
        log_with_timestamp("✅ Получено приветствие")
        
        weather = get_weather()
        log_with_timestamp("✅ Получена погода")
        
        exchange_rates = get_exchange_rates()
        log_with_timestamp("✅ Получены курсы валют")
        
        currency_analysis = get_currency_analysis()
        log_with_timestamp("✅ Получен анализ валют")
        
        crypto_analysis = get_crypto_analysis()
        log_with_timestamp("✅ Получен анализ криптовалют")
        
        investment_wisdom = get_investment_wisdom()
        log_with_timestamp("✅ Получена инвестиционная мудрость")
        
        birthday_reminder = get_birthday_reminder()
        log_with_timestamp("✅ Проверены дни рождения")
        
        memorial_reminder = get_memorial_reminder()
        log_with_timestamp("✅ Проверены дни памяти")
        
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
                log_with_timestamp("📚 Получаю книгу недели...")
                book_of_week = get_book_of_the_week_with_api()
                full_message += f"\n\n{book_of_week}"
                log_with_timestamp("✅ Книга недели получена")
            except Exception as e:
                log_with_timestamp(f"❌ Ошибка при получении книги недели: {e}")
                full_message += "\n\n📚 *Книга недели*\n\nК сожалению, сейчас нет доступных рекомендаций."
        
        # Добавляем напоминание о дне рождения, если есть
        if birthday_reminder:
            full_message += f"\n\n{birthday_reminder}"
            log_with_timestamp(f"✅ Добавлено напоминание о дне рождения: {birthday_reminder}")
        
        # Добавляем напоминание о дне памяти, если есть
        if memorial_reminder:
            full_message += f"\n\n{memorial_reminder}"
            log_with_timestamp(f"✅ Добавлено напоминание о дне памяти: {memorial_reminder}")
        
        full_message += "\n\nХорошего дня! 😊"
        
        # Отправляем сообщение
        log_with_timestamp("📤 Отправляю сообщение в Telegram...")
        import asyncio
        asyncio.run(bot.send_message(chat_id=USER_CHAT_ID, text=full_message, parse_mode='Markdown'))
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        log_with_timestamp("✅ УТРЕННЕЕ СООБЩЕНИЕ ОТПРАВЛЕНО УСПЕШНО")
        log_with_timestamp(f"⏱️ Время выполнения: {duration:.2f} секунд")
        log_with_timestamp("=" * 60)
        
        # Отправляем отладочное сообщение об успехе
        send_debug_message(f"Утреннее сообщение отправлено успешно за {duration:.2f}с")
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        error_message = f"❌ Ошибка при формировании утреннего сообщения: {e}"
        log_with_timestamp(error_message)
        log_with_timestamp(f"⏱️ Время до ошибки: {duration:.2f} секунд")
        log_with_timestamp(f"Трассировка: {traceback.format_exc()}")
        
        try:
            import asyncio
            error_msg = f"❌ Ошибка бота: {e}\n⏱️ Время до ошибки: {duration:.2f}с"
            asyncio.run(bot.send_message(chat_id=USER_CHAT_ID, text=error_msg))
            log_with_timestamp("✅ Сообщение об ошибке отправлено")
        except Exception as send_error:
            log_with_timestamp(f"❌ Критическая ошибка: не удалось отправить сообщение об ошибке: {send_error}")

def send_weekly_summary():
    """Отправляет еженедельную сводку по рынку валют и криптовалют"""
    start_time = datetime.now()
    log_with_timestamp("=" * 60)
    log_with_timestamp("НАЧАЛО ОТПРАВКИ ЕЖЕНЕДЕЛЬНОЙ СВОДКИ")
    log_with_timestamp("=" * 60)
    
    try:
        today = datetime.now()
        log_with_timestamp(f"Сегодня {today.strftime('%A')} (weekday={today.weekday()})")
        
        # Отправляем отладочное сообщение о начале работы
        send_debug_message(f"Начинаю формирование еженедельной сводки. День недели: {today.strftime('%A')}")
        
        greeting = get_motivational_greeting()
        log_with_timestamp("✅ Получено приветствие")
        
        weekly_currency_summary = get_weekly_currency_summary()
        log_with_timestamp("✅ Получена еженедельная сводка по валютам")
        
        weekly_crypto_summary = get_weekly_crypto_summary()
        log_with_timestamp("✅ Получена еженедельная сводка по криптовалютам")
        
        investment_wisdom = get_investment_wisdom()
        log_with_timestamp("✅ Получена инвестиционная мудрость")
        
        # Формируем еженедельное сообщение
        weekly_message = f"""{greeting}

📊 *ЕЖЕНЕДЕЛЬНАЯ СВОДКА ПО РЫНКУ*

{weekly_currency_summary}

{weekly_crypto_summary}

{investment_wisdom}

Хорошего воскресенья! 😊"""
        
        # Отправляем сообщение
        log_with_timestamp("📤 Отправляю еженедельную сводку...")
        import asyncio
        asyncio.run(bot.send_message(chat_id=USER_CHAT_ID, text=weekly_message, parse_mode='Markdown'))
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        log_with_timestamp("✅ ЕЖЕНЕДЕЛЬНАЯ СВОДКА ОТПРАВЛЕНА УСПЕШНО")
        log_with_timestamp(f"⏱️ Время выполнения: {duration:.2f} секунд")
        log_with_timestamp("=" * 60)
        
        # Отправляем отладочное сообщение об успехе
        send_debug_message(f"Еженедельная сводка отправлена успешно за {duration:.2f}с")
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        error_message = f"❌ Ошибка при формировании еженедельной сводки: {e}"
        log_with_timestamp(error_message)
        log_with_timestamp(f"⏱️ Время до ошибки: {duration:.2f} секунд")
        log_with_timestamp(f"Трассировка: {traceback.format_exc()}")
        
        try:
            import asyncio
            error_msg = f"❌ Ошибка еженедельной сводки: {e}\n⏱️ Время до ошибки: {duration:.2f}с"
            asyncio.run(bot.send_message(chat_id=USER_CHAT_ID, text=error_msg))
            log_with_timestamp("✅ Сообщение об ошибке отправлено")
        except Exception as send_error:
            log_with_timestamp(f"❌ Критическая ошибка: не удалось отправить сообщение об ошибке: {send_error}")

# Планировщик задач
scheduler = BlockingScheduler(timezone="Europe/Moscow")

# Добавляем обработчики исключений для задач
def safe_send_morning_message():
    """Безопасная отправка утреннего сообщения с обработкой исключений"""
    try:
        send_morning_message()
    except Exception as e:
        log_with_timestamp(f"КРИТИЧЕСКАЯ ОШИБКА в утреннем сообщении: {e}")
        log_with_timestamp(f"Трассировка: {traceback.format_exc()}")
        try:
            import asyncio
            error_msg = f"❌ Критическая ошибка бота: {e}"
            asyncio.run(bot.send_message(chat_id=USER_CHAT_ID, text=error_msg))
        except:
            log_with_timestamp("Не удалось отправить сообщение об ошибке")

def safe_send_weekly_summary():
    """Безопасная отправка еженедельной сводки с обработкой исключений"""
    try:
        send_weekly_summary()
    except Exception as e:
        log_with_timestamp(f"КРИТИЧЕСКАЯ ОШИБКА в еженедельной сводке: {e}")
        log_with_timestamp(f"Трассировка: {traceback.format_exc()}")
        try:
            import asyncio
            error_msg = f"❌ Критическая ошибка бота: {e}"
            asyncio.run(bot.send_message(chat_id=USER_CHAT_ID, text=error_msg))
        except:
            log_with_timestamp("Не удалось отправить сообщение об ошибке")

# Планировщик задач
scheduler.add_job(safe_send_morning_message, 'cron', hour=9, minute=0)  # Ежедневно в 9:00
scheduler.add_job(safe_send_weekly_summary, 'cron', day_of_week=6, hour=10, minute=0)  # Воскресенье в 10:00

log_with_timestamp("✅ Умный Джери запущен и ждёт:")
log_with_timestamp("   📅 Ежедневные сообщения в 9:00")
log_with_timestamp("   📊 Еженедельные сводки по воскресеньям в 10:00")
log_with_timestamp("   🛡️ Добавлена защита от зависаний")
log_with_timestamp("   🐛 Добавлено подробное логирование")

# Отправляем сообщение о запуске
try:
    send_debug_message("Бот запущен в режиме отладки")
except:
    pass

try:
    scheduler.start()
except KeyboardInterrupt:
    log_with_timestamp("Бот остановлен пользователем")
except Exception as e:
    log_with_timestamp(f"Критическая ошибка планировщика: {e}")
    log_with_timestamp(f"Трассировка: {traceback.format_exc()}")
