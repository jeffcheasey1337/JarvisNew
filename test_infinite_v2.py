# -*- coding: utf-8 -*-
"""
🧪 ТЕСТ УЛУЧШЕННОЙ INFINITE LEARNING SYSTEM
С умным поиском и фильтрацией
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

print("="*80)
print("🧪 ТЕСТ УЛУЧШЕННОЙ СИСТЕМЫ v2.0")
print("="*80)
print()

print("Импорт модуля...")
try:
    from infinite_learning_system import InfiniteLearningSystem
    print("✓ Модуль импортирован")
except Exception as e:
    print(f"✗ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
    input("\nEnter...")
    exit(1)

print()
print("="*80)
print("УЛУЧШЕНИЯ В v2.0:")
print("="*80)
print()
print("✅ Умный поиск - пробует варианты запроса")
print("✅ Автоперевод - 'Тарантино' → 'Tarantino'")
print("✅ Фильтрация - убирает мусорные темы")
print("✅ Нормализация - 'Monty Python's' → 'Monty Python'")
print()

# Тестовые темы
print("="*80)
print("ТЕСТОВЫЕ ТЕМЫ:")
print("="*80)
print()

initial_topics = [
    "Python",
    "Квентин Тарантино",  # Тест транслитерации и перевода
    "Искусственный интеллект",
]

print("1. Python - должен найти везде")
print("2. Квентин Тарантино - тест умного поиска:")
print("   - Попробует 'Квентин Тарантино'")
print("   - Попробует 'Quentin Tarantino' (транслит)")
print("   - Попробует 'Тарантино'")
print("   - Попробует 'Tarantino'")
print("3. Искусственный интеллект")
print()

input("Enter для запуска теста...")

print()
print("="*80)
print("ЗАПУСК ОБУЧЕНИЯ (ограничено 5 темами)")
print("="*80)
print()

# Создаем систему
system = InfiniteLearningSystem(initial_topics=initial_topics)

# Запускаем
try:
    system.start_infinite_learning(max_topics=5)
except KeyboardInterrupt:
    print("\n⚠ Остановлено пользователем")
except Exception as e:
    print(f"\n✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*80)
print("РЕЗУЛЬТАТЫ ТЕСТА")
print("="*80)
print()

# Проверяем результаты
import json
from pathlib import Path

data_dir = Path('data/infinite_knowledge')

if data_dir.exists():
    files = list(data_dir.glob('*.json'))
    topic_files = [f for f in files if f.name != 'knowledge_graph.json']
    
    print(f"Изучено тем: {len(topic_files)}")
    print()
    
    if topic_files:
        print("Изученные темы:")
        for f in topic_files:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                sources = len(data.get('sources', []))
                chars = len(data.get('content', ''))
                entities = sum(len(v) for v in data.get('entities', {}).values())
                
                print(f"  ✓ {f.stem}")
                print(f"    Источников: {sources}")
                print(f"    Контент: {chars} символов")
                print(f"    Найдено сущностей: {entities}")
        
        print()
    
    # Граф знаний
    graph_file = data_dir / 'knowledge_graph.json'
    if graph_file.exists():
        with open(graph_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
            
            graph = graph_data.get('graph', {})
            
            print(f"Граф знаний:")
            print(f"  Тем в графе: {len(graph)}")
            print(f"  Связей: {sum(len(v) for v in graph.values())}")
            print()
            
            # Проверяем качество тем
            all_topics_in_graph = set()
            for topic, related in graph.items():
                all_topics_in_graph.add(topic)
                all_topics_in_graph.update(related)
            
            # Фильтруем плохие темы
            bad_topics = []
            for topic in all_topics_in_graph:
                if any(x in topic for x in ["'s", "tery", "tory"]):
                    bad_topics.append(topic)
            
            if bad_topics:
                print("⚠ Найдены плохие темы (нужна лучшая фильтрация):")
                for bad in bad_topics[:5]:
                    print(f"  - {bad}")
                print()
            else:
                print("✓ Все темы качественные!")
                print()

print("="*80)
print()

# Проверка успешности
if len(topic_files) >= 3:
    print("✅ ТЕСТ УСПЕШЕН!")
    print()
    print("Система работает отлично!")
    print("Умный поиск нашел информацию.")
    print()
    print("Следующий шаг:")
    print("  python integrate_infinite.py")
else:
    print("⚠ ЧАСТИЧНЫЙ УСПЕХ")
    print()
    print(f"Найдено {len(topic_files)} из 5 тем")
    print()
    if len(topic_files) > 0:
        print("Система работает, но можно улучшить:")
        print("  - Добавить больше вариантов поиска")
        print("  - Использовать Google/Bing API")
        print("  - Добавить кэширование результатов")
    else:
        print("Проверьте:")
        print("  - Интернет подключен")
        print("  - Wikipedia доступна")

print()
print("="*80)

input("\nEnter для выхода...")
