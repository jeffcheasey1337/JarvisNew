# -*- coding: utf-8 -*-
"""
JARVIS Continuous Learning WITH INFINITE WEB RESEARCH v2.0
Непрерывное обучение с улучшенной системой бесконечного сбора знаний
"""

import logging
import threading
import time

logger = logging.getLogger(__name__)

# Импорт компонентов
try:
    from .turbo import TurboLearningSystem
    TURBO_AVAILABLE = True
except:
    TURBO_AVAILABLE = False
    logger.warning("Turbo система недоступна")

try:
    from .topics_database import get_all_topics_flat
    TOPICS_AVAILABLE = True
except:
    TOPICS_AVAILABLE = False
    logger.warning("Topics database недоступна")

try:
    from .infinite_learning import InfiniteLearningSystem
    INFINITE_LEARNING_AVAILABLE = True
    logger.info("Infinite Learning v2.0 доступна")
except Exception as e:
    INFINITE_LEARNING_AVAILABLE = False
    logger.warning(f"Infinite Learning недоступна: {e}")


class ContinuousLearning:
    """
    Непрерывное обучение с бесконечным расширением знаний
    
    Возможности:
    - Поиск на 50+ языках Wikipedia
    - Умный поиск с вариантами запроса
    - Автоматическая транслитерация
    - Фильтрация мусорных тем
    - Бесконечное расширение базы знаний
    - GPU ускорение
    """
    
    def __init__(self, config=None, memory_system=None, nlp_processor=None):
        self.config = config or {}
        self.memory_system = memory_system
        self.nlp_processor = nlp_processor
        
        self.running = False
        self.learning_thread = None
        self.total_learned = 0
        
        # Turbo GPU система
        self.turbo_system = None
        if TURBO_AVAILABLE:
            try:
                logger.info("Инициализация Turbo GPU...")
                self.turbo_system = TurboLearningSystem(
                    batch_size=512,
                    num_workers=32
                )
                logger.info("Turbo GPU готова")
            except Exception as e:
                logger.error(f"Ошибка Turbo GPU: {e}")
        
        # Infinite Learning система
        self.infinite_learning = None
        if INFINITE_LEARNING_AVAILABLE:
            try:
                logger.info("Инициализация Infinite Learning v2.0...")
                
                # Получаем стартовые темы из базы
                initial_topics = []
                if TOPICS_AVAILABLE:
                    try:
                        all_topics = get_all_topics_flat()
                        # Берем первые 100 как стартовые
                        initial_topics = all_topics[:100]
                        logger.info(f"Загружено {len(initial_topics)} стартовых тем из базы")
                    except Exception as e:
                        logger.warning(f"Ошибка загрузки тем: {e}")
                
                if not initial_topics:
                    # Дефолтные темы если база недоступна
                    initial_topics = [
                        # Технологии
                        "Python", "JavaScript", "Machine Learning", "Artificial Intelligence",
                        "Blockchain", "Neural Networks", "Deep Learning", "Data Science",
                        
                        # Культура
                        "Квентин Тарантино", "Мартин Скорсезе", "Леонардо ДиКаприо",
                        "Sex Pistols", "The Beatles", "Pink Floyd",
                        
                        # Наука
                        "Квантовая физика", "Теория относительности", "Черные дыры",
                        "ДНК", "Генетика", "Эволюция",
                        
                        # Другое
                        "Философия", "История", "Космос", "Океан"
                    ]
                    logger.info(f"Используются дефолтные темы: {len(initial_topics)}")
                
                # Создаем систему
                self.infinite_learning = InfiniteLearningSystem(
                    turbo_system=self.turbo_system,
                    initial_topics=initial_topics
                )
                
                logger.info("Infinite Learning v2.0 готова к работе")
                logger.info(f"В очереди: {len(self.infinite_learning.topic_queue)} тем")
                
            except Exception as e:
                logger.error(f"Ошибка инициализации Infinite Learning: {e}")
                import traceback
                traceback.print_exc()
        
        logger.info("Continuous Learning инициализирована")
    
    async def start_continuous_learning(self):
        """Async запуск для JARVIS"""
        self.start()
    
    def start(self):
        """Запуск бесконечного обучения"""
        if self.running:
            logger.warning("Обучение уже запущено")
            return
        
        self.running = True
        
        self.learning_thread = threading.Thread(
            target=self._learning_loop,
            daemon=True,
            name="InfiniteLearning"
        )
        self.learning_thread.start()
        
        logger.info("Бесконечное обучение запущено")
    
    def stop(self):
        """Остановка обучения"""
        if not self.running:
            return
        
        self.running = False
        
        if self.learning_thread:
            self.learning_thread.join(timeout=5)
        
        if self.infinite_learning:
            total = len(self.infinite_learning.studied_topics)
            queue = len(self.infinite_learning.topic_queue)
            logger.info(f"Обучение остановлено")
            logger.info(f"Изучено тем: {total}")
            logger.info(f"В очереди: {queue}")
    
    def _learning_loop(self):
        """Основной цикл бесконечного обучения"""
        logger.info("="*80)
        logger.info("ЗАПУСК БЕСКОНЕЧНОГО ОБУЧЕНИЯ")
        logger.info("="*80)
        
        if self.infinite_learning:
            try:
                # Запускаем бесконечное обучение (без лимита тем)
                self.infinite_learning.start_infinite_learning(max_topics=None)
                
            except Exception as e:
                logger.error(f"Критическая ошибка обучения: {e}", exc_info=True)
        else:
            logger.warning("Infinite Learning недоступна - обучение невозможно")
        
        self.running = False
        logger.info("Цикл обучения завершен")
    
    def get_stats(self):
        """Получение статистики"""
        stats = {
            'running': self.running,
            'total_learned': 0,
            'queue_size': 0,
        }
        
        if self.infinite_learning:
            stats.update({
                'total_learned': len(self.infinite_learning.studied_topics),
                'queue_size': len(self.infinite_learning.topic_queue),
                'stats': self.infinite_learning.stats,
            })
        
        return stats
    
    def learn_topic(self, topic: str, category: str = "general"):
        """
        Добавление темы для изучения
        
        Args:
            topic: Тема для изучения
            category: Категория (не используется)
            
        Returns:
            True если тема добавлена
        """
        if self.infinite_learning:
            if topic not in self.infinite_learning.studied_topics:
                # Добавляем в начало очереди для приоритетного изучения
                self.infinite_learning.topic_queue.appendleft(topic)
                logger.info(f"Тема '{topic}' добавлена в очередь (приоритет)")
                return True
            else:
                logger.debug(f"Тема '{topic}' уже изучена")
                return False
        
        return False
