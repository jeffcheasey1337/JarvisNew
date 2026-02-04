# -*- coding: utf-8 -*-
"""
JARVIS Continuous Learning WITH HYBRID SYSTEM
10x-15x скорость!
"""

import logging
import threading

logger = logging.getLogger(__name__)

try:
    from .turbo import TurboLearningSystem
    TURBO_GPU_AVAILABLE = True
except:
    TURBO_GPU_AVAILABLE = False

try:
    from .topics_database import get_all_topics_flat
    TOPICS_AVAILABLE = True
except:
    TOPICS_AVAILABLE = False

try:
    from .hybrid_learning import HybridLearningSystem
    HYBRID_AVAILABLE = True
    logger.info("⚡ Hybrid Learning доступна")
except Exception as e:
    HYBRID_AVAILABLE = False
    logger.warning(f"Hybrid Learning недоступна: {e}")


class ContinuousLearning:
    """Гибридное обучение - 10x-15x быстрее!"""
    
    def __init__(self, config=None, memory_system=None, nlp_processor=None):
        self.config = config or {}
        self.memory_system = memory_system
        self.nlp_processor = nlp_processor
        
        self.running = False
        self.learning_thread = None
        
        # Turbo GPU
        self.turbo_gpu = None
        if TURBO_GPU_AVAILABLE:
            try:
                logger.info("Инициализация Turbo GPU...")
                self.turbo_gpu = TurboLearningSystem(batch_size=1024, num_workers=32)
                logger.info("Turbo GPU готова")
            except Exception as e:
                logger.error(f"Ошибка Turbo GPU: {e}")
        
        # Hybrid Learning
        self.hybrid_learning = None
        if HYBRID_AVAILABLE:
            try:
                logger.info("Инициализация Hybrid Learning...")
                
                # Загружаем ВСЕ темы
                all_topics = []
                if TOPICS_AVAILABLE:
                    try:
                        all_topics = get_all_topics_flat()
                        logger.info(f"Загружено {len(all_topics)} тем из базы")
                    except:
                        pass
                
                if not all_topics:
                    all_topics = ["Python", "AI", "Machine Learning"]
                
                self.hybrid_learning = HybridLearningSystem(
                    turbo_system=self.turbo_gpu,
                    topics_list=all_topics,
                    num_workers=15  # 15 потоков
                )
                
                logger.info(f"⚡ Hybrid готова ({len(all_topics)} тем, 15 потоков)")
            except Exception as e:
                logger.error(f"Ошибка Hybrid: {e}")
        
        logger.info("Continuous Learning готова")
    
    async def start_continuous_learning(self):
        """Async запуск"""
        self.start()
    
    def start(self):
        """Запуск гибридного обучения"""
        if self.running:
            return
        
        self.running = True
        self.learning_thread = threading.Thread(target=self._loop, daemon=True)
        self.learning_thread.start()
        logger.info("⚡ Hybrid обучение запущено")
    
    def stop(self):
        """Остановка"""
        self.running = False
        if self.learning_thread:
            self.learning_thread.join(timeout=5)
        
        if self.hybrid_learning:
            studied = len(self.hybrid_learning.studied_topics)
            logger.info(f"Обучение остановлено. Изучено: {studied}")
    
    def _loop(self):
        """Цикл обучения"""
        if self.hybrid_learning:
            try:
                self.hybrid_learning.start_hybrid_learning()
            except Exception as e:
                logger.error(f"Ошибка: {e}", exc_info=True)
        
        self.running = False
    
    def get_stats(self):
        """Статистика"""
        stats = {'running': self.running}
        
        if self.hybrid_learning:
            stats.update({
                'total_learned': len(self.hybrid_learning.studied_topics),
                'queue_size': len(self.hybrid_learning.topic_queue),
                'stats': self.hybrid_learning.stats,
            })
        
        return stats
    
    def learn_topic(self, topic: str, category: str = "general"):
        """Добавление темы"""
        if self.hybrid_learning and topic not in self.hybrid_learning.studied_topics:
            self.hybrid_learning.topic_queue.appendleft(topic)
            return True
        return False
