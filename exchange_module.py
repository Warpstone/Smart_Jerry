import requests
import logging
from datetime import datetime, timedelta
import time
import random

# === Базовые настройки ===
# API Центрального Банка РФ
CURRENCY_API_URL = "https://www.cbr-xml-daily.ru/"
# НОВЫЙ, НАДЕЖНЫЙ API для криптовалют (Coinbase V2)
CRYPTO_API_URL = "https://api.coinbase.com/v2/"
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


# === НОВАЯ ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ОБРАБОТКИ ДАННЫХ (Coinbase) ===
def _fetch_and_process_crypto_data(url):
    """
    Функция для получения и форматирования текущих цен криптовалют
    с Coinbase V2 API.
    """
    # Маппинг для запросов и вывода: (API_Symbol, Display_Symbol, Display_Name)
    crypto_map = [
        ("BTC", "₿", "BTC"),
        ("ETH", "Ξ", "ETH"),
        ("TON", "💎", "TON"),
    ]

    lines = []
    retrieved_count = 0

    for api_symbol, display_symbol, display_name in crypto_map:
        # Формируем URL для запроса цены конкретной пары, например: /v2/prices/BTC-USD/spot
        endpoint = f"prices/{api_symbol}-USD/spot"
        full_url = url + endpoint

        try:
            # Делаем отдельный запрос для каждой монеты
            resp = _http_get_with_retries(full_url, max_retries=2, backoff=0.5)
            data = resp.json().get("data")

            if not data or "amount" not in data:
                logging.warning(f"Данные о цене не найдены для {display_name} в ответе Coinbase.")
                continue

            price_usd = float(data["amount"])

            # Форматирование цены
            if price_usd >= 1000:
                # Для BTC и ETH
                formatted_price = f"{price_usd:,.0f}"
            else:
                # Для TON
                formatted_price = f"{price_usd:,.2f}"

            lines.append(f"{display_symbol} {display_name}: {formatted_price} USD")
            retrieved_count += 1

        except Exception as e:
            # Логируем ошибку для конкретной монеты, но продолжаем для других
            logging.error(f"Ошибка получения цены {display_name} с Coinbase: {e}")
            continue

    if retrieved_count == 0:
        raise ConnectionError("Не удалось получить данные ни для одной криптовалюты.")

    return "\n".join(lines)


# === Анализ криптовалют (текущие цены) ===
def get_crypto_analysis():
    """
    Получает текущие цены криптовалют (BTC, ETH, TON) с помощью Coinbase API.
    """
    try:
        report = _fetch_and_process_crypto_data(CRYPTO_API_URL)
        logging.info("Анализ криптовалют получен успешно (Coinbase API)")
        return report

    except Exception as e:
        logging.error(f"Критическая ошибка: Coinbase API не сработал: {type(e).__name__} - {e}")
        return "📊 Криптовалюты: Критический сбой API. Не удалось получить данные."


# === Текущие курсы валют (Без изменений) ===
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


# === Проверка курса валют за неделю (Фикс с ЦБ РФ уже включен) ===
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
                lines.append(f"{code} {symbol} ({t_rate:.2f} RUB): {diff_pct:+.2f}%")  # Добавил \n
            else:
                lines.append(f"{code}: данные за неделю назад невалидны")

        logging.info("Недельная сводка валют ЦБ РФ получена успешно")
        return "\n".join(lines)

    except Exception as e:
        logging.error(f"Ошибка get_weekly_currency_summary (CBR): {e}")
        return "Не удалось получить недельный анализ валют ЦБ РФ."


# === Проверка криптовалют за неделю (Текущие цены) ===
def get_weekly_crypto_summary():
    """
    Возвращает краткий обзор текущих цен криптовалют (теперь используется Coinbase).
    """
    try:
        report = _fetch_and_process_crypto_data(CRYPTO_API_URL)
        logging.info("Сводка криптовалют получена успешно (Coinbase API)")
        return "📊 Криптовалюты (Текущие цены):\n" + report

    except Exception as e:
        logging.error(f"Критическая ошибка: Coinbase API не сработал: {type(e).__name__} - {e}")
        return "📊 Криптовалюты: Критический сбой API. Не удалось получить данные."