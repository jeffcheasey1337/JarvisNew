# -*- coding: utf-8 -*-
"""
🎓 JARVIS Continuous Learning - GPU VERSION
"""

import time
from pathlib import Path
from datetime import datetime

try:
    from .topics_database import get_all_topics_flat, get_topics_count
    from .turbo import TurboLearningSystem
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from topics_database import get_all_topics_flat, get_topics_count
    from turbo import TurboLearningSystem


class ContinuousLearning:
    """Непрерывное обучение с GPU"""
    
    def __init__(self, batch_size=512):
        self.batch_size = batch_size
        self.running = False
        
        # Создаём турбо-систему (GPU)
        print("\n🚀 Инициализация GPU обучения...")
        self.turbo = TurboLearningSystem(batch_size=batch_size)
        
        self.total_learned = 0
        
    def start(self):
        """Запуск обучения"""
        self.running = True
        
        # Получаем все темы
        all_topics = get_all_topics_flat()
        total_topics = len(all_topics)
        
        print(f"\n📚 Начинается обучение на {total_topics} темах")
        print(f"📦 Batch size: {self.batch_size}")
        print(f"🎮 GPU: ВКЛЮЧЕНА\n")
        
        self.turbo.start_time = time.time()
        
        processed = 0
        batch_num = 0
        
        try:
            while self.running and processed < total_topics:
                batch_num += 1
                
                # Берём батч
                batch_start = processed
                batch_end = min(batch_start + self.batch_size, total_topics)
                batch = all_topics[batch_start:batch_end]
                
                # Обрабатываем НА GPU
                result = self.turbo.learn_batch(batch)
                
                processed += len(batch)
                self.total_learned = processed
                
                # Логируем каждые 10 батчей
                if batch_num % 10 == 0:
                    stats = self.turbo.get_stats()
                    print(f"[Батч {batch_num}] "
                          f"Обработано: {processed}/{total_topics} | "
                          f"Скорость: {stats['speed']:.1f} тем/сек | "
                          f"GPU: {stats['gpu_info']['memory_allocated']:.0f} MB")
                
                # Небольшая пауза
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\n⚠️  Обучение прервано")
        
        finally:
            self.stop()
    
    def stop(self):
        """Остановка"""
        self.running = False
        
        if hasattr(self, 'turbo'):
            stats = self.turbo.get_stats()
            print(f"\n✅ Обучение завершено")
            print(f"📊 Всего обработано: {stats['total_processed']} тем")
            print(f"⚡ Средняя скорость: {stats['speed']:.1f} тем/сек")


def main():
    learning = ContinuousLearning(batch_size=512)
    
    try:
        learning.start()
    except KeyboardInterrupt:
        print("\nОстановка...")
    finally:
        learning.stop()


if __name__ == "__main__":
    main()
