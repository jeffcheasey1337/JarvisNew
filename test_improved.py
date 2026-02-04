# -*- coding: utf-8 -*-
"""
🧪 ТЕСТ УЛУЧШЕННОЙ СИСТЕМЫ
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

print("="*80)
print("🧪 ТЕСТ IMPROVED WEB LEARNING SYSTEM v2.0")
print("="*80)
print()

# Импорт
print("[1/2] Импорт...")
try:
    from improved_web_learning import ImprovedAutonomousLearning
    print("  ✓ Модуль импортирован")
except Exception as e:
    print(f"  ✗ Ошибка: {e}")
    exit(1)

print()

# Тест
print("[2/2] Тестирование...")
print()

system = ImprovedAutonomousLearning()

# Одна тема для быстрого теста
test_topic = "Python"

print(f"Тест на теме: {test_topic}")
print("-"*80)

success = system.learn_topic(test_topic)

print("-"*80)
print()

if success:
    stats = system.get_stats()
    
    print("✅ УСПЕХ!")
    print()
    print(f"Источников собрано: {stats['collector']['sources_collected']}")
    print(f"Контента собрано: {stats['total_content']} символов")
    print(f"Embeddings создано: {stats['embeddings_created']}")
    print()
    print("Система работает!")
    print()
    print("Следующие шаги:")
    print("  python integrate_improved.py  - интеграция в JARVIS")
    print("  python -m jarvis              - запуск")
else:
    print("❌ ОШИБКА")
    print("Не удалось собрать информацию")

print()
print("="*80)

input("\nEnter для выхода...")
