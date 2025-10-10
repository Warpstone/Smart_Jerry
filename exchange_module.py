import os
import json
import time
import random
from datetime import datetime
import logging
import requests

# --- Конфигурация кеша и endpoint'ов ---
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, "crypto_cache.json")
CACHE_TTL = 300  # секунды — 5 минут (подставь своё значение при необходимости)

COINGECKO_MARKETS_URL = "https://api.coingecko.com/api/v3/coins/markets"
CRYPTO_IDS = "bitcoin,ethereum,the-open-network"  # список монет через запятую
EXCHANGE_API_URL = 'https://api.exchangerate-api.com/v4/latest/USD'  # API для курса USD->RUB

def _request_with_retries(url, params=None, headers=None, max_retries=3, backoff_factor=1.0):
    """GET с экспоненциальным бэкофом и поддержкой Retry-After для 429."""
    attempt = 0
    while attempt <= max_retries:
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
        except requests.RequestException as e:
            logging.warning(f"Request exception to {url}: {e}. attempt {attempt+1}/{max_retries}")
            if attempt == max_retries:
                raise
            wait = backoff_factor * (2 ** attempt) + random.random()
            time.sleep(wait)
            attempt += 1
            continue

        if resp.status_code == 429:
            # Rate limit — сначала проверяем Retry-After
            retry_after = resp.headers.get("Retry-After")
            try:
                wait = int(retry_after) if retry_after and retry_after.isdigit() else int(backoff_factor * (2 ** attempt))
            except Exception:
                wait = backoff_factor * (2 ** attempt)
            logging.warning(f"429 from {url}. Waiting {wait}s before retry (attempt {attempt+1}/{max_retries}).")
            time.sleep(wait + random.random())
            attempt += 1
            continue

        try:
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            logging.warning(f"HTTP error {resp.status_code} from {url}: {e}. attempt {attempt+1}/{max_retries}")
            if attempt == max_retries:
                raise
            wait = backoff_factor * (2 ** attempt) + random.random()
            time.sleep(wait)
            attempt += 1

    raise Exception("Max retries exceeded for " + url)


def _load_cached_analysis():
    """Вернём кешированный анализ, если он свежий."""
    try:
        if not os.path.exists(CACHE_FILE):
            return None
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
        ts = datetime.fromisoformat(payload.get("timestamp"))
        if (datetime.now() - ts).total_seconds() <= CACHE_TTL:
            return payload.get("analysis")
    except Exception as e:
        logging.warning(f"Не удалось загрузить кеш: {e}")
    return None


def _save_cached_analysis(analysis_text):
    """Сохраним анализ в кеш (контролируемый файл .cache/crypto_cache.json)."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"timestamp": datetime.now().isoformat(), "analysis": analysis_text}, f, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Не удалось сохранить кеш: {e}")


def get_exchange_rates():
    """Получает текущие курсы валют и криптовалют"""
    try:
        print(f"[{datetime.now()}] Получаю курсы валют...")
        
        # Получаем курс USD к рублю
        ex_resp = _request_with_retries(EXCHANGE_API_URL, max_retries=2, backoff_factor=1.0)
        ex_data = ex_resp.json()
        usd_to_rub = ex_data.get("rates", {}).get("RUB", 95.0)
        
        # Получаем курсы криптовалют
        params = {
            "ids": CRYPTO_IDS,
            "vs_currency": "usd"
        }
        resp = _request_with_retries(COINGECKO_MARKETS_URL, params=params, max_retries=2, backoff_factor=1.0)
        data = resp.json()
        
        by_id = {item.get("id"): item for item in data}
        btc_usd = by_id.get("bitcoin", {}).get("current_price", 0)
        eth_usd = by_id.get("ethereum", {}).get("current_price", 0)
        ton_usd = by_id.get("the-open-network", {}).get("current_price", 0)
        
        btc_rub = btc_usd * usd_to_rub
        eth_rub = eth_usd * usd_to_rub
        ton_rub = ton_usd * usd_to_rub
        
        # Формируем сообщение
        message = f"""💱 Курсы валют (к рублю):
🇺🇸 USD: {usd_to_rub:.2f} ₽

₿ Курсы криптовалют:
₿ BTC: {btc_rub:,.0f} ₽
Ξ ETH: {eth_rub:,.0f} ₽
💎 TON: {ton_rub:.2f} ₽"""
        
        print(f"[{datetime.now()}] Курсы валют получены успешно")
        return message
        
    except Exception as e:
        logging.error(f"Ошибка при получении курсов валют: {e}")
        return f"💱 Не удалось получить курсы валют. Ошибка: {e}"


def get_currency_analysis():
    """Получает анализ изменений валют"""
    try:
        # Упрощенная версия - возвращаем общую информацию
        return "📊 *Анализ валют:* Данные обновляются..."
    except Exception as e:
        logging.error(f"Ошибка в анализе валют: {e}")
        return "📊 Анализ валют недоступен"


def get_weekly_currency_summary():
    """Получает еженедельную сводку по валютам"""
    try:
        return "📊 *Еженедельная сводка по валютам:*\nДанные за неделю обновляются..."
    except Exception as e:
        logging.error(f"Ошибка в еженедельной сводке валют: {e}")
        return "📊 Еженедельная сводка валют недоступна"


def get_weekly_crypto_summary():
    """Получает еженедельную сводку по криптовалютам"""
    try:
        return "📈 *Еженедельная сводка по криптовалютам:*\nДанные за неделю обновляются..."
    except Exception as e:
        logging.error(f"Ошибка в еженедельной сводке криптовалют: {e}")
        return "📈 Еженедельная сводка криптовалют недоступна"


def get_crypto_analysis():
    """Получает анализ изменения криптовалют за 24ч.
    Использует /coins/markets (один запрос) + кеш + retry на 429.
    """
    try:
        # 1) Попробуем выполнить один компактный запрос, который вернёт цену и 24h изменение сразу
        params = {
            "ids": CRYPTO_IDS,
            "vs_currency": "usd",
            "price_change_percentage": "24h"
        }
        resp = _request_with_retries(COINGECKO_MARKETS_URL, params=params, max_retries=3, backoff_factor=1.0)
        data = resp.json()

        if not data:
            raise ValueError("Пустой ответ от CoinGecko")

        # 2) Получим текущий курс USD->RUB (по одному запросу)
        try:
            ex_resp = _request_with_retries(EXCHANGE_API_URL, max_retries=2, backoff_factor=1.0)
            ex_data = ex_resp.json()
            usd_to_rub = ex_data.get("rates", {}).get("RUB", 1)
        except Exception as e:
            logging.warning(f"Не удалось получить курс USD->RUB: {e}. Будем считать 1.")
            usd_to_rub = 1

        # 3) Соберём анализ по каждой монете
        # создаём словарь по id для удобства
        by_id = {item.get("id"): item for item in data}
        def extract_price_info(coin_id):
            coin = by_id.get(coin_id, {})
            current = coin.get("current_price")
            # сначала смотрим standard field, потом fallback
            change = coin.get("price_change_percentage_24h")
            if change is None:
                # бывают разные поля — попробуем взять вложенный вариант
                change = coin.get("price_change_percentage_24h_in_currency", {}).get("usd")
            return current, change

        btc_cur, btc_change = extract_price_info("bitcoin")
        eth_cur, eth_change = extract_price_info("ethereum")
        ton_cur, ton_change = extract_price_info("the-open-network")

        # безопасные fallback'ы, если чего-то нет
        if btc_cur is None: btc_cur = 0
        if eth_cur is None: eth_cur = 0
        if ton_cur is None: ton_cur = 0
        if btc_change is None: btc_change = 0
        if eth_change is None: eth_change = 0
        if ton_change is None: ton_change = 0

        btc_rub = btc_cur * usd_to_rub
        eth_rub = eth_cur * usd_to_rub
        ton_rub = ton_cur * usd_to_rub

        analysis = (
            "📈 Анализ криптовалют (за 24ч):\n"
            f"₿ BTC: {btc_change:+.2f}% ({btc_rub:,.0f} ₽)\n"
            f"Ξ ETH: {eth_change:+.2f}% ({eth_rub:,.0f} ₽)\n"
            f"💎 TON: {ton_change:+.2f}% ({ton_rub:,.0f} ₽)"
        )

        # сохраним в контролируемый кеш
        _save_cached_analysis(analysis)
        return analysis

    except Exception as e:
        logging.error(f"Ошибка в анализе криптовалют: {e}")
        # попытка вернуть кешированное значение
        cached = _load_cached_analysis()
        if cached:
            logging.info("Возвращаю кешированные данные по криптовалютам (из-за ошибки API).")
            return cached + "\n\n(Примечание: данные из кеша — API временно недоступен.)"
        # если кеша нет — возвращаем сообщение об ошибке
        return f"📈 Анализ криптовалют (за 24ч):\nНе удалось получить данные. Ошибка: {e}\n\n*Совет:* проверь CoinGecko."
