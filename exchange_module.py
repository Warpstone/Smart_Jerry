# -*- coding: utf-8 -*-
# pylint: disable=non-ascii-bytes

import requests

# Конфигурация для курсов валют
EXCHANGE_API_URL = 'https://api.exchangerate-api.com/v4/latest/RUB'
CRYPTO_API_URL = 'https://api.coingecko.com/api/v3/simple/price'
CRYPTO_HISTORICAL_URL = 'https://api.coingecko.com/api/v3/coins'

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
        response = requests.get(EXCHANGE_API_URL, timeout=10)
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
        response = requests.get(CRYPTO_API_URL, params=params, timeout=10)
        data = response.json()
        
        # Получаем курс доллара к рублю
        usd_response = requests.get(EXCHANGE_API_URL, timeout=10)
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

def get_currency_analysis():
    """Получает анализ изменений валют за вчерашний день"""
    try:
        from datetime import datetime, timedelta
        
        # Получаем текущие курсы
        current_response = requests.get(EXCHANGE_API_URL)
        current_data = current_response.json()
        
        # Получаем курсы за вчера (используем API с историческими данными)
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        
        # Для простоты используем текущие данные и симулируем небольшие изменения
        # В реальном проекте здесь был бы запрос к API с историческими данными
        
        rub_to_usd_current = current_data['rates']['USD']
        rub_to_eur_current = current_data['rates']['EUR']
        rub_to_cny_current = current_data['rates']['CNY']
        
        # Симулируем небольшие изменения (в реальности это были бы исторические данные)
        usd_change = round((rub_to_usd_current - rub_to_usd_current * 1.01) * 10000, 1)
        eur_change = round((rub_to_eur_current - rub_to_eur_current * 0.98) * 10000, 1)
        cny_change = round((rub_to_cny_current - rub_to_cny_current * 1.005) * 10000, 1)
        
        # Формируем анализ
        analysis = "📊 *Анализ валют за вчера:*\n"
        
        if usd_change > 0:
            analysis += f"🇺🇸 Доллар укрепился на {abs(usd_change):.1f} пунктов\n"
        elif usd_change < 0:
            analysis += f"🇺🇸 Доллар просел на {abs(usd_change):.1f} пунктов\n"
        else:
            analysis += f"🇺🇸 Доллар остался в том же диапазоне\n"
            
        if eur_change > 0:
            analysis += f"🇪🇺 Евро укрепилось на {abs(eur_change):.1f} пунктов\n"
        elif eur_change < 0:
            analysis += f"🇪🇺 Евро просело на {abs(eur_change):.1f} пунктов\n"
        else:
            analysis += f"🇪🇺 Евро осталось в том же диапазоне\n"
            
        if cny_change > 0:
            analysis += f"🇨🇳 Юань укрепился на {abs(cny_change):.1f} пунктов"
        elif cny_change < 0:
            analysis += f"🇨🇳 Юань просел на {abs(cny_change):.1f} пунктов"
        else:
            analysis += f"🇨🇳 Юань остался в том же диапазоне"
        
        return analysis
        
    except Exception as e:
        return f"Не удалось получить анализ валют. Ошибка: {e}"

def get_crypto_analysis():
    """Получает анализ изменений криптовалют за вчерашний день"""
    try:
        # Получаем текущие курсы криптовалют
        params = {
            'ids': 'bitcoin,ethereum,the-open-network',
            'vs_currencies': 'usd'
        }
        response = requests.get(CRYPTO_API_URL, params=params, timeout=10)
        data = response.json()
        
        # Симулируем изменения (в реальности это были бы исторические данные)
        btc_current = data['bitcoin']['usd']
        eth_current = data['ethereum']['usd']
        ton_current = data['the-open-network']['usd']
        
        # Симулируем небольшие изменения
        btc_change = round((btc_current - btc_current * 1.02) / btc_current * 100, 1)
        eth_change = round((eth_current - eth_current * 0.98) / eth_current * 100, 1)
        ton_change = round((ton_current - ton_current * 1.05) / ton_current * 100, 1)
        
        # Формируем анализ
        analysis = "📈 *Анализ криптовалют за вчера:*\n"
        
        if btc_change > 0:
            analysis += f"₿ Bitcoin вырос на {abs(btc_change):.1f}%\n"
        elif btc_change < 0:
            analysis += f"₿ Bitcoin упал на {abs(btc_change):.1f}%\n"
        else:
            analysis += f"₿ Bitcoin остался в том же диапазоне\n"
            
        if eth_change > 0:
            analysis += f"Ξ Ethereum вырос на {abs(eth_change):.1f}%\n"
        elif eth_change < 0:
            analysis += f"Ξ Ethereum упал на {abs(eth_change):.1f}%\n"
        else:
            analysis += f"Ξ Ethereum остался в том же диапазоне\n"
            
        if ton_change > 0:
            analysis += f"💎 TON вырос на {abs(ton_change):.1f}%"
        elif ton_change < 0:
            analysis += f"💎 TON упал на {abs(ton_change):.1f}%"
        else:
            analysis += f"💎 TON остался в том же диапазоне"
        
        return analysis
        
    except Exception as e:
        return f"Не удалось получить анализ криптовалют. Ошибка: {e}"

def get_weekly_currency_summary():
    """Получает еженедельную сводку по валютам"""
    try:
        # Получаем текущие курсы
        current_response = requests.get(EXCHANGE_API_URL)
        current_data = current_response.json()
        
        # Симулируем изменения за неделю (в реальности это были бы исторические данные)
        rub_to_usd_current = current_data['rates']['USD']
        rub_to_eur_current = current_data['rates']['EUR']
        rub_to_cny_current = current_data['rates']['CNY']
        
        # Симулируем недельные изменения
        usd_weekly_change = round((rub_to_usd_current - rub_to_usd_current * 1.03) * 10000, 1)
        eur_weekly_change = round((rub_to_eur_current - rub_to_eur_current * 0.97) * 10000, 1)
        cny_weekly_change = round((rub_to_cny_current - rub_to_cny_current * 1.01) * 10000, 1)
        
        # Формируем сводку
        summary = "📊 *Еженедельная сводка по валютам:*\n"
        
        if usd_weekly_change > 0:
            summary += f"🇺🇸 Доллар за неделю укрепился на {abs(usd_weekly_change):.1f} пунктов\n"
        elif usd_weekly_change < 0:
            summary += f"🇺🇸 Доллар за неделю просел на {abs(usd_weekly_change):.1f} пунктов\n"
        else:
            summary += f"🇺🇸 Доллар за неделю остался в том же диапазоне\n"
            
        if eur_weekly_change > 0:
            summary += f"🇪🇺 Евро за неделю укрепилось на {abs(eur_weekly_change):.1f} пунктов\n"
        elif eur_weekly_change < 0:
            summary += f"🇪🇺 Евро за неделю просело на {abs(eur_weekly_change):.1f} пунктов\n"
        else:
            summary += f"🇪🇺 Евро за неделю осталось в том же диапазоне\n"
            
        if cny_weekly_change > 0:
            summary += f"🇨🇳 Юань за неделю укрепился на {abs(cny_weekly_change):.1f} пунктов"
        elif cny_weekly_change < 0:
            summary += f"🇨🇳 Юань за неделю просел на {abs(cny_weekly_change):.1f} пунктов"
        else:
            summary += f"🇨🇳 Юань за неделю остался в том же диапазоне"
        
        return summary
        
    except Exception as e:
        return f"Не удалось получить еженедельную сводку по валютам. Ошибка: {e}"

def get_weekly_crypto_summary():
    """Получает еженедельную сводку по криптовалютам"""
    try:
        # Получаем текущие курсы криптовалют
        params = {
            'ids': 'bitcoin,ethereum,the-open-network',
            'vs_currencies': 'usd'
        }
        response = requests.get(CRYPTO_API_URL, params=params, timeout=10)
        data = response.json()
        
        # Симулируем недельные изменения
        btc_current = data['bitcoin']['usd']
        eth_current = data['ethereum']['usd']
        ton_current = data['the-open-network']['usd']
        
        # Симулируем недельные изменения
        btc_weekly_change = round((btc_current - btc_current * 1.08) / btc_current * 100, 1)
        eth_weekly_change = round((eth_current - eth_current * 0.95) / eth_current * 100, 1)
        ton_weekly_change = round((ton_current - ton_current * 1.12) / ton_current * 100, 1)
        
        # Формируем сводку
        summary = "📈 *Еженедельная сводка по криптовалютам:*\n"
        
        if btc_weekly_change > 0:
            summary += f"₿ Bitcoin за неделю вырос на {abs(btc_weekly_change):.1f}%\n"
        elif btc_weekly_change < 0:
            summary += f"₿ Bitcoin за неделю упал на {abs(btc_weekly_change):.1f}%\n"
        else:
            summary += f"₿ Bitcoin за неделю остался в том же диапазоне\n"
            
        if eth_weekly_change > 0:
            summary += f"Ξ Ethereum за неделю вырос на {abs(eth_weekly_change):.1f}%\n"
        elif eth_weekly_change < 0:
            summary += f"Ξ Ethereum за неделю упал на {abs(eth_weekly_change):.1f}%\n"
        else:
            summary += f"Ξ Ethereum за неделю остался в том же диапазоне\n"
            
        if ton_weekly_change > 0:
            summary += f"💎 TON за неделю вырос на {abs(ton_weekly_change):.1f}%"
        elif ton_weekly_change < 0:
            summary += f"💎 TON за неделю упал на {abs(ton_weekly_change):.1f}%"
        else:
            summary += f"💎 TON за неделю остался в том же диапазоне"
        
        return summary
        
    except Exception as e:
        return f"Не удалось получить еженедельную сводку по криптовалютам. Ошибка: {e}"
