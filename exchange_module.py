import requests
import logging
from datetime import datetime, timedelta
import time
import random

# === Базовые настройки ===
# API Центрального Банка РФ
CURRENCY_API_URL = "https://www.cbr-xml-daily.ru/"
CRYPTO_API_URL = "https://api.coingecko.com/api/v3/simple/price"
HEADERS = {"User-Agent": "SmartJerryBot/1.0"}

# === НОВЫЙ РЕЗЕРВНЫЙ API (Placeholder) ===
# ВНИМАНИЕ: В реальном проекте этот URL и логика ниже должны быть настроены
# под CoinMarketCap, Coinbase или другой выбранный вами сервис.
CRYPTO_FALLBACK_API_URL = "https://api.coinmarketcap.com/data/v1/cryptocurrency/quotes/latest"


# === Вспомогательная функция для повторных запросов (Без изменений) ===
def _get_historical_cbr_rates(date: datetime, max_days_back=7):
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
    # ... (код без изменений) ...
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
    # ... (код без изменений) ...
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


# === НОВАЯ ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ОБРАБОТКИ ДАННЫХ ===
def _fetch_and_process_crypto_data(url, include_24h_change=False):
    """
    Универсальная функция для получения и форматирования данных криптовалют
    с учетом того, нужно ли включать 24-часовое изменение.
    """
    crypto_ids = "bitcoin,ethereum,the-open-network"

    params = {
        "ids": crypto_ids,
        "vs_currencies": "usd",
        "include_24hr_change": "true" if include_24h_change else "false"
    }

    resp = _http_get_with_retries(url, params=params, max_retries=2, backoff=0.5)
    data = resp.json()

    if not data:
        raise ValueError("Ответ API пуст или невалиден.")

    lines = []
    retrieved_count = 0

    crypto_map = {
        "bitcoin": ("BTC", "₿"),
        "ethereum": ("ETH", "Ξ"),
        "the-open-network": ("TON", "💎")
    }

    for crypto_id, (name, symbol) in crypto_map.items():
        asset_data = data.get(crypto_id)

        if not asset_data or "usd" not in asset_data:
            logging.warning(f"Данные о цене не найдены для {crypto_id}.")
            if include_24h_change:
                lines.append(f"{name}: Нет данных за 24ч")
            continue

        if include_24h_change:
            # Отчет по 24h изменению
            change_key = "usd_24hr_change"
            if change_key in asset_data:
                change_24h = float(asset_data[change_key])
                lines.append(f"{name}: {change_24h:+.2f}%")
                retrieved_count += 1
        else:
            # Отчет по текущим ценам
            price_usd = float(asset_data["usd"])
            if price_usd >= 1000:
                formatted_price = f"{price_usd:,.0f}"
            else:
                formatted_price = f"{price_usd:,.2f}"

            lines.append(f"{symbol} {name}: {formatted_price} USD")
            retrieved_count += 1

    if retrieved_count == 0:
        raise ValueError("Не удалось получить данные о криптовалютах")

    return "\n".join(lines)


# === Анализ криптовалют (текущие цены) - ДОБАВЛЕНА ЛОГИКА FALLBACK ===
def get_crypto_analysis():
    """
    Получает текущие цены криптовалют (BTC, ETH, TON) с помощью CoinGecko API,
    с резервным подключением к другому API в случае сбоя.
    """
    # 1. Попытка получить данные от ОСНОВНОГО API (CoinGecko)
    try:
        report = _fetch_and_process_crypto_data(CRYPTO_API_URL, include_24h_change=False)
        logging.info("Анализ криптовалют получен успешно (CoinGecko API)")
        return report

    except Exception as e:
        logging.warning(f"Ошибка CoinGecko API ({type(e).__name__}). Переключаюсь на резервный API.")

        # 2. Попытка получить данные от РЕЗЕРВНОГО API
        try:
            # ВНИМАНИЕ: Если этот резервный API имеет другой формат ответа,
            # вам нужно будет скопировать _fetch_and_process_crypto_data
            # и изменить логику обработки данных внутри копии.
            report = _fetch_and_process_crypto_data(CRYPTO_FALLBACK_API_URL, include_24h_change=False)
            logging.info("Анализ криптовалют получен успешно (Резервный API)")
            return report + "\n\n(Резервный API использован)"

        except Exception as fallback_e:
            logging.error(f"Критическая ошибка: Резервный API тоже не сработал: {type(fallback_e).__name__}")
            return f"📈 Анализ криптовалют: Критический сбой API. Не удалось получить данные."


# === Текущие курсы валют (Без изменений) ===
def get_exchange_rates():
    # ... (код без изменений) ...
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


# === Проверка курса валют за неделю (Без изменений) ===
def get_weekly_currency_summary():
    # ... (код без изменений) ...
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


def get_weekly_crypto_summary():
    """
    Возвращает краткий обзор изменения криптовалют за 24 часа.
    """
    try:
        # Пытаемся получить данные только от ОСНОВНОГО API (CoinGecko)
        report = _fetch_and_process_crypto_data(CRYPTO_API_URL, include_24h_change=True)
        logging.info("Сводка криптовалют получена успешно (CoinGecko API)")
        return "📊 Криптовалюты (изменение за 24ч):\n" + report

    except Exception as e:
        # Если сбой, просто возвращаем сообщение об ошибке
        logging.error(f"Ошибка CoinGecko API: {type(e).__name__} - Не удалось получить данные.")
        # Заменим "Критический сбой" на более мягкое сообщение
        return "📊 Криптовалюты: Не удалось получить данные за 24 часа (сбой основного API)."

        # 2. Попытка получить данные от РЕЗЕРВНОГО API
        try:
            # ВНИМАНИЕ: Если этот резервный API имеет другой формат ответа,
            # вам нужно будет скопировать _fetch_and_process_crypto_data
            # и изменить логику обработки данных внутри копии.
            report = _fetch_and_process_crypto_data(CRYPTO_FALLBACK_API_URL, include_24h_change=True)
            logging.info("Сводка криптовалют получена успешно (Резервный API)")
            return "📊 Криптовалюты (изменение за 24ч):\n" + report + "\n\n(Резервный API использован)"

        except Exception as fallback_e:
            logging.error(f"Критическая ошибка: Резервный API тоже не сработал: {type(fallback_e).__name__}")
            return "📊 Криптовалюты: Критический сбой API. Не удалось получить данные."