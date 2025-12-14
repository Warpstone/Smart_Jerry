import requests
import logging
from datetime import datetime, timedelta
import time
import random

# === Базовые настройки ===
# API Центрального Банка РФ
CURRENCY_API_URL = "https://www.cbr-xml-daily.ru/"
# НОВЫЙ API для ДНЕВНОГО отчета (CoinGecko Simple Price)
CRYPTO_DAILY_API_URL = "https://api.coingecko.com/api/v3/simple/price"
# API для НЕДЕЛЬНОГО отчета (CoinGecko Markets)
CRYPTO_WEEKLY_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
HEADERS = {"User-Agent": "SmartJerryBot/1.0"}


# === Вспомогательная функция для повторных запросов ===
def _get_historical_cbr_rates(date: datetime, max_days_back=7):
    """
    Получает архивные курсы ЦБ РФ, смещаясь назад, если дата нерабочая.
    """
    current_date = date
    for i in range(max_days_back):
        # Правильный формат даты для архива ЦБ РФ: YYYY/MM/DD
        date_str = current_date.strftime("%Y/%m/%d")
        url = f"{CURRENCY_API_URL}archive/{date_str}/daily_json.js"
        try:
            resp = _http_get_with_retries(url, max_retries=2, backoff=0.8)
            valutes = resp.json().get("Valute", {})
            # Проверяем, что в ответе есть данные о валютах, иначе это пустой день
            if valutes:
                logging.info(f"Исторические данные ЦБ РФ получены за {date_str}")
                return valutes
        except Exception as e:
            # Логируем ошибку, но пробуем предыдущий день
            logging.warning(f"Ошибка получения данных ЦБ за {date_str}. Пробую предыдущий день. {e}")

        # Сдвиг на предыдущий день
        current_date = current_date - timedelta(days=1)

    logging.error(f"Не удалось получить исторические данные ЦБ за {max_days_back} дней до {date.strftime('%Y-%m-%d')}")
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


# === Анализ валют за сутки (Без изменений) ===
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

        logging.info("Анализ валют ЦБ РФ получен успешно.")
        return "\n".join(lines)

    except Exception as e:
        logging.error(f"Ошибка get_currency_analysis (CBR): {e}")
        return f"💱 Анализ валют: Не удалось получить данные ЦБ РФ ({e})"


# === НОВАЯ ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ТЕКУЩЕЙ ЦЕНЫ (CoinGecko Simple Price) ===
def _get_crypto_current_price(asset_ids: str):
    """Получает текущие цены активов с CoinGecko Simple Price API."""

    # asset_ids - это строка с id через запятую, например: "bitcoin,ethereum,the-open-network"
    params = {
        "ids": asset_ids,
        "vs_currencies": "usd"
    }

    url = CRYPTO_DAILY_API_URL
    resp = _http_get_with_retries(url, params=params, max_retries=2, backoff=0.5)

    # Ответ имеет вид: {"bitcoin": {"usd": 65000}, "ethereum": {"usd": 4000}, ...}
    return resp.json()


# === ИСПРАВЛЕННЫЙ АНАЛИЗ КРИПТОВАЛЮТ (текущие цены - ДНЕВНОЙ ОТЧЕТ) ===
def get_crypto_analysis():
    """
    Получает текущие цены криптовалют (BTC, ETH, TON) через CoinGecko Simple Price API.
    Эта функция предназначена для ежедневной сводки.
    """
    # Mapping: CoinGecko Asset ID : (Display Name, Symbol)
    crypto_map = {
        "bitcoin": ("BTC", "₿"),
        "ethereum": ("ETH", "Ξ"),
        "the-open-network": ("TON", "💎"),
    }

    # Собираем ID для запроса в одну строку
    asset_ids = ",".join(crypto_map.keys())

    lines = []
    retrieved_count = 0

    try:
        # Получаем все цены одним запросом
        all_prices = _get_crypto_current_price(asset_ids)
        logging.info("Текущие цены криптовалют получены успешно (CoinGecko Simple API)")

        for asset_id, (name, symbol) in crypto_map.items():
            # Извлекаем цену. Если данных нет, price_usd будет 0.0
            price_usd = all_prices.get(asset_id, {}).get("usd", 0.0)

            if price_usd > 0:
                # Форматирование цены
                formatted_price = f"{price_usd:,.2f}"
                if price_usd >= 1000:
                    formatted_price = f"{price_usd:,.0f}"

                lines.append(f"{symbol} {name}: {formatted_price} USD")
                retrieved_count += 1
            else:
                logging.warning(f"Не удалось получить цену для {name} из ответа CoinGecko Simple API.")

    except Exception as e:
        logging.error(f"Критическая ошибка get_crypto_analysis (CoinGecko Simple): {e}")

    if retrieved_count == 0:
        return "📊 Криптовалюты: Критический сбой API. Не удалось получить данные."

    return "\n".join(lines)


# === Текущие курсы валют (Без изменений) ===
def get_exchange_rates():
    """Возвращает актуальные курсы валют ЦБ РФ."""
    try:
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


# === Проверка курса валют за неделю (Без изменений) ===
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

        # 2. Получаем курсы неделю назад (через архив, с функцией отката на рабочий день)
        w_valutes = _get_historical_cbr_rates(week_ago)

        lines = ["📅 Изменения курсов ЦБ РФ за 7 дней (к RUB):"]
        currency_codes = ["USD", "EUR"]

        # Если не удалось получить исторические данные
        if not w_valutes:
            for code in currency_codes:
                lines.append(f"{code}: исторические данные недоступны")
            return "\n".join(lines)

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
            else:
                lines.append(f"{code}: данные за неделю назад невалидны")

        logging.info("Недельная сводка валют ЦБ РФ получена успешно")
        return "\n".join(lines)

    except Exception as e:
        logging.error(f"Ошибка get_weekly_currency_summary (CBR): {e}")
        return "Не удалось получить недельный анализ валют ЦБ РФ."


# === НЕДЕЛЬНАЯ СВОДКА ПО КРИПТОВАЛЮТАМ (Без изменений) ===
def _get_crypto_weekly_change_coingecko():
    """
    Получает текущие цены и 7-дневное изменение с CoinGecko Markets API.
    """
    # CoinGecko ID для запроса
    crypto_ids = "bitcoin,ethereum,the-open-network"

    params = {
        "vs_currency": "usd",
        "ids": crypto_ids,
        # Запрашиваем 7-дневное изменение цены
        "price_change_percentage": "7d"
    }

    url = CRYPTO_WEEKLY_API_URL
    resp = _http_get_with_retries(url, params=params, max_retries=2, backoff=0.5)
    data_list = resp.json()

    if not isinstance(data_list, list) or not data_list:
        raise ValueError("Ответ CoinGecko Markets API пуст или невалиден.")

    lines = []
    symbol_map = {"btc": "₿", "eth": "Ξ", "ton": "💎"}

    for item in data_list:
        symbol = item.get('symbol', '').lower()

        # Проверяем наличие всех нужных данных
        price_today = item.get('current_price')
        change_7d = item.get('price_change_percentage_7d_in_currency')

        if price_today and change_7d is not None and symbol in symbol_map:
            # Форматирование цены
            formatted_price_today = f"{price_today:,.2f}"
            if price_today >= 1000:
                formatted_price_today = f"{price_today:,.0f}"

            # Форматирование изменения
            formatted_change = f"{change_7d:+.2f}%"

            display_name = item.get('name').upper().replace('COIN', '')  # Очищаем имя
            display_symbol = symbol_map.get(symbol, '')

            lines.append(f"{display_symbol} {display_name} ({formatted_price_today} USD): {formatted_change}")

    if not lines:
        raise ValueError("Не удалось получить данные о недельном изменении для всех криптовалют.")

    return "\n".join(lines)


def get_weekly_crypto_summary():
    """
    Возвращает краткий обзор изменения криптовалют за 7 дней
    (использует CoinGecko Markets API).
    """
    try:
        report = _get_crypto_weekly_change_coingecko()
        logging.info("Недельная сводка криптовалют получена успешно (CoinGecko Markets API)")
        return "📊 Криптовалюты (изменение за 7 дней):\n" + report

    except Exception as e:
        logging.error(f"Критическая ошибка: CoinGecko Markets API не сработал: {type(e).__name__} - {e}")
        # Возвращаем сообщение об ошибке
        return "📊 Криптовалюты: Критический сбой API. Не удалось получить данные для недельного отчета."