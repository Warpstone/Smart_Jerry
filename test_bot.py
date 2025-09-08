# -*- coding: utf-8 -*-
# pylint: disable=non-ascii-bytes

from telegram import Bot
from datetime import datetime

# Импорт модулей
from weather_module import get_weather
from greetings_module import get_motivational_greeting
from exchange_module import get_exchange_rates

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
    
    print("=" * 50)
    print("✅ Все модули протестированы!")

def send_test_message():
    """Отправляет тестовое сообщение в Telegram"""
    print("📱 Отправка тестового сообщения...")
    
    greeting = get_motivational_greeting()
    weather = get_weather()
    exchange_rates = get_exchange_rates()
    
    # Формируем полное сообщение
    full_message = f"""{greeting}

🌤️ {weather}

{exchange_rates}

Хорошего дня! 😊

🧪 Это тестовое сообщение от {datetime.now().strftime('%H:%M:%S')}"""
    
    try:
        bot.send_message(chat_id=USER_CHAT_ID, text=full_message)
        print("✅ Тестовое сообщение отправлено успешно!")
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")

def main():
    """Главная функция для выбора действия"""
    print("🤖 Тестовый скрипт для бота-информатора")
    print("=" * 40)
    print("1. Тестировать модули (без отправки)")
    print("2. Отправить тестовое сообщение в Telegram")
    print("3. Выход")
    print("=" * 40)
    
    while True:
        choice = input("Выберите действие (1-3): ").strip()
        
        if choice == "1":
            test_all_modules()
            print()
        elif choice == "2":
            send_test_message()
            print()
        elif choice == "3":
            print("👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
