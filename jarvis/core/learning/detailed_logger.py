# -*- coding: utf-8 -*-
"""
Patch для turbo.py - добавление детального логирования
"""

import logging
import time
from datetime import datetime

# Настройка детального логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('logs/turbo_detailed.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('TurboLearning')

class DetailedTurboLearning:
    """Расширенная версия TurboLearningSystem с детальными логами"""
    
    def __init__(self, original_system):
        self.system = original_system
        self.batch_count = 0
        self.total_items = 0
        self.start_time = None
    
    def learn_batch(self, items):
        """Обучение с детальными логами"""
        batch_start = time.time()
        self.batch_count += 1
        batch_size = len(items)
        
        logger.info(f"⚡ НАЧАЛО БАТЧА #{self.batch_count}")
        logger.debug(f"   Размер батча: {batch_size}")
        logger.debug(f"   Всего обработано: {self.total_items}")
        
        # Вызываем оригинальный метод
        try:
            result = self.system.learn_batch(items)
            
            batch_time = time.time() - batch_start
            items_per_sec = batch_size / batch_time if batch_time > 0 else 0
            
            self.total_items += batch_size
            
            logger.info(f"✓ БАТЧ #{self.batch_count} ЗАВЕРШЁН")
            logger.debug(f"   Время: {batch_time:.3f} сек")
            logger.debug(f"   Скорость: {items_per_sec:.1f} элементов/сек")
            logger.debug(f"   Всего обработано: {self.total_items}")
            
            # GPU статистика
            if hasattr(self.system, 'get_gpu_stats'):
                gpu_stats = self.system.get_gpu_stats()
                if gpu_stats:
                    logger.debug(f"   GPU: {gpu_stats['utilization']:.1f}% | VRAM: {gpu_stats['memory_used']:.0f}MB | Temp: {gpu_stats['temp']:.0f}°C")
            
            return result
            
        except Exception as e:
            logger.error(f"✗ ОШИБКА В БАТЧЕ #{self.batch_count}: {e}")
            raise
    
    def log_session_summary(self):
        """Итоговая статистика сессии"""
        if self.start_time:
            total_time = time.time() - self.start_time
            avg_speed = self.total_items / total_time if total_time > 0 else 0
            
            logger.info("="*80)
            logger.info("📊 ИТОГИ СЕССИИ ОБУЧЕНИЯ")
            logger.info("="*80)
            logger.info(f"Всего батчей: {self.batch_count}")
            logger.info(f"Всего элементов: {self.total_items}")
            logger.info(f"Общее время: {total_time:.1f} сек")
            logger.info(f"Средняя скорость: {avg_speed:.1f} элементов/сек")
            logger.info("="*80)
