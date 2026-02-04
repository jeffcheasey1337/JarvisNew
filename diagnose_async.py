# -*- coding: utf-8 -*-
"""
🔍 ДИАГНОСТИКА ASYNC WIKIPEDIA
Проверка работы асинхронных запросов
"""

import asyncio
import sys

print("="*80)
print("🔍 ДИАГНОСТИКА ASYNC WIKIPEDIA")
print("="*80)
print()

# Проверка aiohttp
print("[1/3] Проверка aiohttp...")
try:
    import aiohttp
    print(f"  ✓ aiohttp {aiohttp.__version__}")
except ImportError:
    print("  ✗ aiohttp не установлен")
    print()
    print("Установите: pip install aiohttp")
    input("Enter...")
    sys.exit(1)

print()

# Тест простого запроса
print("[2/3] Тест простого async запроса...")
print()

async def test_simple():
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            url = "https://ru.wikipedia.org"
            
            print(f"  Запрос: {url}")
            
            async with session.get(url) as response:
                print(f"  Статус: {response.status}")
                
                if response.status == 200:
                    print("  ✓ Wikipedia доступна")
                    return True
                elif response.status == 403:
                    print("  ✗ 403 Forbidden - требуется User-Agent")
                    return False
                else:
                    print(f"  ✗ Неожиданный статус: {response.status}")
                    return False
    
    except Exception as e:
        print(f"  ✗ Ошибка: {e}")
        return False

result = asyncio.run(test_simple())

print()

if not result:
    print("⚠ Простой запрос не работает")
    print()
    input("Enter...")

# Тест с User-Agent
print("[3/3] Тест с правильным User-Agent...")
print()

async def test_with_ua():
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        headers = {
            'User-Agent': 'JARVIS-Turbo/1.0 (Educational) Python/3.11'
        }
        
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            # Тест Wikipedia API
            api_url = "https://ru.wikipedia.org/w/api.php"
            
            params = {
                'action': 'opensearch',
                'search': 'Python',
                'limit': 1,
                'format': 'json'
            }
            
            print(f"  Запрос: {api_url}")
            print(f"  Параметры: {params}")
            print()
            
            async with session.get(api_url, params=params) as response:
                print(f"  Статус: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    print(f"  ✓ Ответ получен")
                    
                    if len(data) >= 2 and data[1]:
                        title = data[1][0]
                        print(f"  ✓ Найдено: {title}")
                        print()
                        
                        # Получаем контент
                        content_params = {
                            'action': 'query',
                            'prop': 'extracts',
                            'exintro': True,
                            'explaintext': True,
                            'titles': title,
                            'format': 'json'
                        }
                        
                        print("  Получение контента...")
                        
                        async with session.get(api_url, params=content_params) as response2:
                            print(f"  Статус: {response2.status}")
                            
                            if response2.status == 200:
                                data2 = await response2.json()
                                pages = data2.get('query', {}).get('pages', {})
                                
                                for page_data in pages.values():
                                    extract = page_data.get('extract', '')
                                    
                                    if extract:
                                        print(f"  ✓ Получено {len(extract)} символов")
                                        print()
                                        print("  Первые 200 символов:")
                                        print("  " + "-"*76)
                                        print("  " + extract[:200])
                                        print("  " + "-"*76)
                                        print()
                                        print("✅ ASYNC WIKIPEDIA РАБОТАЕТ!")
                                        return True
                                    else:
                                        print("  ✗ Контент пустой")
                            else:
                                print(f"  ✗ Ошибка получения контента: {response2.status}")
                    else:
                        print("  ✗ Результаты поиска пустые")
                elif response.status == 403:
                    print("  ✗ 403 Forbidden")
                    text = await response.text()
                    print(f"  Ответ: {text[:200]}")
                else:
                    print(f"  ✗ Статус: {response.status}")
                
                return False
    
    except Exception as e:
        print(f"  ✗ Исключение: {e}")
        import traceback
        traceback.print_exc()
        return False

result = asyncio.run(test_with_ua())

print()
print("="*80)

if result:
    print("✅ ВСЁ РАБОТАЕТ!")
    print()
    print("Async Wikipedia запросы успешны.")
    print("Turbo система должна работать.")
    print()
    print("Если test_turbo.py не работал - возможны другие проблемы:")
    print("  1. Таймауты слишком короткие")
    print("  2. Слишком много параллельных запросов")
    print("  3. Wikipedia ограничивает частоту")
    print()
    print("Запустите улучшенную версию:")
    print("  python test_turbo_fixed.py")
else:
    print("❌ ПРОБЛЕМЫ С ASYNC WIKIPEDIA")
    print()
    print("Возможные причины:")
    print("  1. Wikipedia блокирует aiohttp запросы")
    print("  2. Проблемы с SSL сертификатами")
    print("  3. Нужен другой User-Agent")
    print("  4. Требуется VPN")
    print()
    print("Решения:")
    print("  1. Используйте обычную версию (не турбо)")
    print("  2. Настройте VPN")
    print("  3. Используйте proxy")

print()
print("="*80)

input("\nEnter для выхода...")
