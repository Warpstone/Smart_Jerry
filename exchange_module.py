# -*- coding: utf-8 -*-
# pylint: disable=non-ascii-bytes

import requests

# Конфигурация для курсов валют
EXCHANGE_API_URL = 'https://api.exchangerate-api.com/v4/latest/RUB'
CRYPTO_API_URL = 'https://api.coingecko.com/api/v3/simple/price'

def get_exchange_rates():
    """Получает курсы валют и криптовалют"""
    try:
        # Получаем курсы обычных валют
        fiat_rates = get_fiat_rates()
        # Получаем курсы криптовалют
        crypto_rates = get_crypto_rates()
        
        return f"{fiat_rates}\n\n{crypto_rates}"
        
    except Exception as e:
        return f"Не удалось получить курсы валют. Ошибка: {e}"

def get_fiat_rates():
    """Получает курсы обычных валют"""
    try:
        response = requests.get(EXCHANGE_API_URL)
        data = response.json()
        
        # Получаем курсы относительно RUB (рубля)
        rub_to_usd = data['rates']['USD']  # Сколько долларов за 1 рубль
        rub_to_eur = data['rates']['EUR']  # Сколько евро за 1 рубль  
        rub_to_cny = data['rates']['CNY']  # Сколько юаней за 1 рубль
        
        # Вычисляем курсы валют к рублю (инвертируем)
        usd_rate = 1 / rub_to_usd  # Сколько рублей за 1 доллар
        eur_rate = 1 / rub_to_eur  # Сколько рублей за 1 евро
        cny_rate = 1 / rub_to_cny  # Сколько рублей за 1 юань
        
        return f"""💱 Курсы валют (к рублю):
🇺🇸 USD: {usd_rate:.2f} ₽
🇪🇺 EUR: {eur_rate:.2f} ₽
🇨🇳 CNY: {cny_rate:.2f} ₽"""
        
    except Exception as e:
        return f"Не удалось получить курсы валют. Ошибка: {e}"

def get_crypto_rates():
    """Получает курсы криптовалют"""
    try:
        # Получаем курсы криптовалют в долларах
        params = {
            'ids': 'bitcoin,ethereum,the-open-network',
            'vs_currencies': 'usd'
        }
        response = requests.get(CRYPTO_API_URL, params=params)
        data = response.json()
        
        # Получаем курс доллара к рублю
        usd_response = requests.get(EXCHANGE_API_URL)
        usd_data = usd_response.json()
        usd_to_rub = 1 / usd_data['rates']['USD']  # Сколько рублей за 1 доллар
        
        # Извлекаем курсы криптовалют
        btc_usd = data['bitcoin']['usd']
        eth_usd = data['ethereum']['usd']
        ton_usd = data['the-open-network']['usd']
        
        # Конвертируем в рубли
        btc_rub = btc_usd * usd_to_rub
        eth_rub = eth_usd * usd_to_rub
        ton_rub = ton_usd * usd_to_rub
        
        return f"""₿ Курсы криптовалют:
₿ BTC: {btc_rub:,.0f} ₽
Ξ ETH: {eth_rub:,.0f} ₽
💎 TON: {ton_rub:.2f} ₽"""
        
    except Exception as e:
        return f"Не удалось получить курсы криптовалют. Ошибка: {e}"
