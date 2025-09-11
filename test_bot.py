# -*- coding: utf-8 -*-
# pylint: disable=non-ascii-bytes

from telegram import Bot
from datetime import datetime

# Импорт модулей
from weather_module import get_weather
from greetings_module import get_motivational_greeting
from exchange_module import get_exchange_rates
from birthday_module import get_birthday_reminder, get_all_birthdays
from memorial_module import get_memorial_reminder, get_all_memorials
from investment_module import get_investment_wisdom

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
    
    print("=" * 50)
    print("✅ Все модули протестированы!")

def send_test_message():
    """Отправляет тестовое сообщение в Telegram"""
    print("📱 Отправка тестового сообщения...")
    
    greeting = get_motivational_greeting()
    weather = get_weather()
    exchange_rates = get_exchange_rates()
    investment_wisdom = get_investment_wisdom()
    
    # Формируем полное сообщение
    full_message = f"""{greeting}

🌤️ {weather}

{exchange_rates}

{investment_wisdom}

Хорошего дня! 😊

🧪 Это тестовое сообщение от {datetime.now().strftime('%H:%M:%S')}"""
    
    try:
        # Используем синхронный метод для отправки сообщения
        import asyncio
        asyncio.run(bot.send_message(chat_id=USER_CHAT_ID, text=full_message))
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

def main():
    """Главная функция для выбора действия"""
    print("🤖 Тестовый скрипт для бота-информатора")
    print("=" * 40)
    print("1. Тестировать модули (без отправки)")
    print("2. Отправить тестовое сообщение в Telegram")
    print("3. Показать все дни рождения")
    print("4. Показать все дни памяти")
    print("5. Выход")
    print("=" * 40)
    
    while True:
        choice = input("Выберите действие (1-5): ").strip()
        
        if choice == "1":
            test_all_modules()
            print()
        elif choice == "2":
            send_test_message()
            print()
        elif choice == "3":
            show_all_birthdays()
            print()
        elif choice == "4":
            show_all_memorials()
            print()
        elif choice == "5":
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
