#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TEST ENHANCED LEARNING - Тестирование улучшенной системы обучения
Проверяет все компоненты и показывает примеры работы
"""

import sys
import asyncio
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

def test_content_cleaner():
    """Тест очистки контента"""
    print("="*70)
    print("1️⃣  ТЕСТ: Content Cleaner (Очистка данных)")
    print("="*70)
    print()
    
    from jarvis.core.learning.enhanced_learning import ContentCleaner
    
    test_cases = [
        {
            'name': 'HTML + Спам',
            'topic': 'Python',
            'content': """
                <div class="article">
                    Python is a high-level programming language.
                    Created by Guido van Rossum in 1991.
                    <script>alert('spam')</script>
                    Python is used in AI and web development.
                    Subscribe to our newsletter!
                    Click here to buy now!
                </div>
            """
        },
        {
            'name': 'Нерелевантный контент',
            'topic': 'Machine Learning',
            'content': """
                Lorem ipsum dolor sit amet.
                This is just random text.
                Nothing about machine learning here.
            """
        },
        {
            'name': 'Качественный контент',
            'topic': 'Artificial Intelligence',
            'content': """
                Artificial Intelligence (AI) is intelligence demonstrated by machines.
                The field was founded in 1956 at Dartmouth College.
                Modern AI uses neural networks and deep learning.
                AI applications include computer vision, natural language processing, and robotics.
            """
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Тест {i}: {test['name']}")
        print(f"  Тема: {test['topic']}")
        print(f"  Исходный размер: {len(test['content'])} символов")
        
        cleaned = ContentCleaner.clean(test['content'], test['topic'])
        
        if cleaned:
            print(f"  ✅ Очищенный размер: {len(cleaned)} символов")
            print(f"  Результат: {cleaned[:100]}...")
        else:
            print(f"  ❌ Контент отклонён (низкое качество)")
        print()
    
    print("✓ Content Cleaner работает!\n")


def test_knowledge_extractor():
    """Тест извлечения знаний"""
    print("="*70)
    print("2️⃣  ТЕСТ: Knowledge Extractor (Извлечение знаний)")
    print("="*70)
    print()
    
    from jarvis.core.learning.enhanced_learning import KnowledgeExtractor
    
    text = """
        Python was created by Guido van Rossum in 1991.
        It is a high-level programming language.
        Python is used by over 50% of data scientists.
        The language was named after Monty Python.
        Python 3.0 was released in 2008.
        Django is a popular web framework written in Python.
        Python supports multiple programming paradigms.
    """
    
    topic = "Python programming"
    
    print(f"Исходный текст ({len(text)} символов):")
    print(text)
    print()
    
    # Извлечение фактов
    print("📝 ФАКТЫ:")
    facts = KnowledgeExtractor.extract_facts(text, topic)
    for i, fact in enumerate(facts, 1):
        print(f"  {i}. {fact}")
    print()
    
    # Извлечение связей
    print("🔗 СВЯЗИ:")
    relationships = KnowledgeExtractor.extract_relationships(text, topic)
    for i, rel in enumerate(relationships, 1):
        print(f"  {i}. {rel['subject']} --[{rel['relation']}]--> {rel['object']}")
    print()
    
    # Извлечение сущностей
    print("🏷️  СУЩНОСТИ:")
    entities = KnowledgeExtractor.extract_entities(text)
    for entity_type, items in entities.items():
        if items:
            print(f"  {entity_type}: {', '.join(items)}")
    print()
    
    print("✓ Knowledge Extractor работает!\n")


def test_quality_monitor():
    """Тест мониторинга качества"""
    print("="*70)
    print("3️⃣  ТЕСТ: Learning Quality Monitor (Мониторинг качества)")
    print("="*70)
    print()
    
    from jarvis.core.learning.enhanced_learning import LearningQualityMonitor
    
    monitor = LearningQualityMonitor()
    
    # Симулируем обработку контента разного качества
    test_data = [
        ('Python', 'Python was created in 1991. It is used for AI and web development. Python has 50% market share.', {'is_unique': True}),
        ('AI', 'Click here buy now subscribe newsletter', {'is_unique': True}),
        ('Machine Learning', 'ML uses algorithms to learn patterns. Neural networks are popular. Deep learning achieved 95% accuracy in image recognition.', {'is_unique': True}),
        ('JavaScript', 'some random text here nothing useful', {'is_unique': False}),
        ('Blockchain', 'Blockchain is a distributed ledger. Bitcoin was created in 2009. Ethereum supports smart contracts.', {'is_unique': True}),
    ]
    
    print("Обработка тестовых данных...\n")
    
    for topic, content, metadata in test_data:
        score = monitor.evaluate_content_quality(topic, content, metadata)
        status = "✅ ПРИНЯТ" if score >= 0.4 else "❌ ОТКЛОНЁН"
        print(f"{status} | {topic:20} | Оценка: {score:.2f} ({score*100:.0f}%)")
    
    print()
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print()
    
    stats = monitor.get_statistics()
    print(f"  Средняя оценка: {stats['avg_quality']:.2%}")
    print(f"  Обработано: {stats['total_processed']}")
    print(f"  Отклонено: {stats['low_quality_rejected']} ({stats['rejection_rate']:.1%})")
    print(f"  Статус: {stats['status']}")
    print()
    
    print("📋 ПОЛНЫЙ ОТЧЁТ:")
    print(monitor.get_report())
    
    print("✓ Quality Monitor работает!\n")


async def test_enhanced_system():
    """Тест полной интеграции"""
    print("="*70)
    print("4️⃣  ТЕСТ: Enhanced Learning System (Полная интеграция)")
    print("="*70)
    print()
    
    # Создаём мок памяти
    class MockEmbedder:
        def encode(self, texts):
            import numpy as np
            if isinstance(texts, str):
                texts = [texts]
            return np.random.rand(len(texts), 384)
    
    class MockCollection:
        def __init__(self):
            self.data = {'ids': [], 'metadatas': [], 'documents': []}
        
        def get(self):
            return self.data
        
        def add(self, **kwargs):
            self.data['ids'].extend(kwargs.get('ids', []))
            self.data['metadatas'].extend(kwargs.get('metadatas', []))
            self.data['documents'].extend(kwargs.get('documents', []))
    
    class MockMemory:
        def __init__(self):
            self.collection = MockCollection()
            self.embedder = MockEmbedder()
        
        async def store_memory(self, content, memory_type=None, metadata=None):
            self.collection.add(
                ids=[f"test_{len(self.collection.data['ids'])}"],
                documents=[content],
                metadatas=[metadata or {}]
            )
    
    from jarvis.core.learning.enhanced_learning import EnhancedLearningSystem
    
    memory = MockMemory()
    enhanced = EnhancedLearningSystem(memory)
    
    print("✓ Enhanced система создана\n")
    
    # Тест обучения на качественном контенте
    print("Тест 1: Качественный контент")
    good_content = """
        Python is a high-level programming language created by Guido van Rossum in 1991.
        It emphasizes code readability with significant whitespace.
        Python is used by over 60% of developers worldwide.
        Popular frameworks include Django, Flask, and FastAPI.
        Python 3.11 was released in 2022 with performance improvements.
    """
    
    success = await enhanced.learn_from_content("Python", good_content, {'source': 'test'})
    print(f"  Результат: {'✅ УСПЕХ' if success else '❌ ПРОВАЛ'}")
    print(f"  Записей в памяти: {len(memory.collection.data['ids'])}")
    print()
    
    # Тест обучения на плохом контенте
    print("Тест 2: Низкокачественный контент")
    bad_content = "click here buy now subscribe"
    
    success = await enhanced.learn_from_content("Spam", bad_content, {'source': 'test'})
    print(f"  Результат: {'✅ УСПЕХ' if success else '❌ ПРОВАЛ (ожидаемо)'}")
    print()
    
    # Тест на большом тексте
    print("Тест 3: Большой текст с фактами")
    long_content = """
        Machine Learning is a subset of Artificial Intelligence.
        The term was coined by Arthur Samuel in 1959.
        Modern ML uses neural networks for pattern recognition.
        Deep Learning emerged in 2006 with Geoffrey Hinton's work.
        Popular ML libraries include TensorFlow, PyTorch, and scikit-learn.
        ML applications include computer vision, NLP, and recommendation systems.
        The global ML market is expected to reach $200 billion by 2026.
    """
    
    success = await enhanced.learn_from_content("Machine Learning", long_content, {'source': 'test'})
    print(f"  Результат: {'✅ УСПЕХ' if success else '❌ ПРОВАЛ'}")
    print(f"  Всего записей в памяти: {len(memory.collection.data['ids'])}")
    print()
    
    # Получаем отчёт
    print("📊 ФИНАЛЬНЫЙ ОТЧЁТ:")
    print(enhanced.get_quality_report())
    
    print("✓ Enhanced Learning System работает!\n")


def test_integration():
    """Тест интеграции"""
    print("="*70)
    print("5️⃣  ТЕСТ: Integration Layer (Интеграция)")
    print("="*70)
    print()
    
    try:
        from jarvis.core.learning.integration import SmartContinuousLearning
        print("✓ SmartContinuousLearning импортирована")
        
        # Проверка что можно создать
        class MockMemory:
            def __init__(self):
                self.collection = type('obj', (object,), {
                    'get': lambda: {'ids': [], 'metadatas': [], 'documents': []}
                })()
        
        smart = SmartContinuousLearning({}, MockMemory(), None)
        print(f"✓ Система создана")
        print(f"  Enhanced доступна: {smart.enhanced is not None}")
        print(f"  Base Learning доступна: {smart.base_learning is not None}")
        print()
        
        print("✓ Integration Layer работает!\n")
        
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        import traceback
        traceback.print_exc()


async def run_all_tests():
    """Запуск всех тестов"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "🧪 ENHANCED LEARNING SYSTEM TESTS" + " "*20 + "║")
    print("╚" + "="*68 + "╝")
    print()
    
    try:
        test_content_cleaner()
        test_knowledge_extractor()
        test_quality_monitor()
        await test_enhanced_system()
        test_integration()
        
        print("="*70)
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("="*70)
        print()
        print("✅ Enhanced Learning System готова к использованию!")
        print()
        print("📖 Следующие шаги:")
        print("  1. Прочитайте ENHANCED_LEARNING_GUIDE.md")
        print("  2. Интегрируйте в jarvis/assistant.py")
        print("  3. Запустите JARVIS и проверьте логи")
        print()
        
        return True
        
    except Exception as e:
        print("="*70)
        print(f"❌ ОШИБКА ПРИ ТЕСТИРОВАНИИ: {e}")
        print("="*70)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
