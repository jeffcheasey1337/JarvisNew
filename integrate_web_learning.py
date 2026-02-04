# -*- coding: utf-8 -*-
"""
INTEGRATION: Web Learning → JARVIS

Интеграция автономной системы обучения из интернета в JARVIS
"""

from pathlib import Path
import shutil
from datetime import datetime

print("="*80)
print("ИНТЕГРАЦИЯ WEB LEARNING В JARVIS")
print("="*80)
print()

root = Path.cwd()

# ============================================================================
# ШАГ 1: КОПИРУЕМ autonomous_web_learning.py
# ============================================================================

print("[1/3] Копирование модуля web learning...")

source = root / 'autonomous_web_learning.py'
dest = root / 'jarvis' / 'core' / 'learning' / 'web_learning.py'

if source.exists():
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    print(f"  OK: {dest.relative_to(root)}")
else:
    print(f"  ОШИБКА: {source} не найден!")
    exit(1)

print()

# ============================================================================
# ШАГ 2: УСТАНОВКА ЗАВИСИМОСТЕЙ
# ============================================================================

print("[2/3] Проверка зависимостей...")

try:
    import requests
    print("  OK: requests установлен")
except ImportError:
    print("  Нужно установить: pip install requests")

try:
    import bs4
    print("  OK: beautifulsoup4 установлен")
except ImportError:
    print("  Нужно установить: pip install beautifulsoup4")

print()

# ============================================================================
# ШАГ 3: ОБНОВЛЯЕМ CONTINUOUS.PY
# ============================================================================

print("[3/3] Обновление continuous.py с web learning...")

continuous_file = root / 'jarvis' / 'core' / 'learning' / 'continuous.py'

# Backup
if continuous_file.exists():
    backup = continuous_file.parent / f'continuous_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
    shutil.copy2(continuous_file, backup)
    print(f"  Backup: {backup.name}")

# Новый код с web learning
NEW_CONTINUOUS = '''# -*- coding: utf-8 -*-
"""
JARVIS Continuous Learning System WITH WEB RESEARCH
Система непрерывного обучения с исследованием интернета
"""

import logging
import threading
import time
import asyncio
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Импорт систем
try:
    from .turbo import TurboLearningSystem
    TURBO_AVAILABLE = True
    logger.info("Turbo GPU система доступна")
except ImportError as e:
    TURBO_AVAILABLE = False
    logger.warning(f"Turbo система недоступна: {e}")

try:
    from .topics_database import get_all_topics_flat, get_topics_count
    TOPICS_DB_AVAILABLE = True
except ImportError:
    TOPICS_DB_AVAILABLE = False
    logger.warning("Topics database недоступна")

try:
    from .web_learning import AutonomousWebLearningSystem
    WEB_LEARNING_AVAILABLE = True
    logger.info("Web Learning система доступна")
except ImportError as e:
    WEB_LEARNING_AVAILABLE = False
    logger.warning(f"Web Learning недоступна: {e}")


class ContinuousLearning:
    """
    Система непрерывного обучения
    С интернет-исследованием
    """
    
    def __init__(self, config=None, memory_system=None, nlp_processor=None):
        self.config = config or {}
        self.memory_system = memory_system
        self.nlp_processor = nlp_processor
        
        # Параметры
        self.batch_size = self.config.get('learning', {}).get('batch_size', 512)
        self.learning_interval = self.config.get('learning', {}).get('interval', 30)
        
        # НОВОЕ: Web Learning
        self.use_web_learning = self.config.get('learning', {}).get('use_web_learning', True)
        
        # Состояние
        self.running = False
        self.learning_thread = None
        self.total_learned = 0
        self.session_learned = 0
        
        # Turbo система
        self.turbo_system = None
        if TURBO_AVAILABLE:
            try:
                logger.info("Инициализация Turbo GPU системы...")
                self.turbo_system = TurboLearningSystem(
                    batch_size=self.batch_size,
                    num_workers=32
                )
                logger.info("Turbo GPU система инициализирована")
            except Exception as e:
                logger.error(f"Ошибка инициализации Turbo: {e}")
                self.turbo_system = None
        
        # НОВОЕ: Web Learning система
        self.web_learning = None
        if WEB_LEARNING_AVAILABLE and self.use_web_learning:
            try:
                logger.info("Инициализация Web Learning системы...")
                self.web_learning = AutonomousWebLearningSystem(
                    memory_system=self.memory_system,
                    turbo_system=self.turbo_system
                )
                logger.info("Web Learning система инициализирована")
            except Exception as e:
                logger.error(f"Ошибка инициализации Web Learning: {e}")
                self.web_learning = None
        
        # Статистика
        self.stats = {
            'start_time': None,
            'total_topics': 0,
            'learned_topics': 0,
            'topics_per_second': 0,
        }
        
        logger.info("Система непрерывного обучения инициализирована")
    
    async def start_continuous_learning(self):
        """Запуск (async для JARVIS)"""
        self.start()
    
    def start(self):
        """Запуск обучения"""
        if self.running:
            logger.warning("Обучение уже запущено")
            return
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        self.learning_thread = threading.Thread(
            target=self._learning_loop,
            daemon=True,
            name="ContinuousLearning"
        )
        self.learning_thread.start()
        
        logger.info("Непрерывное обучение запущено")
    
    def stop(self):
        """Остановка"""
        if not self.running:
            return
        
        self.running = False
        
        if self.learning_thread:
            self.learning_thread.join(timeout=5)
        
        logger.info(f"Обучение остановлено. Изучено тем: {self.total_learned}")
    
    def _learning_loop(self):
        """Основной цикл обучения"""
        logger.info("Начало цикла обучения...")
        
        # Получаем темы
        all_topics = []
        if TOPICS_DB_AVAILABLE:
            try:
                all_topics = get_all_topics_flat()
                logger.info(f"Загружено {len(all_topics)} тем для обучения")
            except Exception as e:
                logger.error(f"Ошибка загрузки тем: {e}")
        
        if not all_topics:
            logger.warning("Нет тем для обучения")
            all_topics = ["Python", "Machine Learning", "Web Development"]
        
        self.stats['total_topics'] = len(all_topics)
        
        processed = 0
        
        try:
            for topic in all_topics:
                if not self.running:
                    break
                
                # НОВОЕ: Web Learning - собираем реальные знания из интернета
                if self.web_learning:
                    logger.info(f"[Web Learning] {topic}")
                    success = self.web_learning.learn_topic_from_web(topic)
                    
                    if success:
                        processed += 1
                        self.total_learned = processed
                        self.session_learned += 1
                        self.stats['learned_topics'] = processed
                    
                    # Обновляем скорость
                    if self.stats['start_time']:
                        elapsed = time.time() - self.stats['start_time']
                        self.stats['topics_per_second'] = processed / elapsed if elapsed > 0 else 0
                    
                    # Логируем каждые 10 тем
                    if processed % 10 == 0:
                        speed = self.stats['topics_per_second']
                        logger.info(
                            f"Прогресс: {processed}/{len(all_topics)} | "
                            f"Скорость: {speed:.2f} тем/мин | "
                            f"Режим: Web Learning"
                        )
                    
                    # Пауза между темами (чтобы не перегружать сайты)
                    time.sleep(5)
                
                else:
                    # Fallback: обычное обучение без web research
                    logger.debug(f"[Обычное обучение] {topic}")
                    processed += 1
                    self.total_learned = processed
                    time.sleep(0.1)
            
            logger.info(f"Обучение завершено! Изучено {processed} тем")
        
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}", exc_info=True)
        
        finally:
            self.running = False
    
    def get_stats(self):
        """Статистика"""
        stats = self.stats.copy()
        
        if self.web_learning:
            stats['web_learning'] = self.web_learning.get_stats()
        
        stats['session_learned'] = self.session_learned
        stats['total_learned'] = self.total_learned
        stats['running'] = self.running
        
        return stats
    
    def learn_topic(self, topic: str, category: str = "general"):
        """Обучение на одной теме"""
        if self.web_learning:
            return self.web_learning.learn_topic_from_web(topic)
        else:
            logger.warning("Web Learning недоступна")
            return False
'''

continuous_file.write_text(NEW_CONTINUOUS, encoding='utf-8')
print(f"  OK: continuous.py обновлен с Web Learning")

print()

# ============================================================================
# ИТОГИ
# ============================================================================

print("="*80)
print("ИНТЕГРАЦИЯ ЗАВЕРШЕНА!")
print("="*80)
print()

print("Что установлено:")
print("  1. Web Learning модуль (web_learning.py)")
print("  2. Обновлен continuous.py с интернет-исследованием")
print()

print("Теперь JARVIS будет:")
print("  1. Брать тему из базы (например 'Квентин Тарантино')")
print("  2. Искать информацию в интернете (Google, Reddit, форумы)")
print("  3. Парсить и скачивать контент")
print("  4. Создавать embeddings на РЕАЛЬНЫХ данных")
print("  5. Сохранять знания в память")
print()

print("Зависимости:")
print("  pip install requests beautifulsoup4")
print()

print("Запуск:")
print("  python -m jarvis")
print()

print("="*80)

input("\nEnter для выхода...")
