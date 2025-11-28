import requests
import logging
from datetime import datetime, timedelta
import time
import random

# === Базовые настройки ===
# API Центрального Банка РФ
CURRENCY_API_URL = "https://www.cbr-xml-daily.ru/"
CRYPTO_API_URL = "https://api.coincap.io/v2/assets"
HEADERS = {"User-Agent": "SmartJerryBot/1.0"}


# === Вспомогательная функция для повторных запросов ===
def _get_historical_cbr_rates(date: datetime):
    """
    Получает курсы ЦБ РФ на заданную дату.
    (Убрана лишняя "_" из имени функции для лучшего стиля).
    """
    # Правильный формат даты для архива ЦБ РФ: YYYY/MM/DD
    date_str = date.strftime("%Y/%m/%d")
    # Формат архива: https://www.cbr-xml-daily.ru/archive/YYYY/MM/DD/daily_json.js
    url = f"{CURRENCY_API_URL}archive/{date_str}/daily_json.js"
    try:
        resp = _http_get_with_retries(url, max_retries=2, backoff=0.8)
        # Если данные получены, возвращаем только секцию Valute
        return resp.json().get("Valute", {})
    except Exception as e:
        logging.error(f"Ошибка получения исторических данных ЦБ за {date_str}: {e}")
        return {}


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
    Использует API Центрального Банка РФ.
    """
    try:
        # CBR API: https://www.cbr-xml-daily.ru/daily_json.js
        resp = _http_get_with_retries(f"{CURRENCY_API_URL}daily_json.js",
                                      max_retries=2,
                                      backoff=0.8,
                                      )
        data = resp.json()
        valutes = data.get("Valute", {})

        # Валюты для отчета
        currency_codes = ["USD", "EUR", "CNY"]
        lines = ["💱 Изменение курсов ЦБ РФ за сутки (к RUB):"]

        for code in currency_codes:
            valute_data = valutes.get(code)
            if not valute_data:
                continue

            # === ЛОГИКА ПЕРЕМЕЩЕНА ВНУТРЬ ЦИКЛА ===
            nominal = valute_data.get("Nominal", 1)
            current_rate = valute_data.get("Value", 0)
            previous_rate = valute_data.get("Previous", 0)

            # Пересчет на 1 единицу валюты (для CNY nominal=10)
            rate_today = current_rate / nominal
            rate_yesterday = previous_rate / nominal

            if rate_yesterday > 0:
                # Расчет изменения в %
                change_pct = ((rate_today - rate_yesterday) / rate_yesterday) * 100
                symbol = {"USD": "$", "EUR": "€", "CNY": "¥"}.get(code, "")

                lines.append(f"{code} {symbol} ({rate_today:.2f} RUB): {change_pct:+.2f}%")
            else:
                lines.append(f"{code}: нет предыдущих данных")
            # === КОНЕЦ ЛОГИКИ ВНУТРИ ЦИКЛА ===

        logging.info("Анализ валют ЦБ РФ получен успешно.")
        return "\n".join(lines)

    except Exception as e:
        logging.error(f"Ошибка get_currency_analysis (CBR): {e}")
        return f"💱 Анализ валют: Не удалось получить данные ЦБ РФ ({e})"


# === Анализ криптовалют (оставлено без изменений) ===
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
            "toncoin": ("toncoin", "💎")
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
        lines = ["📈 Анализ криптовалют (текущие цены):"]

        if "BTC" in prices:
            btc_price, btc_symbol = prices["BTC"]
            lines.append(f"{btc_symbol} BTC: {btc_price:,.0f} USD")

        if "ETH" in prices:
            eth_price, eth_symbol = prices["ETH"]
            lines.append(f"{eth_symbol} ETH: {eth_price:,.0f} USD")

        if "toncoin" in prices:
            ton_price, ton_symbol = prices["toncoin"]
            lines.append(f"{ton_symbol} TON: {ton_price:,.2f} USD")

        logging.info("Анализ криптовалют получен успешно (CoinCap API)")
        return "\n".join(lines)

    except Exception as e:
        logging.error(f"Ошибка get_crypto_analysis: {e}")
        return (
            "📈 Анализ криптовалют:\n"
            f"Не удалось получить данные. Ошибка: {e}\n"
            "Проверь подключение или повтори позже."
        )


# === Текущие курсы валют ===
def get_exchange_rates():
    """Возвращает актуальные курсы валют ЦБ РФ."""
    try:
        # CBR API: https://www.cbr-xml-daily.ru/daily_json.js
        resp = _http_get_with_retries(
            f"{CURRENCY_API_URL}daily_json.js",
            max_retries=2,
            backoff=0.8
        )
        data = resp.json()
        valutes = data.get("Valute", {})

        lines = ["💵 Курсы валют ЦБ РФ (к RUB):"]

        currency_codes = ["USD", "EUR", "CNY"]

        for code in currency_codes:
            valute_data = valutes.get(code)
            if not valute_data:
                continue

            nominal = valute_data.get("Nominal", 1)
            current_rate = valute_data.get("Value", 0)

            # Курс за 1 единицу
            rate_per_one = current_rate / nominal
            symbol = {"USD": "$", "EUR": "€", "CNY": "¥"}.get(code, "")
            lines.append(f"{symbol} {code}: {rate_per_one:.2f}")

        logging.info("Курсы валют ЦБ РФ получены успешно")
        return "\n".join(lines)

    except Exception as e:
        logging.error(f"Ошибка get_exchange_rates (CBR): {e}")
        return f"💵 Курсы валют: Не удалось получить данные ЦБ РФ ({e})"


# === Проверка курса валют за неделю ===
def get_weekly_currency_summary():
    """
    Возвращает краткий обзор изменения курсов USD/EUR за неделю (ЦБ РФ).
    """
    try:
        today = datetime.now()
        week_ago = today - timedelta(days=7)

        # 1. Получаем курсы сегодня
        resp_today = _http_get_with_retries(f"{CURRENCY_API_URL}daily_json.js")
        t_valutes = resp_today.json().get("Valute", {})

        # 2. Получаем курсы неделю назад (через архив)
        w_valutes = _get_historical_cbr_rates(week_ago)

        lines = ["📅 Изменения курсов ЦБ РФ за 7 дней (к RUB):"]
        currency_codes = ["USD", "EUR"]

        for code in currency_codes:
            t_data = t_valutes.get(code)
            w_data = w_valutes.get(code)

            if not t_data or not w_data:
                lines.append(f"{code}: исторические данные недоступны")
                continue

            # Сегодня
            t_nominal = t_data.get("Nominal", 1)
            t_rate = t_data.get("Value", 0) / t_nominal

            # Неделю назад
            w_nominal = w_data.get("Nominal", 1)
            w_rate = w_data.get("Value", 0) / w_nominal

            if w_rate > 0:
                diff_pct = ((t_rate - w_rate) / w_rate) * 100
                symbol = {"USD": "$", "EUR": "€"}.get(code, "")
                lines.append(f"{code} {symbol} ({t_rate:.2f} RUB): {diff_pct:+.2f}%")

        logging.info("Недельная сводка валют ЦБ РФ получена успешно")
        return "\n".join(lines)

    except Exception as e:
        logging.error(f"Ошибка get_weekly_currency_summary (CBR): {e}")
        return "Не удалось получить недельный анализ валют ЦБ РФ."


# === Проверка криптовалют за неделю (оставлено без изменений) ===
def get_weekly_crypto_summary():
    """
    Возвращает краткий обзор криптовалют за неделю.
    """
    try:
        # CoinCap API предоставляет историю, но для простоты вернем текущий статус
        # с процентным изменением за 24 часа
        cryptos = {
            "bitcoin": "BTC",
            "ethereum": "ETH",
            "toncoin": "TON"
        }

        lines = ["📊 Криптовалюты (изменение за 24ч):"]

        for crypto_id, name in cryptos.items():
            try:
                resp = _http_get_with_retries(
                    f"{CRYPTO_API_URL}/{crypto_id}",
                    max_retries=2,
                    backoff=0.5
                )
                data = resp.json()

                if "data" in data:
                    change_24h = float(data["data"].get("changePercent24Hr", 0))
                    lines.append(f"{name}: {change_24h:+.2f}%")

            except Exception as e:
                logging.warning(f"Ошибка получения {crypto_id}: {e}")
                continue

        if len(lines) == 1:
            raise ValueError("Не удалось получить данные о криптовалютах")

        logging.info("Недельная сводка криптовалют получена успешно")
        return "\n".join(lines)

    except Exception as e:
        logging.error(f"Ошибка get_weekly_crypto_summary: {e}")
        return "Не удалось получить недельный анализ криптовалют."