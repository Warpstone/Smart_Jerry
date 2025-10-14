import requests
import logging
from datetime import datetime, timedelta
import time
import random

# === Базовые настройки ===
CURRENCY_API_URL = "https://api.frankfurter.app/"
CRYPTO_API_URL = "https://api.coincap.io/v2/assets"
HEADERS = {"User-Agent": "SmartJerryBot/1.0"}

# === Вспомогательная функция для повторных запросов ===
def _http_get_with_retries(url, params=None, max_retries=3, backoff=1.5):
    """HTTP-запрос с повторами при временных ошибках."""
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            return resp
        except Exception as e:
            logging.warning(f"Попытка {attempt + 1}/{max_retries} не удалась: {e}")
            if attempt < max_retries - 1:
                time.sleep(backoff * (attempt + 1))
    raise ConnectionError(f"Не удалось получить данные с {url}")

# === Анализ валют за сутки ===
def get_currency_analysis():
    """
    Анализ изменения курсов валют за последние сутки.
    Использует стабильный источник Frankfurter.app (данные ЕЦБ).
    """
    try:
        base = "USD"
        targets = ["USD", "RUB", "CNY"]

        # === 1. Получаем сегодняшние курсы ===
        resp_today = _http_get_with_retries(
            f"{CURRENCY_API_URL}latest",
            params={"from": base, "to": ",".join(targets)},
            max_retries=2,
            backoff=0.8,
        )
        today_data = resp_today.json()
        today_rates = today_data.get("rates", {})

        # === 2. Получаем вчерашние курсы ===
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        resp_yesterday = _http_get_with_retries(
            f"{CURRENCY_API_URL}{yesterday}",
            params={"from": base, "to": ",".join(targets)},
            max_retries=2,
            backoff=0.8,
        )
        yesterday_data = resp_yesterday.json()
        yesterday_rates = yesterday_data.get("rates", {})

        # === 3. Формируем анализ ===
        lines = []
        for code in targets:
            t_rate = today_rates.get(code)
            y_rate = yesterday_rates.get(code)
            if not t_rate or not y_rate:
                lines.append(f"{code}: данные временно недоступны")
                continue

            change_pct = ((t_rate - y_rate) / y_rate) * 100
            symbol = {"USD": "$", "RUB": "₽", "CNY": "¥"}.get(code, "")
            lines.append(f"{code} {symbol}: {change_pct:+.2f}%")

        result = "💱 *Анализ валют за сутки:*\n" + "\n".join(lines)
        logging.info(f"Анализ валют получен успешно ({yesterday} → {today_data.get('date')})")
        return result

    except Exception as e:
        logging.error(f"Ошибка get_currency_analysis: {e}")
        return f"💱 *Анализ валют:* Не удалось получить данные ({e})"

# === Анализ криптовалют ===
def get_crypto_analysis():
    """
    Безопасная версия анализа криптовалют.
    Использует надежное API CoinCap (без ограничений).
    Возвращает краткий отчёт или сообщение об ошибке.
    """
    try:
        # Словарь криптовалют: ID в CoinCap -> (название, символ)
        cryptos = {
            "bitcoin": ("BTC", "₿"),
            "ethereum": ("ETH", "Ξ"),
            "toncoin": ("TON", "💎")
        }
        
        prices = {}
        
        # Получаем цену каждой криптовалюты
        for crypto_id, (name, symbol) in cryptos.items():
            try:
                resp = _http_get_with_retries(
                    f"{CRYPTO_API_URL}/{crypto_id}",
                    max_retries=2,
                    backoff=0.5
                )
                data = resp.json()
                
                if "data" in data and "priceUsd" in data["data"]:
                    price_usd = float(data["data"]["priceUsd"])
                    prices[name] = (price_usd, symbol)
                else:
                    logging.warning(f"Нет данных для {crypto_id}")
                    
            except Exception as e:
                logging.warning(f"Ошибка получения {crypto_id}: {e}")
                continue
        
        if not prices:
            raise ValueError("Не удалось получить ни одной криптовалюты")
        
        # Формируем отчет
        lines = ["📈 *Анализ криптовалют (текущие цены):*"]
        
        if "BTC" in prices:
            btc_price, btc_symbol = prices["BTC"]
            lines.append(f"{btc_symbol} BTC: {btc_price:,.0f} USD")
            
        if "ETH" in prices:
            eth_price, eth_symbol = prices["ETH"]
            lines.append(f"{eth_symbol} ETH: {eth_price:,.0f} USD")
            
        if "TON" in prices:
            ton_price, ton_symbol = prices["TON"]
            lines.append(f"{ton_symbol} TON: {ton_price:,.2f} USD")
        
        logging.info("Анализ криптовалют получен успешно (CoinCap API)")
        return "\n".join(lines)

    except Exception as e:
        logging.error(f"Ошибка get_crypto_analysis: {e}")
        return (
            "📈 *Анализ криптовалют:*\n"
            f"Не удалось получить данные. Ошибка: {e}\n"
            "Проверь подключение или повтори позже."
        )

# === Проверка курса валют за неделю (дополнительная функция, опционально) ===
def get_weekly_currency_summary():
    """
    Возвращает краткий обзор изменения курса USD/EUR за неделю.
    """
    try:
        base = "EUR"
        target = "USD"
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)

        resp_today = _http_get_with_retries(f"{CURRENCY_API_URL}latest", params={"from": base, "to": target})
        resp_week = _http_get_with_retries(f"{CURRENCY_API_URL}{week_ago}", params={"from": base, "to": target})

        t_rate = resp_today.json().get("rates", {}).get(target)
        w_rate = resp_week.json().get("rates", {}).get(target)

        if not t_rate or not w_rate:
            raise ValueError("Не удалось получить курс за неделю")

        diff = ((t_rate - w_rate) / w_rate) * 100
        return f"📅 За неделю: EUR/USD изменился на {diff:+.2f}%"

    except Exception as e:
        logging.error(f"Ошибка get_weekly_currency_summary: {e}")
        return "Не удалось получить недельный анализ валют."
