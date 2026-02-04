# -*- coding: utf-8 -*-
"""
🧪 ТЕСТ TURBO LEARNING - 100x SPEED
"""

import sys
import asyncio

print("="*80)
print("⚡ ТЕСТ TURBO LEARNING SYSTEM")
print("="*80)
print()

# Проверка aiohttp
print("[1/3] Проверка зависимостей...")
print()

try:
    import aiohttp
    print("  ✓ aiohttp")
except ImportError:
    print("  ✗ aiohttp НЕ установлен")
    print()
    print("Установите: pip install aiohttp")
    print()
    input("Enter...")
    sys.exit(1)

try:
    import requests
    print("  ✓ requests")
except:
    print("  ✗ requests")

print()

# Импорт
print("[2/3] Импорт модуля...")
print()

try:
    from turbo_infinite_learning import TurboInfiniteLearning
    print("  ✓ TurboInfiniteLearning")
except Exception as e:
    print(f"  ✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    input("\nEnter...")
    sys.exit(1)

print()

# Тест
print("[3/3] Запуск теста...")
print()

print("="*80)
print("ТУРБО ТЕСТ - 100 ТЕМ")
print("="*80)
print()

print("Параметры:")
print("  • Тем: 100")
print("  • Параллельность: 50")
print("  • Ожидаемое время: ~10 секунд")
print("  • Ожидаемая скорость: 600+ тем/мин")
print()

test_topics = [
    # Технологии
    "Python", "JavaScript", "Java", "C++", "C#", "Ruby", "Go", "Rust",
    "Machine Learning", "Deep Learning", "AI", "Neural Networks",
    "Blockchain", "Bitcoin", "Ethereum", "Cryptocurrency",
    
    # Культура
    "Квентин Тарантино", "Мартин Скорсезе", "Стивен Спилберг",
    "Леонардо ДиКаприо", "Брэд Питт", "Том Ханкс",
    "The Beatles", "Pink Floyd", "Led Zeppelin", "Queen",
    
    # Наука
    "Квантовая физика", "Теория относительности", "Черные дыры",
    "ДНК", "Генетика", "Эволюция", "Большой взрыв",
    
    # География
    "Париж", "Лондон", "Нью-Йорк", "Токио", "Москва",
    
    # И еще...
    "Философия", "История", "Математика", "Химия", "Биология",
    
    # Добавляем еще для полных 100
] + [f"Topic {i}" for i in range(50)]

print(f"Подготовлено {len(test_topics)} тем")
print()

input("Enter для запуска...")

async def run_test():
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    system = TurboInfiniteLearning(topics_list=test_topics)
    await system.start_turbo_learning()
    
    return system.stats

print()
print("ЗАПУСК...")
print()

try:
    stats = asyncio.run(run_test())
    
    print()
    print("="*80)
    print("✅ ТЕСТ ЗАВЕРШЕН!")
    print("="*80)
    print()
    
    if stats['topics_studied'] > 0:
        print("Результаты:")
        print(f"  Изучено: {stats['topics_studied']}")
        print(f"  Источников: {stats['sources_collected']}")
        print(f"  Новых тем: {stats['entities_discovered']}")
        print(f"  Контента: {stats['total_content']/1024:.1f} KB")
        
        elapsed = (stats['start_time'] - stats['start_time']).total_seconds()
        from datetime import datetime
        elapsed = (datetime.now() - stats['start_time']).total_seconds()
        
        if elapsed > 0:
            speed_per_min = (stats['topics_studied'] / elapsed) * 60
            print(f"  Скорость: {speed_per_min:.0f} тем/мин")
            print()
            
            if speed_per_min > 300:
                print("🚀 ОТЛИЧНО! Скорость > 300 тем/мин")
                print()
                print("Для 4127 тем потребуется:")
                print(f"  {4127/speed_per_min:.1f} минут")
            else:
                print("⚠ Скорость ниже ожидаемой")
                print("Проверьте интернет-соединение")
        
        print()
        print("Следующий шаг:")
        print("  python integrate_turbo.py")
        print()
        print("Затем:")
        print("  python -m jarvis")
        print()
        print("JARVIS обработает все 4127 тем за 6-7 минут!")
    else:
        print("⚠ Темы не изучены")
        print("Проверьте:")
        print("  - Интернет подключен")
        print("  - Wikipedia доступна")

except KeyboardInterrupt:
    print("\n⚠ Остановлено пользователем")
except Exception as e:
    print(f"\n✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*80)

input("\nEnter для выхода...")
