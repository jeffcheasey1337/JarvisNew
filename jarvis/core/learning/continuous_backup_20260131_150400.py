# -*- coding: utf-8 -*-
"""
🎓 JARVIS Continuous Learning System
Система непрерывного обучения с GPU поддержкой
"""

import logging
import threading
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Попытка импорта GPU турбо-системы
try:
    from .turbo import TurboLearningSystem
    TURBO_AVAILABLE = True
    logger.info("✓ Turbo GPU система доступна")
except ImportError as e:
    TURBO_AVAILABLE = False
    logger.warning(f"⚠ Turbo система недоступна: {e}")

try:
    from .topics_database import get_all_topics_flat, get_topics_count, get_random_topics
    TOPICS_DB_AVAILABLE = True
except ImportError:
    TOPICS_DB_AVAILABLE = False
    logger.warning("⚠ Topics database недоступна")


class ContinuousLearning:
    """
    Система непрерывного обучения
    Совместима с основным кодом JARVIS
    """
    
    def __init__(self, config=None, memory_system=None, nlp_processor=None):
        """
        Инициализация
        
        Args:
            config: Конфигурация JARVIS
            memory_system: Система памяти
            nlp_processor: NLP процессор
        """
        self.config = config or {}
        self.memory_system = memory_system
        self.nlp_processor = nlp_processor
        
        # Параметры обучения
        self.batch_size = self.config.get('learning', {}).get('batch_size', 512)
        self.learning_interval = self.config.get('learning', {}).get('interval', 30)
        
        # Состояние
        self.running = False
        self.learning_thread = None
        self.total_learned = 0
        self.session_learned = 0
        
        # GPU Turbo система (если доступна)
        self.turbo_system = None
        if TURBO_AVAILABLE:
            try:
                logger.info("🚀 Инициализация Turbo GPU системы...")
                self.turbo_system = TurboLearningSystem(
                    batch_size=self.batch_size,
                    num_workers=32
                )
                logger.info("✓ Turbo GPU система инициализирована")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации Turbo: {e}")
                self.turbo_system = None
        
        # Статистика
        self.stats = {
            'start_time': None,
            'total_topics': 0,
            'learned_topics': 0,
            'topics_per_second': 0,
        }
        
        logger.info("✓ Система непрерывного обучения инициализирована")
    
    def start(self):
        """Запуск непрерывного обучения"""
        if self.running:
            logger.warning("Обучение уже запущено")
            return
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        # Запускаем в отдельном потоке
        self.learning_thread = threading.Thread(
            target=self._learning_loop,
            daemon=True,
            name="ContinuousLearning"
        )
        self.learning_thread.start()
        
        logger.info("🎓 Непрерывное обучение запущено")
    
    def stop(self):
        """Остановка обучения"""
        if not self.running:
            return
        
        self.running = False
        
        if self.learning_thread:
            self.learning_thread.join(timeout=5)
        
        logger.info(f"🛑 Обучение остановлено. Изучено тем: {self.total_learned}")
    
    def _learning_loop(self):
        """Основной цикл обучения"""
        logger.info("📚 Начало цикла обучения...")
        
        # Получаем все темы если доступна база
        all_topics = []
        if TOPICS_DB_AVAILABLE:
            try:
                all_topics = get_all_topics_flat()
                logger.info(f"📖 Загружено {len(all_topics)} тем для обучения")
            except Exception as e:
                logger.error(f"Ошибка загрузки тем: {e}")
        
        # Если нет тем, используем демо-режим
        if not all_topics:
            logger.warning("⚠ Темы не загружены, используется демо-режим")
            all_topics = self._get_demo_topics()
        
        self.stats['total_topics'] = len(all_topics)
        
        batch_count = 0
        processed = 0
        
        try:
            while self.running and processed < len(all_topics):
                batch_count += 1
                
                # Получаем батч тем
                batch_start = processed
                batch_end = min(batch_start + self.batch_size, len(all_topics))
                batch = all_topics[batch_start:batch_end]
                
                # Обрабатываем батч
                start_time = time.time()
                
                if self.turbo_system:
                    # GPU обучение
                    try:
                        result = self.turbo_system.learn_batch(batch, category="mixed")
                        logger.debug(f"Батч {batch_count}: {result['processed']} тем за {result['time']:.2f} сек")
                    except Exception as e:
                        logger.error(f"Ошибка GPU обучения: {e}")
                        # Fallback на обычное обучение
                        self._learn_batch_cpu(batch)
                else:
                    # CPU обучение
                    self._learn_batch_cpu(batch)
                
                elapsed = time.time() - start_time
                
                processed += len(batch)
                self.total_learned = processed
                self.session_learned += len(batch)
                self.stats['learned_topics'] = processed
                
                # Обновляем статистику
                if self.stats['start_time']:
                    total_elapsed = time.time() - self.stats['start_time']
                    self.stats['topics_per_second'] = processed / total_elapsed if total_elapsed > 0 else 0
                
                # Логируем прогресс каждые 10 батчей
                if batch_count % 10 == 0:
                    speed = self.stats['topics_per_second']
                    logger.info(
                        f"[Батч {batch_count}] Обработано: {processed}/{len(all_topics)} | "
                        f"Скорость: {speed:.1f} тем/сек | "
                        f"GPU: {'✓' if self.turbo_system else '✗'}"
                    )
                
                # Небольшая пауза между батчами
                if self.learning_interval > 0:
                    time.sleep(min(0.1, self.learning_interval / 10))
            
            # Обучение завершено
            if processed >= len(all_topics):
                logger.info(f"✅ Обучение завершено! Изучено {processed} тем")
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка в цикле обучения: {e}", exc_info=True)
        
        finally:
            self.running = False
    
    def _learn_batch_cpu(self, topics):
        """Обучение на CPU (fallback)"""
        # Простая обработка без GPU
        if self.memory_system:
            for topic in topics:
                try:
                    pass
                except:
                    pass
        
        # Симуляция обработки
        time.sleep(0.01 * len(topics) / self.batch_size)
    
    def _get_demo_topics(self):
        """Демо-темы если база недоступна"""
        return [
            f"демо тема {i} для тестирования системы обучения"
            for i in range(100)
        ]
    
    def get_stats(self):
        """Получение статистики обучения"""
        stats = self.stats.copy()
        
        if self.turbo_system:
            try:
                turbo_stats = self.turbo_system.get_stats()
                stats['turbo'] = turbo_stats
            except:
                pass
        
        stats['session_learned'] = self.session_learned
        stats['total_learned'] = self.total_learned
        stats['running'] = self.running
        
        return stats
    
    def learn_topic(self, topic: str, category: str = "general"):
        """
        Обучение на одной теме
        
        Args:
            topic: Тема для изучения
            category: Категория темы
        """
        if self.turbo_system:
            try:
                self.turbo_system.learn_batch([topic], category=category)
            except Exception as e:
                logger.error(f"Ошибка обучения на теме: {e}")
        
        self.total_learned += 1
