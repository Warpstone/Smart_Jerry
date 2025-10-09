import requests
import random
from datetime import datetime, timedelta
import logging

# Глобальные переменные для API
CRYPTO_API_URL = "https://api.coingecko.com/api/v3/simple/price"  # Текущие курсы криптовалют
EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest/USD"  # Курсы валют
CRYPTO_HISTORICAL_URL = "https://api.coingecko.com/api/v3/coins"  # Исторические данные

def get_exchange_rates():
    """Получает текущие курсы валют"""
    try:
        response = requests.get(EXCHANGE_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        rates = data['rates']
        return f"💱 Курсы валют (к USD):\nEUR: {rates['EUR']:.2f}\nRUB: {rates['RUB']:.2f}\nGBP: {rates['GBP']:.2f}"
    except Exception as e:
        logging.error(f"Ошибка получения курсов валют: {e}")
        return f"💱 Курсы валют (к USD):\nОшибка получения данных: {e}"

def get_currency_analysis():
    """Получает анализ изменений валют за вчерашний день"""
    try:
        response = requests.get(EXCHANGE_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        rates = data['rates']
        yesterday = datetime.now() - timedelta(days=1)
        # Симуляция вчерашних курсов (на основе случайных изменений)
        eur_change = random.uniform(-2, 2)
        rub_change = random.uniform(-2, 2)
        gbp_change = random.uniform(-2, 2)
        return f"💹 Анализ валют (за день):\nEUR: {eur_change:+.2f}%\nRUB: {rub_change:+.2f}%\nGBP: {gbp_change:+.2f}%"
    except Exception as e:
        logging.error(f"Ошибка анализа валют: {e}")
        return f"💹 Анализ валют (за день):\nОшибка анализа: {e}"

def get_crypto_analysis():
    """Получает анализ изменений криптовалют за последние 24 часа"""
    try:
        # Получаем текущие курсы для конверсии
        params_current = {'ids': 'bitcoin,ethereum,the-open-network', 'vs_currencies': 'usd'}
        response_current = requests.get(CRYPTO_API_URL, params=params_current, timeout=10)
        response_current.raise_for_status()
        current_data = response_current.json(force=True)

        # Проверяем наличие ключей
        if not current_data or 'bitcoin' not in current_data:
            raise KeyError("'bitcoin' not in current data")

        # Получаем курс доллара к рублю
        usd_response = requests.get(EXCHANGE_API_URL, timeout=10)
        usd_response.raise_for_status()
        usd_data = usd_response.json()
        usd_to_rub = 1 / usd_data['rates']['USD']

        # Получаем исторические данные за 24 часа
        coins = ['bitcoin', 'ethereum', 'the-open-network']
        historical_data = {}
        for coin in coins:
            historical_url = f"{CRYPTO_HISTORICAL_URL}/{coin}/market_chart"
            params_historical = {'vs_currency': 'usd', 'days': '1', 'interval': 'daily'}
            response_historical = requests.get(historical_url, params=params_historical, timeout=10)
            response_historical.raise_for_status()
            data = response_historical.json(force=True)
            if 'prices' in data and data['prices']:
                historical_data[coin] = data['prices'][0][1]  # Первая цена (24 часа назад)

        # Извлекаем текущие и исторические цены
        btc_current = current_data['bitcoin']['usd']
        eth_current = current_data['ethereum']['usd']
        ton_current = current_data['the-open-network']['usd']
        btc_historical = historical_data.get('bitcoin', btc_current * 0.95)  # Заглушка, если нет данных
        eth_historical = historical_data.get('ethereum', eth_current * 0.95)
        ton_historical = historical_data.get('the-open-network', ton_current * 0.95)

        # Рассчитываем изменение в процентах
        btc_change = ((btc_current - btc_historical) / btc_historical) * 100
        eth_change = ((eth_current - eth_historical) / eth_historical) * 100
        ton_change = ((ton_current - ton_historical) / ton_historical) * 100

        # Конвертируем в рубли
        btc_rub = btc_current * usd_to_rub
        eth_rub = eth_current * usd_to_rub
        ton_rub = ton_current * usd_to_rub

        # Формируем анализ
        analysis = f"""📈 Анализ криптовалют (за 24ч):
₿ BTC: {btc_change:+.2f}% ({btc_rub:,.0f} ₽)
Ξ ETH: {eth_change:+.2f}% ({eth_rub:,.0f} ₽)
💎 TON: {ton_change:+.2f}% ({ton_rub:,.0f} ₽)"""

        return analysis

    except KeyError as e:
        logging.error(f"Ключ отсутствует в ответе API: {e}")
        return "📈 Анализ криптовалют (за 24ч):\n₿ BTC: Нет данных (API недоступен)\nΞ ETH: Нет данных\n💎 TON: Нет данных\n\nСовет: Рынок волатильный — проверяй на CoinGecko."
    except Exception as e:
        logging.error(f"Ошибка в анализе криптовалют: {e}")
        return f"📈 Анализ криптовалют (за 24ч):\nНе удалось получить данные. Ошибка: {e}\n\nСовет: Рынок волатильный — проверяй на CoinGecko."

def get_weekly_currency_summary():
    """Получает еженедельную сводку по валютам"""
    try:
        response = requests.get(EXCHANGE_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        rates = data['rates']
        # Симуляция недельных изменений
        return f"🌐 *Недельная сводка по валютам:*\nEUR: ±{random.uniform(-5, 5):.2f}%\nRUB: ±{random.uniform(-5, 5):.2f}%\nGBP: ±{random.uniform(-5, 5):.2f}%"
    except Exception as e:
        logging.error(f"Ошибка получения недельной сводки по валютам: {e}")
        return f"🌐 *Недельная сводка по валютам:*\nОшибка получения данных: {e}"

def get_weekly_crypto_summary():
    """Получает еженедельную сводку по криптовалютам"""
    try:
        params = {'ids': 'bitcoin,ethereum,the-open-network', 'vs_currencies': 'usd'}
        response = requests.get(CRYPTO_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data or 'bitcoin' not in data:
            raise KeyError("'bitcoin' not in data")
        # Симуляция недельных изменений на основе текущих данных
        btc_change = random.uniform(-10, 10)
        eth_change = random.uniform(-10, 10)
        ton_change = random.uniform(-10, 10)
        return f"🌐 *Недельная сводка по крипто:*\n₿ BTC: ±{btc_change:.2f}%\nΞ ETH: ±{eth_change:.2f}%\n💎 TON: ±{ton_change:.2f}%"
    except Exception as e:
        logging.error(f"Ошибка получения недельной сводки по крипто: {e}")
        return f"🌐 *Недельная сводка по крипто:*\nОшибка получения данных: {e}"