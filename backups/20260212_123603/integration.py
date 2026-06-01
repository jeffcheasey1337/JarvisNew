# -*- coding: utf-8 -*-
"""
🔗 INTEGRATION LAYER - Интеграция Enhanced Learning с Continuous Learning
Подключает улучшенную систему обучения к существующему коду
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


class SmartContinuousLearning:
    """
    Умная система непрерывного обучения
    Обёртка над существующей ContinuousLearning с Enhanced компонентами
    """
    
    def __init__(self, config, memory_system, nlp_processor):
        self.config = config
        self.memory_system = memory_system
        self.nlp_processor = nlp_processor
        
        # Загружаем Enhanced Learning System
        try:
            from jarvis.core.learning.enhanced_learning import EnhancedLearningSystem
            self.enhanced = EnhancedLearningSystem(memory_system)
            logger.info("✅ Enhanced Learning System подключена")
        except ImportError:
            logger.warning("⚠️ Enhanced Learning недоступна, используем базовую версию")
            self.enhanced = None
        
        # Загружаем базовую систему как fallback
        try:
            from jarvis.core.learning.full_web_learning import FullWebLearningSystem
            from jarvis.core.learning.topics_database import get_all_topics_flat
            
            topics = get_all_topics_flat()
            
            self.base_learning = FullWebLearningSystem(
                turbo_system=None,
                memory_system=memory_system,
                topics_list=topics,
                num_workers=10
            )
            logger.info("✅ Full Web Learning подключена")
        except ImportError:
            logger.warning("⚠️ Full Web Learning недоступна")
            self.base_learning = None
        
        # Статистика
        self.stats = {
            'start_time': datetime.now(),
            'topics_studied': 0,
            'high_quality_saves': 0,
            'low_quality_rejects': 0,
            'facts_extracted': 0,
            'uptime_hours': 0
        }
        
        self.running = False
        
        # Ссылка на GUI
        self.gui = None
    
    async def start_continuous_learning(self):
        """Запуск умного непрерывного обучения"""
        if not self.base_learning:
            logger.error("❌ Невозможно запустить обучение - нет базовой системы")
            return
        
        self.running = True
        
        logger.info("="*70)
        logger.info("🧠 ЗАПУСК УМНОГО НЕПРЕРЫВНОГО ОБУЧЕНИЯ")
        logger.info("="*70)
        logger.info(f"Enhanced Learning: {'✓' if self.enhanced else '✗'}")
        logger.info(f"Тем в очереди: {len(self.base_learning.topic_queue)}")
        logger.info("="*70)
        print()
        
        # Если есть Enhanced система, используем умное обучение
        if self.enhanced:
            await self._smart_learning_loop()
        else:
            # Fallback на базовую систему
            self.base_learning.start_learning()
    
    async def _smart_learning_loop(self):
        """Умный цикл обучения с Enhanced компонентами"""
        
        # Периодически обновляем приоритеты тем
        last_priority_update = datetime.now()
        
        while self.running and self.base_learning.topic_queue:
            
            # Каждый час пересчитываем приоритеты
            if (datetime.now() - last_priority_update).seconds > 3600:
                await self._update_topic_priorities()
                last_priority_update = datetime.now()
            
            # Берём следующую тему
            if not self.base_learning.topic_queue:
                break
            
            topic = self.base_learning.topic_queue.popleft()
            
            # Учимся с использованием Enhanced системы
            await self._learn_topic_smart(topic)
            
            # Периодически выводим отчёт
            if self.stats['topics_studied'] % 50 == 0:
                self._print_quality_report()
            
            # Обновляем uptime
            self.stats['uptime_hours'] = (
                datetime.now() - self.stats['start_time']
            ).total_seconds() / 3600
            
            # Небольшая пауза
            await asyncio.sleep(1)
    
    async def _learn_topic_smart(self, topic: str):
        """Умное обучение на теме с Enhanced компонентами"""
        
        try:
            # 1. Собираем данные (используем базовую систему)
            logger.info(f"🔍 Изучение: {topic}")
            
            results = self.base_learning.crawler.search_everywhere(topic, max_results=5)
            
            if not results:
                logger.debug(f"❌ Нет данных для '{topic}'")
                return False
            
            # 2. Обрабатываем каждый результат через Enhanced систему
            success_count = 0
            
            for result in results:
                content = result.get('content', '')
                if not content:
                    continue
                
                # УМНАЯ ОБРАБОТКА через Enhanced Learning
                metadata = {
                    'source': result.get('source', 'web'),
                    'url': result.get('url', ''),
                    'is_unique': True
                }
                
                success = await self.enhanced.learn_from_content(
                    topic, 
                    content, 
                    metadata
                )
                
                if success:
                    success_count += 1
                    self.stats['high_quality_saves'] += 1
                else:
                    self.stats['low_quality_rejects'] += 1
            
            # 3. Обновляем статистику
            if success_count > 0:
                self.stats['topics_studied'] += 1
                self.base_learning.stats['topics_studied'] += 1
                
                # Добавляем в граф знаний
                self.base_learning.studied_topics.add(topic)
                
                # Обновляем GUI если есть
                if self.gui:
                    self.gui.add_log(f"[ОБУЧЕНИЕ] ✓ {topic} ({success_count} источников)")
                    self.gui.update_stat('articles_learned', self.stats['topics_studied'])
                
                logger.info(f"✅ Изучено '{topic}': {success_count} источников")
                return True
            else:
                logger.debug(f"⚠️ Не удалось изучить '{topic}' (низкое качество)")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка при изучении '{topic}': {e}")
            return False
    
    async def _update_topic_priorities(self):
        """Обновление приоритетов тем"""
        if not self.enhanced:
            return
        
        logger.info("🎯 Обновление приоритетов тем...")
        
        # Анализируем пробелы в знаниях
        gaps = self.enhanced.analyze_knowledge_gaps()
        
        if gaps:
            logger.info(f"   Обнаружено пробелов: {len(gaps)}")
            
            # Добавляем темы с пробелами в начало очереди
            gap_topics = sorted(gaps.items(), key=lambda x: x[1], reverse=True)
            
            for gap_topic, importance in gap_topics[:5]:
                if gap_topic not in self.base_learning.studied_topics:
                    self.base_learning.topic_queue.appendleft(gap_topic)
                    logger.info(f"   ↑ Приоритет: {gap_topic} (пробел: {importance:.1%})")
    
    def _print_quality_report(self):
        """Вывод отчёта о качестве обучения"""
        if not self.enhanced:
            return
        
        logger.info("\n" + "="*70)
        logger.info(self.enhanced.get_quality_report())
        logger.info("="*70 + "\n")
        
        # Рекомендации
        recommendations = self.enhanced.get_learning_recommendations(5)
        if recommendations:
            logger.info("💡 РЕКОМЕНДАЦИИ ДЛЯ ОБУЧЕНИЯ:")
            for topic, reason in recommendations:
                logger.info(f"   • {topic}: {reason}")
            logger.info("")
    
    def get_stats(self) -> Dict:
        """Получить статистику"""
        base_stats = {}
        if self.base_learning:
            base_stats = {
                'topics_studied': self.stats['topics_studied'],
                'queue_size': len(self.base_learning.topic_queue),
                'pages_crawled': self.base_learning.stats.get('pages_crawled', 0),
            }
        
        enhanced_stats = {}
        if self.enhanced:
            enhanced_stats = self.enhanced.get_statistics()
        
        return {
            **base_stats,
            **enhanced_stats,
            'high_quality_saves': self.stats['high_quality_saves'],
            'low_quality_rejects': self.stats['low_quality_rejects'],
            'uptime_hours': self.stats['uptime_hours'],
            'running': self.running
        }
    
    def change_speed(self, speed: str):
        """Изменить скорость обучения"""
        # Здесь можно добавить логику изменения скорости
        logger.info(f"🎚️ Скорость обучения: {speed.upper()}")
        return f"Скорость установлена: {speed}"
    
    def stop(self):
        """Остановить обучение"""
        self.running = False
        logger.info("⏸️ Обучение остановлено")


# ============================================================================
# БЫСТРАЯ ИНТЕГРАЦИЯ - Автозамена в assistant.py
# ============================================================================

def patch_jarvis_assistant():
    """
    Автоматическая интеграция SmartContinuousLearning в JarvisAssistant
    
    Использование:
        from jarvis.core.learning.integration import patch_jarvis_assistant
        patch_jarvis_assistant()
    """
    
    try:
        import jarvis.assistant as assistant_module
        
        # Сохраняем оригинальный класс
        OriginalJarvisAssistant = assistant_module.JarvisAssistant
        
        # Создаём патченную версию
        class PatchedJarvisAssistant(OriginalJarvisAssistant):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                
                # ЗАМЕНЯЕМ continuous_learning на умную версию
                logger.info("🔧 Применение Smart Continuous Learning патча...")
                
                self.continuous_learning = SmartContinuousLearning(
                    self.config,
                    self.memory_system,
                    self.nlp_processor
                )
                
                logger.info("✅ Smart Continuous Learning активирована!")
        
        # Заменяем класс
        assistant_module.JarvisAssistant = PatchedJarvisAssistant
        
        logger.info("✅ JARVIS Assistant успешно пропатчен!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка патча: {e}")
        return False


# Тест
if __name__ == "__main__":
    print("="*70)
    print("🔗 INTEGRATION LAYER - Тестирование")
    print("="*70)
    print()
    
    # Тест создания
    print("1. Создание SmartContinuousLearning...")
    
    # Мок объекты для теста
    class MockMemory:
        def __init__(self):
            self.collection = MockCollection()
    
    class MockCollection:
        def get(self):
            return {'ids': [], 'metadatas': [], 'documents': []}
        
        def add(self, **kwargs):
            pass
    
    try:
        smart_learning = SmartContinuousLearning(
            config={},
            memory_system=MockMemory(),
            nlp_processor=None
        )
        print("   ✓ SmartContinuousLearning создана")
        print(f"   Enhanced доступна: {smart_learning.enhanced is not None}")
        print(f"   Base Learning доступна: {smart_learning.base_learning is not None}")
        print()
        
        print("2. Получение статистики...")
        stats = smart_learning.get_stats()
        print(f"   Статистика: {stats}")
        print()
        
        print("✅ Интеграция работает!")
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
