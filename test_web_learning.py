# -*- coding: utf-8 -*-
"""
ТЕСТ WEB LEARNING SYSTEM
Проверка автономной системы обучения из интернета
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("="*80)
print("ТЕСТ AUTONOMOUS WEB LEARNING SYSTEM")
print("="*80)
print()

# ============================================================================
# ПРОВЕРКА ЗАВИСИМОСТЕЙ
# ============================================================================

print("[1/4] Проверка зависимостей...")

missing_deps = []

try:
    import requests
    print("  OK: requests")
except ImportError:
    print("  MISSING: requests")
    missing_deps.append("requests")

try:
    import bs4
    print("  OK: beautifulsoup4")
except ImportError:
    print("  MISSING: beautifulsoup4")
    missing_deps.append("beautifulsoup4")

if missing_deps:
    print()
    print(f"Установите зависимости:")
    print(f"  pip install {' '.join(missing_deps)}")
    print()
    input("Enter после установки...")

print()

# ============================================================================
# ИМПОРТ МОДУЛЯ
# ============================================================================

print("[2/4] Импорт модуля...")

try:
    from autonomous_web_learning import AutonomousWebLearningSystem, WebKnowledgeCollector
    print("  OK: Модуль импортирован")
except ImportError as e:
    print(f"  ОШИБКА: {e}")
    print()
    print("Убедитесь что файл autonomous_web_learning.py в текущей папке")
    input("Enter...")
    sys.exit(1)

print()

# ============================================================================
# ТЕСТ СБОРЩИКА ЗНАНИЙ
# ============================================================================

print("[3/4] Тест сборщика знаний...")
print()

collector = WebKnowledgeCollector()

# Тестовая тема
test_topic = "Python programming language"

print(f"Тестовая тема: {test_topic}")
print("Сбор информации из интернета...")
print()

knowledge = collector.collect_knowledge_for_topic(
    test_topic,
    sources=['duckduckgo']  # Только DuckDuckGo для теста
)

print("Результаты:")
print(f"  Источников: {len(knowledge['sources'])}")
print(f"  Контента: {knowledge['total_text_length']} символов")

if knowledge['content']:
    print()
    print("Пример контента (первые 300 символов):")
    print("-"*80)
    print(knowledge['content'][0][:300])
    print("-"*80)

print()

# ============================================================================
# ТЕСТ ПОЛНОЙ СИСТЕМЫ
# ============================================================================

print("[4/4] Тест автономной системы...")
print()

system = AutonomousWebLearningSystem()

test_topics = [
    "Artificial Intelligence",
    "Machine Learning basics",
]

print(f"Тестируем на {len(test_topics)} темах")
print()

for i, topic in enumerate(test_topics):
    print(f"[{i+1}/{len(test_topics)}] {topic}")
    
    success = system.learn_topic_from_web(topic)
    
    if success:
        print(f"  OK: Собрана информация")
    else:
        print(f"  ОШИБКА: Не удалось собрать информацию")
    
    print()

# ============================================================================
# СТАТИСТИКА
# ============================================================================

print("="*80)
print("СТАТИСТИКА")
print("="*80)

stats = system.get_stats()

print(f"Тем изучено: {stats['topics_learned']}")
print(f"Контента собрано: {stats['total_content_collected']} символов")
print(f"Embeddings создано: {stats['embeddings_created']}")
print()

collector_stats = stats['collector']
print("Сборщик знаний:")
print(f"  Тем обработано: {collector_stats['topics_processed']}")
print(f"  Поисков выполнено: {collector_stats['searches_performed']}")
print(f"  Страниц спарсено: {collector_stats['pages_scraped']}")
print(f"  Знаний извлечено: {collector_stats['knowledge_extracted']}")
print(f"  Ошибок: {collector_stats['errors']}")

print()
print("="*80)
print()

print("ТЕСТ ЗАВЕРШЕН!")
print()

if stats['topics_learned'] > 0:
    print("OK: Система работает!")
    print()
    print("Следующие шаги:")
    print("  1. python integrate_web_learning.py  - интеграция в JARVIS")
    print("  2. python -m jarvis                  - запуск с Web Learning")
else:
    print("ПРОБЛЕМА: Система не смогла собрать информацию")
    print()
    print("Возможные причины:")
    print("  - Нет интернета")
    print("  - Сайты блокируют запросы")
    print("  - Нужно изменить User-Agent")

print()
print("="*80)

input("\nEnter для выхода...")
