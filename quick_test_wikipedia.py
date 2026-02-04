# -*- coding: utf-8 -*-
"""
✅ WORKING WEB LEARNING - С ПРАВИЛЬНЫМ USER-AGENT
"""

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

print("="*80)
print("✅ QUICK TEST - Wikipedia with User-Agent")
print("="*80)
print()

import requests
import time

# Создаем сессию с правильным User-Agent
session = requests.Session()
session.headers.update({
    'User-Agent': 'JARVIS-Learning/1.0 (Educational; Python) requests/2.31.0'
})

topic = "Python"

print(f"Тест на теме: {topic}")
print("-"*80)

try:
    # 1. Поиск
    print("\n[1/3] Поиск статьи...")
    
    api_url = "https://ru.wikipedia.org/w/api.php"
    
    search_params = {
        'action': 'opensearch',
        'search': topic,
        'limit': 1,
        'format': 'json'
    }
    
    response = session.get(api_url, params=search_params, timeout=15)
    
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 200:
        results = response.json()
        
        if len(results) >= 2 and results[1]:
            title = results[1][0]
            print(f"✓ Найдена статья: {title}")
            
            time.sleep(1)
            
            # 2. Получение контента
            print("\n[2/3] Получение контента...")
            
            content_params = {
                'action': 'query',
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True,
                'titles': title,
                'format': 'json'
            }
            
            response = session.get(api_url, params=content_params, timeout=15)
            
            print(f"Статус: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                pages = data.get('query', {}).get('pages', {})
                
                for page_data in pages.values():
                    extract = page_data.get('extract', '')
                    
                    if extract:
                        print(f"✓ Получено {len(extract)} символов")
                        print()
                        print("Первые 300 символов:")
                        print("─"*76)
                        print(extract[:300])
                        print("─"*76)
                        print()
                        print("✅ УСПЕХ! Wikipedia API работает!")
                    else:
                        print("⚠ Контент пустой")
            else:
                print(f"✗ Ошибка: {response.status_code}")
                print(response.text[:500])
        else:
            print("⚠ Результаты поиска пустые")
    else:
        print(f"✗ Ошибка поиска: {response.status_code}")
        print(response.text[:500])

except Exception as e:
    print(f"✗ Исключение: {e}")
    import traceback
    traceback.print_exc()

print()
print("-"*80)
print()

print("Если тест успешен - запускайте:")
print("  python working_web_learning.py")
print()
print("="*80)

input("\nEnter...")
