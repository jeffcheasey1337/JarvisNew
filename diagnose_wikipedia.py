# -*- coding: utf-8 -*-
"""
🔍 ДИАГНОСТИЧЕСКАЯ ВЕРСИЯ
Подробное логирование каждого шага
"""

import requests
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(message)s'
)

print("="*80)
print("🔍 ДЕТАЛЬНАЯ ДИАГНОСТИКА WIKIPEDIA API")
print("="*80)
print()

# Тест прямого запроса к Wikipedia
print("[1/4] Тест прямого доступа к Wikipedia...")
print()

try:
    response = requests.get('https://ru.wikipedia.org', timeout=10)
    print(f"  ✓ Статус: {response.status_code}")
    print(f"  ✓ Wikipedia доступна")
except Exception as e:
    print(f"  ✗ Ошибка: {e}")
    print("  Проверьте интернет-соединение")

print()

# Тест API поиска
print("[2/4] Тест Wikipedia API - поиск...")
print()

query = "Python programming"

try:
    api_url = "https://ru.wikipedia.org/w/api.php"
    
    params = {
        'action': 'opensearch',
        'search': query,
        'limit': 5,
        'format': 'json'
    }
    
    print(f"  URL: {api_url}")
    print(f"  Параметры: {params}")
    print()
    
    response = requests.get(api_url, params=params, timeout=10)
    
    print(f"  Статус: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"  ✓ Ответ получен")
        print()
        print("  Результаты поиска:")
        
        if len(data) >= 2:
            titles = data[1]
            descriptions = data[2] if len(data) > 2 else []
            urls = data[3] if len(data) > 3 else []
            
            for i, title in enumerate(titles):
                print(f"    {i+1}. {title}")
                if i < len(descriptions):
                    print(f"       {descriptions[i]}")
                if i < len(urls):
                    print(f"       URL: {urls[i]}")
                print()
            
            if titles:
                print(f"  ✓ Найдено {len(titles)} результатов")
            else:
                print("  ⚠ Результаты пустые")
        else:
            print("  ⚠ Неожиданный формат ответа")
            print(f"  Данные: {data}")
    else:
        print(f"  ✗ Ошибка: статус {response.status_code}")
        print(f"  Ответ: {response.text[:500]}")

except Exception as e:
    print(f"  ✗ Исключение: {e}")
    import traceback
    traceback.print_exc()

print()

# Тест получения контента
print("[3/4] Тест Wikipedia API - получение статьи...")
print()

try:
    api_url = "https://ru.wikipedia.org/w/api.php"
    
    # Пробуем конкретное название статьи
    title = "Python"
    
    params = {
        'action': 'query',
        'prop': 'extracts',
        'exintro': True,
        'explaintext': True,
        'titles': title,
        'format': 'json'
    }
    
    print(f"  Статья: {title}")
    print(f"  Параметры: {params}")
    print()
    
    response = requests.get(api_url, params=params, timeout=10)
    
    print(f"  Статус: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        pages = data.get('query', {}).get('pages', {})
        
        print(f"  Страниц в ответе: {len(pages)}")
        print()
        
        for page_id, page_data in pages.items():
            print(f"  Page ID: {page_id}")
            print(f"  Title: {page_data.get('title', 'N/A')}")
            
            extract = page_data.get('extract', '')
            
            if extract:
                print(f"  Контент: {len(extract)} символов")
                print()
                print("  Первые 300 символов:")
                print("  " + "-"*76)
                print("  " + extract[:300])
                print("  " + "-"*76)
                print()
                print("  ✓ Контент успешно получен!")
            else:
                print("  ⚠ Контент пустой")
                print(f"  Данные страницы: {page_data}")
    else:
        print(f"  ✗ Ошибка: статус {response.status_code}")

except Exception as e:
    print(f"  ✗ Исключение: {e}")
    import traceback
    traceback.print_exc()

print()

# Тест английской Wikipedia
print("[4/4] Тест English Wikipedia API...")
print()

try:
    api_url = "https://en.wikipedia.org/w/api.php"
    
    params = {
        'action': 'query',
        'prop': 'extracts',
        'exintro': True,
        'explaintext': True,
        'titles': 'Python (programming language)',
        'format': 'json'
    }
    
    print(f"  Статья: Python (programming language)")
    print()
    
    response = requests.get(api_url, params=params, timeout=10)
    
    print(f"  Статус: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        pages = data.get('query', {}).get('pages', {})
        
        for page_id, page_data in pages.items():
            extract = page_data.get('extract', '')
            
            if extract:
                print(f"  ✓ Получено {len(extract)} символов")
                print()
                print("  Первые 200 символов:")
                print("  " + "-"*76)
                print("  " + extract[:200])
                print("  " + "-"*76)
            else:
                print("  ⚠ Контент пустой")
    else:
        print(f"  ✗ Ошибка: {response.status_code}")

except Exception as e:
    print(f"  ✗ Исключение: {e}")

print()
print("="*80)
print("ИТОГИ ДИАГНОСТИКИ")
print("="*80)
print()

print("Если все тесты прошли успешно - Wikipedia API работает")
print("Если есть ошибки - возможные причины:")
print("  1. Блокировка Wikipedia в вашей сети")
print("  2. Проблемы с DNS")
print("  3. Требуется VPN")
print("  4. Проблемы с SSL сертификатами")
print()

print("Решения:")
print("  1. Проверьте доступ: открыть https://ru.wikipedia.org в браузере")
print("  2. Попробуйте VPN если Wikipedia заблокирована")
print("  3. Используйте альтернативный DNS (8.8.8.8)")
print()
print("="*80)

input("\nEnter для выхода...")
