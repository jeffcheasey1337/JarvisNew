# -*- coding: utf-8 -*-
"""
🔧 ИНТЕГРАЦИЯ FULL WEB LEARNING
Весь интернет, не только Wikipedia!
"""

from pathlib import Path
import shutil
from datetime import datetime

print("="*80)
print("🌐 ИНТЕГРАЦИЯ FULL WEB LEARNING")
print("="*80)
print()

root = Path.cwd()

print("[1/2] Копирование модуля...")
source = root / 'full_web_learning.py'
dest = root / 'jarvis' / 'core' / 'learning' / 'full_web_learning.py'

if not source.exists():
    print(f"  ✗ {source} не найден!")
    input("Enter...")
    exit(1)

dest.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(source, dest)
print(f"  ✓ {dest.relative_to(root)}")
print()

print("[2/2] Обновление continuous.py...")

continuous_file = root / 'jarvis' / 'core' / 'learning' / 'continuous.py'

if continuous_file.exists():
    backup = continuous_file.parent / f'continuous_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
    shutil.copy2(continuous_file, backup)
    print(f"  Backup: {backup.name}")

NEW_CODE = '''# -*- coding: utf-8 -*-
"""
JARVIS Continuous Learning WITH FULL WEB CRAWLER
Весь интернет!
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
    from .full_web_learning import FullWebLearningSystem
    FULLWEB_AVAILABLE = True
    logger.info("Full Web Learning доступна")
except Exception as e:
    FULLWEB_AVAILABLE = False
    logger.warning(f"Full Web недоступна: {e}")


class ContinuousLearning:
    """Обучение из всего интернета!"""
    
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
        
        # Full Web Learning
        self.fullweb_learning = None
        if FULLWEB_AVAILABLE:
            try:
                logger.info("Инициализация Full Web Learning...")
                
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
                
                self.fullweb_learning = FullWebLearningSystem(
                    turbo_system=self.turbo_gpu,
                    memory_system=memory_system,  # ВАЖНО!
                    topics_list=all_topics,
                    num_workers=10  # 10 потоков
                )
                
                logger.info(f"Full Web готова ({len(all_topics)} тем, 10 потоков)")
            except Exception as e:
                logger.error(f"Ошибка Full Web: {e}")
        
        logger.info("Continuous Learning готова")
    
    async def start_continuous_learning(self):
        """Async запуск"""
        self.start()
    
    def start(self):
        """Запуск обучения"""
        if self.running:
            return
        
        self.running = True
        self.learning_thread = threading.Thread(target=self._loop, daemon=True)
        self.learning_thread.start()
        logger.info("Full Web обучение запущено")
    
    def stop(self):
        """Остановка"""
        self.running = False
        if self.learning_thread:
            self.learning_thread.join(timeout=5)
        
        if self.fullweb_learning:
            studied = len(self.fullweb_learning.studied_topics)
            logger.info(f"Обучение остановлено. Изучено: {studied}")
    
    def _loop(self):
        """Цикл обучения"""
        if self.fullweb_learning:
            try:
                self.fullweb_learning.start_learning()
            except Exception as e:
                logger.error(f"Ошибка: {e}", exc_info=True)
        
        self.running = False
    
    def get_stats(self):
        """Статистика"""
        stats = {'running': self.running}
        
        if self.fullweb_learning:
            stats.update({
                'total_learned': len(self.fullweb_learning.studied_topics),
                'queue_size': len(self.fullweb_learning.topic_queue),
                'stats': self.fullweb_learning.stats,
            })
        
        return stats
    
    def learn_topic(self, topic: str, category: str = "general"):
        """Добавление темы"""
        if self.fullweb_learning and topic not in self.fullweb_learning.studied_topics:
            self.fullweb_learning.topic_queue.appendleft(topic)
            return True
        return False
'''

continuous_file.write_text(NEW_CODE, encoding='utf-8')
print(f"  ✓ continuous.py обновлен")
print()

print("="*80)
print("✅ FULL WEB LEARNING ИНТЕГРИРОВАНА!")
print("="*80)
print()

print("🌐 ИСТОЧНИКИ:")
print("  ✓ DuckDuckGo (Google результаты)")
print("  ✓ Новостные сайты")
print("  ✓ Блоги и статьи")
print("  ✓ Форумы")
print("  ✓ Wikipedia (резерв)")
print("  ✓ Любые веб-страницы")
print()

print("📊 КАК РАБОТАЕТ:")
print("  1. Для каждой темы → поиск в DuckDuckGo")
print("  2. Получает топ-5 результатов из интернета")
print("  3. Парсит каждую страницу")
print("  4. Извлекает текстовый контент")
print("  5. Сохраняет в memory_system")
print("  6. Находит новые темы")
print("  7. Повторяет бесконечно")
print()

print("⚡ СКОРОСТЬ:")
print("  • 10 потоков параллельно")
print("  • ~15-25 тем/мин (зависит от интернета)")
print("  • 1617 тем за ~65-108 минут")
print()

print("💾 ПАМЯТЬ:")
print("  • Каждая тема → 5 записей в память")
print("  • 1617 тем × 5 = ~8,000 записей")
print("  • Было: 13,302")
print("  • Станет: ~21,000 записей!")
print()

print("🌐 УНИКАЛЬНОСТЬ:")
print("  • Не только Wikipedia")
print("  • Весь открытый интернет")
print("  • Новости, блоги, форумы")
print("  • Актуальная информация")
print()

print("="*80)
print()

input("Enter для продолжения...")

print()
print("🚀 ГОТОВО! Запускайте JARVIS:")
print()
print("  python -m jarvis")
print()
print("JARVIS будет учиться из всего интернета!")
print()
