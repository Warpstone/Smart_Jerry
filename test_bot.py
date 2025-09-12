# -*- coding: utf-8 -*-
# pylint: disable=non-ascii-bytes

from telegram import Bot
from datetime import datetime

# Импорт модулей
from weather_module import get_weather
from greetings_module import get_motivational_greeting
from exchange_module import get_exchange_rates, get_currency_analysis, get_crypto_analysis, get_weekly_currency_summary, get_weekly_crypto_summary
from birthday_module import get_birthday_reminder, get_all_birthdays
from memorial_module import get_memorial_reminder, get_all_memorials
from investment_module import get_investment_wisdom
from book_week_module import get_book_of_the_week, get_book_of_the_week_with_api, get_book_from_google_books, get_book_from_open_library, get_all_categories, get_books_count

# Конфигурация бота (используем те же данные)
TELEGRAM_TOKEN = '7627055581:AAHtAlEKgbjhQYid8I-bUBul6UKqjFQAxFo'
USER_CHAT_ID = '94476735'

# Инициализация бота
bot = Bot(token=TELEGRAM_TOKEN)

def test_all_modules():
    """Тестирует все модули отдельно"""
    print("🧪 Тестирование модулей...")
    print("=" * 50)
    
    # Тест приветствий
    print("1. Тест приветствий:")
    greeting = get_motivational_greeting()
    print(f"   {greeting}")
    print()
    
    # Тест погоды
    print("2. Тест погоды:")
    weather = get_weather()
    print(f"   {weather}")
    print()
    
    # Тест курсов валют (включая криптовалюты)
    print("3. Тест курсов валют:")
    exchange_rates = get_exchange_rates()
    print(f"   {exchange_rates}")
    print()
    
    # Тест дней рождения
    print("4. Тест дней рождения:")
    birthday_reminder = get_birthday_reminder()
    if birthday_reminder:
        print(f"   {birthday_reminder}")
    else:
        print("   Сегодня нет напоминаний о днях рождения (напоминания показываются за 3 дня и ближе)")
    print()
    
    # Тест дней памяти
    print("5. Тест дней памяти:")
    memorial_reminder = get_memorial_reminder()
    if memorial_reminder:
        print(f"   {memorial_reminder}")
    else:
        print("   Сегодня нет напоминаний о днях памяти (напоминания показываются за 3 дня и ближе)")
    print()
    
    # Тест инвестиционных мудростей
    print("6. Тест инвестиционных мудростей:")
    investment_wisdom = get_investment_wisdom()
    print(f"   {investment_wisdom}")
    print()
    
    # Тест анализа валют
    print("7. Тест анализа валют:")
    currency_analysis = get_currency_analysis()
    print(f"   {currency_analysis}")
    print()
    
    # Тест анализа криптовалют
    print("8. Тест анализа криптовалют:")
    crypto_analysis = get_crypto_analysis()
    print(f"   {crypto_analysis}")
    print()
    
    # Тест еженедельной сводки по валютам
    print("9. Тест еженедельной сводки по валютам:")
    weekly_currency = get_weekly_currency_summary()
    print(f"   {weekly_currency}")
    print()
    
    # Тест еженедельной сводки по криптовалютам
    print("10. Тест еженедельной сводки по криптовалютам:")
    weekly_crypto = get_weekly_crypto_summary()
    print(f"   {weekly_crypto}")
    print()
    
    # Тест книги недели
    print("11. Тест книги недели:")
    book_of_week = get_book_of_the_week_with_api()
    print(f"   {book_of_week}")
    print()
    
    
    print("=" * 50)
    print("✅ Все модули протестированы!")

def send_test_message():
    """Отправляет тестовое сообщение в Telegram"""
    print("📱 Отправка тестового сообщения...")
    
    greeting = get_motivational_greeting()
    weather = get_weather()
    exchange_rates = get_exchange_rates()
    currency_analysis = get_currency_analysis()
    crypto_analysis = get_crypto_analysis()
    investment_wisdom = get_investment_wisdom()
    
    # Формируем полное сообщение
    full_message = f"""{greeting}

🌤️ {weather}

{exchange_rates}

{currency_analysis}

{crypto_analysis}

{investment_wisdom}

Хорошего дня! 😊

🧪 Это тестовое сообщение от {datetime.now().strftime('%H:%M:%S')}"""
    
    try:
        # Используем синхронный метод для отправки сообщения
        import asyncio
        asyncio.run(bot.send_message(chat_id=USER_CHAT_ID, text=full_message, parse_mode='Markdown'))
        print("✅ Тестовое сообщение отправлено успешно!")
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")

def show_all_birthdays():
    """Показывает все дни рождения"""
    print("📅 Список всех дней рождения:")
    print("=" * 40)
    all_birthdays = get_all_birthdays()
    print(all_birthdays)

def show_all_memorials():
    """Показывает все дни памяти"""
    print("🕊️ Список всех дней памяти:")
    print("=" * 40)
    all_memorials = get_all_memorials()
    print(all_memorials)

def send_weekly_test_message():
    """Отправляет тестовую еженедельную сводку в Telegram"""
    print("📊 Отправка тестовой еженедельной сводки...")
    
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

Хорошего воскресенья! 😊

🧪 Это тестовая еженедельная сводка от {datetime.now().strftime('%H:%M:%S')}"""
    
    try:
        # Используем синхронный метод для отправки сообщения
        import asyncio
        asyncio.run(bot.send_message(chat_id=USER_CHAT_ID, text=weekly_message, parse_mode='Markdown'))
        print("✅ Тестовая еженедельная сводка отправлена успешно!")
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")

def show_books_info():
    """Показывает информацию о базе книг"""
    print("📚 Информация о базе книг:")
    print("=" * 40)
    categories = get_all_categories()
    total_books = get_books_count()
    
    print(f"📖 Всего книг в базе: {total_books}")
    print(f"📂 Категории ({len(categories)}):")
    for category in categories:
        print(f"   • {category.title()}")
    print()

def send_book_test_message():
    """Отправляет тестовое сообщение с книгой недели в Telegram"""
    print("📚 Отправка тестового сообщения с книгой недели...")
    
    greeting = get_motivational_greeting()
    book_of_week = get_book_of_the_week_with_api()  # Используем версию с API
    
    # Формируем сообщение с книгой недели
    book_message = f"""{greeting}

{book_of_week}

Хорошего дня! 😊

🧪 Это тестовое сообщение с книгой недели от {datetime.now().strftime('%H:%M:%S')}"""
    
    try:
        # Используем синхронный метод для отправки сообщения
        import asyncio
        asyncio.run(bot.send_message(chat_id=USER_CHAT_ID, text=book_message, parse_mode='Markdown'))
        print("✅ Тестовое сообщение с книгой недели отправлено успешно!")
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")

def main():
    """Главная функция для выбора действия"""
    print("🤖 Тестовый скрипт для бота-информатора")
    print("=" * 40)
    print("1. Тестировать модули (без отправки)")
    print("2. Отправить тестовое сообщение в Telegram")
    print("3. Отправить тестовую еженедельную сводку в Telegram")
    print("4. Отправить тестовое сообщение с книгой недели в Telegram")
    print("5. Показать все дни рождения")
    print("6. Показать все дни памяти")
    print("7. Показать информацию о базе книг")
    print("8. Выход")
    print("=" * 40)
    
    while True:
        choice = input("Выберите действие (1-8): ").strip()
        
        if choice == "1":
            test_all_modules()
            print()
        elif choice == "2":
            send_test_message()
            print()
        elif choice == "3":
            send_weekly_test_message()
            print()
        elif choice == "4":
            send_book_test_message()
            print()
        elif choice == "5":
            show_all_birthdays()
            print()
        elif choice == "6":
            show_all_memorials()
            print()
        elif choice == "7":
            show_books_info()
            print()
        elif choice == "8":
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
