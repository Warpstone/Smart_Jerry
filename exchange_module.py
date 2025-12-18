import requests
import logging
from datetime import datetime, timedelta
import time

# === Базовые настройки ===
CURRENCY_API_URL = "https://www.cbr-xml-daily.ru/"
# Используем Binance V3 API
BINANCE_API_URL = "https://api.binance.com/api/v3"
HEADERS = {"User-Agent": "SmartJerryBot/1.0"}


# === Вспомогательные функции (Твои оригинальные без изменений) ===

def _http_get_with_retries(url, params=None, max_retries=3, backoff=1.5):
    """Твоя функция с повторами — оставляем как есть для стабильности."""
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


def _get_historical_cbr_rates(date: datetime, max_days_back=7):
    """Твоя функция получения архивных курсов ЦБ РФ."""
    current_date = date
    for i in range(max_days_back):
        date_str = current_date.strftime("%Y/%m/%d")
        url = f"{CURRENCY_API_URL}archive/{date_str}/daily_json.js"
        try:
            resp = _http_get_with_retries(url, max_retries=2, backoff=0.8)
            valutes = resp.json().get("Valute", {})
            if valutes:
                return valutes
        except Exception as e:
            logging.warning(f"Ошибка ЦБ за {date_str}: {e}")
        current_date -= timedelta(days=1)
    return {}


# === Анализ валют ЦБ РФ (Твой оригинальный код) ===

def get_exchange_rates():
    """Актуальные курсы ЦБ РФ (USD, EUR, CNY)."""
    try:
        resp = _http_get_with_retries(f"{CURRENCY_API_URL}daily_json.js")
        valutes = resp.json().get("Valute", {})
        lines = ["💵 Курсы валют ЦБ РФ (к RUB):"]
        for code, sym in [("USD", "$"), ("EUR", "€"), ("CNY", "¥")]:
            v = valutes.get(code)
            if v:
                rate = v["Value"] / v["Nominal"]
                lines.append(f"{sym} {code}: {rate:.2f}")
        return "\n".join(lines)
    except Exception as e:
        return f"💵 Курсы валют: Ошибка ЦБ ({e})"


def get_currency_analysis():
    """Суточный анализ валют ЦБ РФ."""
    try:
        resp = _http_get_with_retries(f"{CURRENCY_API_URL}daily_json.js")
        valutes = resp.json().get("Valute", {})
        lines = ["💱 Изменение курсов ЦБ РФ за сутки (к RUB):"]
        for code, sym in [("USD", "$"), ("EUR", "€"), ("CNY", "¥")]:
            v = valutes.get(code)
            if v:
                today = v["Value"] / v["Nominal"]
                prev = v["Previous"] / v["Nominal"]
                change = ((today - prev) / prev) * 100
                lines.append(f"{code} {sym} ({today:.2f} RUB): {change:+.2f}%")
        return "\n".join(lines)
    except Exception as e:
        return "💱 Анализ валют: Ошибка данных ЦБ."


def get_weekly_currency_summary():
    """Недельный анализ валют ЦБ РФ."""
    try:
        t_valutes = _http_get_with_retries(f"{CURRENCY_API_URL}daily_json.js").json().get("Valute", {})
        w_valutes = _get_historical_cbr_rates(datetime.now() - timedelta(days=7))
        lines = ["📅 Изменения курсов ЦБ РФ за 7 дней (к RUB):"]
        for code, sym in [("USD", "$"), ("EUR", "€")]:
            t, w = t_valutes.get(code), w_valutes.get(code)
            if t and w:
                diff = ((t["Value"] / t["Nominal"] - w["Value"] / w["Nominal"]) / (w["Value"] / w["Nominal"])) * 100
                lines.append(f"{code} {sym} ({t['Value'] / t['Nominal']:.2f} RUB): {diff:+.2f}%")
        return "\n".join(lines)
    except:
        return "Не удалось получить недельный анализ валют."


# === НОВЫЙ БЛОК: Криптовалюты (Binance API) ===

def get_crypto_analysis():
    """
    Дневной отчет по крипте. Теперь через Binance.
    Заменяет твой старый get_crypto_analysis.
    """
    # Теперь TON есть на Binance, используем прямые пары
    crypto_map = {"BTCUSDT": ("BTC", "₿"), "ETHUSDT": ("ETH", "Ξ"), "TONUSDT": ("TON", "💎")}
    lines = []

    for symbol, (name, icon) in crypto_map.items():
        try:
            url = f"{BINANCE_API_URL}/ticker/price"
            resp = requests.get(url, params={"symbol": symbol}, timeout=10)
            resp.raise_for_status()
            price = float(resp.json()['price'])

            fmt_p = f"{price:,.0f}" if price >= 1000 else f"{price:,.2f}"
            lines.append(f"{icon} {name}: {fmt_p} USD")
        except Exception as e:
            logging.error(f"Ошибка Binance для {name}: {e}")
            lines.append(f"{icon} {name}: нет данных")

    return "\n".join(lines) if lines else "📊 Криптовалюты: Сервис временно недоступен."


def get_weekly_crypto_summary():
    """
    Еженедельный отчет (Воскресенье).
    Использует Binance Klines для расчета изменения за 7 дней.
    """
    crypto_map = {"BTCUSDT": ("BTC", "₿"), "ETHUSDT": ("ETH", "Ξ"), "TONUSDT": ("TON", "💎")}
    lines = []

    for symbol, (name, icon) in crypto_map.items():
        try:
            # Запрашиваем дневные свечи. limit=8 дает нам текущую свечу + 7 предыдущих
            url = f"{BINANCE_API_URL}/klines"
            params = {"symbol": symbol, "interval": "1d", "limit": 8}
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()

            # Цена сейчас (закрытие последней свечи) и цена 7 дней назад (закрытие первой свечи в выборке)
            price_now = float(data[-1][4])
            price_old = float(data[0][4])

            change = ((price_now - price_old) / price_old) * 100
            fmt_p = f"{price_now:,.0f}" if price_now >= 1000 else f"{price_now:,.2f}"

            lines.append(f"{icon} {name} ({fmt_p} USD): {change:+.2f}%")
        except Exception as e:
            logging.error(f"Ошибка Binance Weekly для {name}: {e}")

    if not lines:
        return "📊 Криптовалюты: Не удалось собрать недельный отчет."

    return "📊 Криптовалюты (изменение за 7 дней):\n" + "\n".join(lines)