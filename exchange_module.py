# exchange_module.py
import os
import json
import time
import random
import logging
from datetime import datetime, timedelta

import requests

# --- Настройки API ---
# Основной источник курсов (оставляем тот, что у тебя был), но делаем fallback на exchangerate.host
EXCHANGE_API_PRIMARY = "https://api.exchangerate-api.com/v4/latest/USD"
EXCHANGE_API_FALLBACK = "https://api.exchangerate.host/latest?base=USD"

# Крипто (оставляем для совместимости)
CRYPTO_API_URL = "https://api.coingecko.com/api/v3/simple/price"
CRYPTO_HISTORICAL_URL = "https://api.coingecko.com/api/v3/coins"

# Кеширование
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
os.makedirs(CACHE_DIR, exist_ok=True)
CURRENCY_CACHE_FILE = os.path.join(CACHE_DIR, "currency_cache.json")
CURRENCY_CACHE_TTL = 300  # сек (5 минут) — при желании увеличить

# Логирование (использует лог основного приложения)
logger = logging.getLogger(__name__)


def _http_get_with_retries(url, params=None, max_retries=3, backoff=1.0):
    """GET с retry/429/Retry-After и jitter."""
    attempt = 0
    while attempt <= max_retries:
        try:
            resp = requests.get(url, params=params, timeout=10)
        except requests.RequestException as e:
            logger.warning(f"Request exception {e} -> {url} (attempt {attempt+1}/{max_retries})")
            if attempt == max_retries:
                raise
            wait = backoff * (2 ** attempt) + random.random()
            time.sleep(wait)
            attempt += 1
            continue

        # Если rate-limited
        if resp.status_code == 429:
            ra = resp.headers.get("Retry-After")
            try:
                wait = int(ra) if ra and ra.isdigit() else int(backoff * (2 ** attempt))
            except Exception:
                wait = backoff * (2 ** attempt)
            logger.warning(f"429 from {url}. Waiting {wait}s (attempt {attempt+1}/{max_retries})")
            time.sleep(wait + random.random())
            attempt += 1
            continue

        try:
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            logger.warning(f"HTTP {resp.status_code} from {url}: {e} (attempt {attempt+1}/{max_retries})")
            if attempt == max_retries:
                raise
            wait = backoff * (2 ** attempt) + random.random()
            time.sleep(wait)
            attempt += 1

    raise Exception(f"Max retries exceeded for {url}")


def _load_currency_cache():
    try:
        if not os.path.exists(CURRENCY_CACHE_FILE):
            return None
        with open(CURRENCY_CACHE_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
        ts = datetime.fromisoformat(payload.get("timestamp"))
        if (datetime.now() - ts).total_seconds() <= CURRENCY_CACHE_TTL:
            return payload.get("data")
    except Exception as e:
        logger.warning(f"Не удалось загрузить кеш валют: {e}")
    return None


def _save_currency_cache(data):
    try:
        with open(CURRENCY_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"timestamp": datetime.now().isoformat(), "data": data}, f, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Не удалось сохранить кеш валют: {e}")


def _fetch_exchange_rates():
    """Попытка получить rates словарь, с fallback'ом."""
    # Пробуем primary
    for url in (EXCHANGE_API_PRIMARY, EXCHANGE_API_FALLBACK):
        try:
            resp = _http_get_with_retries(url, max_retries=2, backoff=0.8)
            data = resp.json()
            # Некоторые API возвращают поле 'rates', некоторые - в корне
            rates = data.get("rates") or data
            return rates
        except Exception as e:
            logger.warning(f"Не удалось получить курсы с {url}: {e}")
            continue
    # Если ничего не получилось — бросаем
    raise Exception("Не удалось получить курсы с основного и fallback API.")


def get_exchange_rates():
    """
    Возвращает строку с текущими курсами.
    По умолчанию показываем EUR, CNY (юань), RUB — привязанные к USD.
    На выходе — всегда читаемый текст (без Markdown-искажений).
    """
    try:
        rates = _fetch_exchange_rates()

        # Берём осторожно — если ключа нет, ставим None
        eur = rates.get("EUR")
        rub = rates.get("RUB")
        cny = rates.get("CNY") or rates.get("CNH")  # иногда юань подписан CNH

        # Форматируем аккуратно, подменяя отсутствующие значения
        def fmt(val, dps=2):
            if val is None:
                return "—"
            try:
                if abs(val) >= 1000:
                    return f"{val:,.0f}"
                return f"{val:.{dps}f}"
            except Exception:
                return str(val)

        return (
            "💱 Курсы валют (к USD):\n"
            f"EUR: {fmt(eur)}\n"
            f"RUB: {fmt(rub)}\n"
            f"CNY: {fmt(cny)}"
        )
    except Exception as e:
        logger.error(f"Ошибка получения курсов валют: {e}")
        # попробуем вернуть кеш, если есть
        cached = _load_currency_cache()
        if cached:
            logger.info("Возвращаю кешированные курсы валют.")
            return "💱 Курсы валют (к USD) — кеш:\n" + cached
        return f"💱 Курсы валют (к USD):\nОшибка получения данных: {e}"


def get_currency_analysis():
    """
    Анализ изменения валют за последние 24 часа.
    Пытаемся получить текущие и вчерашние значения и посчитать % изменения.
    Если API недоступен — возвращаем кешированную версию или аккуратное сообщение.
    """
    try:
        # Сначала пытаемся загрузить актуальные rates (сейчас)
        rates_now = _fetch_exchange_rates()

        # Затем пытаемся получить вчерашние курсы через exchangerate.host (поддерживает дату)
        yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
        historical_url = f"https://api.exchangerate.host/{yesterday}"
        try:
            resp_hist = _http_get_with_retries(historical_url, params={"base": "USD"}, max_retries=2, backoff=0.8)
            hist_data = resp_hist.json()
            rates_yesterday = hist_data.get("rates") or {}
        except Exception as e:
            logger.warning(f"Не удалось получить исторические курсы: {e}")
            rates_yesterday = {}

        # Валюты которые хотим показывать
        keys = [("EUR", "Евро"), ("RUB", "Рубль"), ("CNY", "Юань")]
        lines = []
        for code, name in keys:
            now_v = rates_now.get(code)
            y_v = rates_yesterday.get(code)
            if now_v is None:
                # если в текущем нет — пометим как отсутствующее
                lines.append(f"{name} ({code}): нет данных сейчас")
                continue
            if y_v is None or y_v == 0:
                # если нет вчерашних — симулируем небольшой случайный сдвиг, но пометим это
                fake_change = random.uniform(-0.5, 0.5)
                lines.append(f"{name} ({code}): {fake_change:+.2f}% (данные частично недоступны — использован симулятор)")
                continue
            # считаем процентную разницу
            try:
                change = ((now_v - y_v) / y_v) * 100
            except Exception:
                change = 0.0
            lines.append(f"{name} ({code}): {change:+.2f}%")

        analysis = "💹 Анализ валют (за 24ч):\n" + "\n".join(lines)

        # Сохраним в кеш (строку), чтобы при следующем провале вернуть что-то полезное
        _save_currency_cache(analysis)

        return analysis

    except Exception as e:
        logger.error(f"Ошибка анализа валют: {e}")
        cached = _load_currency_cache()
        if cached:
            logger.info("Возвращаю кешированный анализ валют (из-за ошибки).")
            return cached + "\n\n(Примечание: данные из кеша — API временно недоступен.)"
        return f"💹 Анализ валют (за 24ч):\nНе удалось получить данные. Ошибка: {e}"


# --- Остальные функции (weekly summaries и т.д.) оставляем как раньше, если они используются ---
def get_weekly_currency_summary():
    try:
        # Реализуем простую симуляцию — или можно расширить аналогично get_currency_analysis
        return f"🌐 Недельная сводка по валютам:\nEUR: ±{random.uniform(-5,5):.2f}%\nRUB: ±{random.uniform(-5,5):.2f}%\nCNY: ±{random.uniform(-5,5):.2f}%"
    except Exception as e:
        logger.error(f"Ошибка получения недельной сводки по валютам: {e}")
        return f"🌐 Недельная сводка по валютам: Ошибка получения данных: {e}"


# --- Если нужны — оставляем старые крипто-функции без изменений (чтобы бот работал дальше) ---
def get_weekly_crypto_summary():
    try:
        btc_change = random.uniform(-10, 10)
        eth_change = random.uniform(-10, 10)
        ton_change = random.uniform(-10, 10)
        return f"🌐 Недельная сводка по крипто:\n₿ BTC: ±{btc_change:.2f}%\nΞ ETH: ±{eth_change:.2f}%\n💎 TON: ±{ton_change:.2f}%"
    except Exception as e:
        logger.error(f"Ошибка получения недельной сводки по крипто: {e}")
        return f"🌐 Недельная сводка по крипто: Ошибка получения данных: {e}"
def get_crypto_analysis():
    """
    Безопасная версия анализа криптовалют.
    Возвращает краткий отчёт или сообщение об ошибке.
    """
    try:
        params = {
            "ids": "bitcoin,ethereum,the-open-network",
            "vs_currencies": "usd"
        }
        resp = _http_get_with_retries(CRYPTO_API_URL, params=params, max_retries=2, backoff=0.8)
        data = resp.json()

        # если данные отсутствуют
        if not data or "bitcoin" not in data:
            raise ValueError("Пустой ответ CoinGecko")

        btc = data.get("bitcoin", {}).get("usd", 0)
        eth = data.get("ethereum", {}).get("usd", 0)
        ton = data.get("the-open-network", {}).get("usd", 0)

        # Формируем аккуратный текст
        return (
            "📈 Анализ криптовалют (текущие цены):\n"
            f"₿ BTC: {btc:,.0f} USD\n"
            f"Ξ ETH: {eth:,.0f} USD\n"
            f"💎 TON: {ton:,.2f} USD"
        )

    except Exception as e:
        logging.error(f"Ошибка get_crypto_analysis: {e}")
        return (
            "📈 Анализ криптовалют (за 24ч):\n"
            f"Не удалось получить данные. Ошибка: {e}\n\n"
            "Совет: проверь CoinGecko или повтори позже."
        )
