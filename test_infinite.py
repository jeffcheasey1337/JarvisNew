# -*- coding: utf-8 -*-
"""
🧪 ТЕСТ INFINITE LEARNING SYSTEM
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

print("="*80)
print("🧪 ТЕСТ БЕСКОНЕЧНОЙ СИСТЕМЫ ОБУЧЕНИЯ")
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
print("ТЕСТОВЫЙ ЗАПУСК")
print("="*80)
print()

# Начальные темы
initial_topics = [
    "Python",
    "Квентин Тарантино",
]

print(f"Начальные темы: {initial_topics}")
print()

# Создаем систему
system = InfiniteLearningSystem(initial_topics=initial_topics)

print("="*80)
print("ЗАПУСК ОБУЧЕНИЯ (ограничено 3 темами для теста)")
print("="*80)
print()

# Запускаем с лимитом 3 темы
try:
    system.start_infinite_learning(max_topics=3)
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

# Показываем что собрали
import json
from pathlib import Path

data_dir = Path('data/infinite_knowledge')

if data_dir.exists():
    files = list(data_dir.glob('*.json'))
    
    # Исключаем граф знаний
    topic_files = [f for f in files if f.name != 'knowledge_graph.json']
    
    print(f"Изучено тем: {len(topic_files)}")
    print()
    
    if topic_files:
        print("Примеры изученных тем:")
        for f in topic_files[:5]:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                topic = data.get('content', '')[:50]
                sources = len(data.get('sources', []))
                entities = sum(len(v) for v in data.get('entities', {}).values())
                
                print(f"  • {f.stem}")
                print(f"    Источников: {sources}")
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
            
            if graph:
                print("Примеры связей:")
                for topic, related in list(graph.items())[:3]:
                    print(f"  {topic} → {list(related)[:3]}")
else:
    print("⚠ Данные не найдены")

print()
print("="*80)
print()

if topic_files and len(topic_files) > 0:
    print("✅ ТЕСТ УСПЕШЕН!")
    print()
    print("Система работает! Можно интегрировать в JARVIS:")
    print("  python integrate_infinite.py")
else:
    print("⚠ ПРОБЛЕМЫ")
    print()
    print("Проверьте:")
    print("  1. Интернет подключен")
    print("  2. Wikipedia доступна")
    print("  3. Нет блокировок")

print()
print("="*80)

input("\nEnter для выхода...")
