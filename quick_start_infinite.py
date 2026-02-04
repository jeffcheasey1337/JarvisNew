# -*- coding: utf-8 -*-
"""
🚀 БЫСТРЫЙ СТАРТ - INFINITE LEARNING
Пошаговый запуск системы бесконечного обучения
"""

import sys
from pathlib import Path

print("="*80)
print("🚀 INFINITE LEARNING - БЫСТРЫЙ СТАРТ")
print("="*80)
print()

# Проверка зависимостей
print("[1/5] Проверка зависимостей...")
print()

missing = []

try:
    import requests
    print("  ✓ requests")
except:
    print("  ✗ requests")
    missing.append("requests")

try:
    import bs4
    print("  ✓ beautifulsoup4")
except:
    print("  ✗ beautifulsoup4")
    missing.append("beautifulsoup4")

if missing:
    print()
    print(f"Установите: pip install {' '.join(missing)}")
    print()
    input("Enter после установки...")

print()

# Проверка файлов
print("[2/5] Проверка файлов...")
print()

root = Path.cwd()

files_needed = {
    'infinite_learning_system.py': 'Основной модуль',
    'test_infinite.py': 'Тестовый скрипт',
    'integrate_infinite.py': 'Интеграция в JARVIS',
}

all_ok = True
for filename, description in files_needed.items():
    filepath = root / filename
    if filepath.exists():
        print(f"  ✓ {filename}")
    else:
        print(f"  ✗ {filename} - {description}")
        all_ok = False

if not all_ok:
    print()
    print("Скачайте все файлы!")
    input("Enter...")
    sys.exit(1)

print()

# План действий
print("[3/5] План действий:")
print()
print("  1. Тест системы (3 темы, ~2 мин)")
print("     python test_infinite.py")
print()
print("  2. Интеграция в JARVIS")
print("     python integrate_infinite.py")
print()
print("  3. Запуск JARVIS")
print("     python -m jarvis")
print()

# Что будет происходить
print("[4/5] Что будет происходить:")
print()
print("  Стартовые темы (из базы):")
print("    • Python")
print("    • Квентин Тарантино")
print("    • Искусственный интеллект")
print("    • ... еще 97 тем")
print()
print("  Для каждой темы:")
print("    1. Поиск в Wikipedia (50+ языков)")
print("    2. Краулинг веб-страниц")
print("    3. Извлечение упоминаний")
print("    4. Добавление новых тем в очередь")
print("    5. Создание embeddings на GPU")
print("    6. Обновление графа знаний")
print()
print("  Пример расширения:")
print("    'Тарантино' → находит:")
print("      • Ума Турман")
print("      • Криминальное чтиво")
print("      • Харви Вайнштейн")
print("      → добавляет в очередь")
print()
print("    'Ума Турман' → находит:")
print("      • Kill Bill")
print("      • Итан Хоук")
print("      → добавляет в очередь")
print()
print("    И так БЕСКОНЕЧНО!")
print()

# Производительность
print("[5/5] Производительность:")
print()
print("  Одна тема:")
print("    • Wikipedia (50 языков): ~5-10 сек")
print("    • Веб-краулинг: ~3-5 сек")
print("    • Анализ сущностей: ~1 сек")
print("    • Embeddings (GPU): ~1 сек")
print("    • ИТОГО: ~10-15 сек/тема")
print()
print("  Прогноз на 1000 тем:")
print("    • Время: ~3-4 часа")
print("    • Найдено новых тем: ~2000-5000")
print("    • Общая база: 3000-6000 тем")
print()
print("  За сутки работы:")
print("    • ~6000 тем изучено")
print("    • ~20000 новых тем найдено")
print("    • База: 26000+ тем")
print()

print("="*80)
print()

choice = input("Запустить тест прямо сейчас? (y/n): ")

if choice.lower() == 'y':
    print()
    print("Запуск теста...")
    print()
    
    import subprocess
    subprocess.run([sys.executable, 'test_infinite.py'])
else:
    print()
    print("Запустите вручную:")
    print("  python test_infinite.py")

print()
print("="*80)
