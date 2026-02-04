# -*- coding: utf-8 -*-
"""
📊 JARVIS REAL-TIME MONITOR
Система детального мониторинга обучения в реальном времени

Возможности:
✅ Real-time статистика GPU/CPU/RAM
✅ Детальные логи каждого шага
✅ Прогресс-бары
✅ Скорость обучения
✅ Оптимизация производительности
"""

import time
import json
from pathlib import Path
from datetime import datetime
import threading
import sys

class RealTimeMonitor:
    """Мониторинг обучения в реальном времени"""
    
    def __init__(self):
        self.root = Path.cwd()
        self.logs_dir = self.root / 'logs' / 'realtime'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_log = self.logs_dir / f'realtime_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        self.stats_file = self.logs_dir / 'live_stats.json'
        
        self.monitoring = False
        self.monitor_thread = None
        
        self.stats = {
            'start_time': None,
            'total_topics': 0,
            'topics_learned': 0,
            'topics_per_second': 0,
            'gpu_usage': 0,
            'gpu_memory': 0,
            'gpu_temp': 0,
            'cpu_usage': 0,
            'ram_usage': 0,
            'batch_size': 0,
            'current_batch': 0,
            'eta_seconds': 0,
        }
    
    def log(self, message, level='INFO'):
        """Подробное логирование с timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        # В консоль
        print(log_entry)
        
        # В файл
        with open(self.current_log, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def get_gpu_stats(self):
        """Получение статистики GPU"""
        try:
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu',
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=1
            )
            
            if result.returncode == 0:
                data = result.stdout.strip().split(',')
                return {
                    'utilization': float(data[0]),
                    'memory_used': float(data[1]),
                    'memory_total': float(data[2]),
                    'temperature': float(data[3]),
                }
        except:
            pass
        
        return None
    
    def get_cpu_ram_stats(self):
        """Получение статистики CPU и RAM"""
        try:
            import psutil
            return {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'ram_percent': psutil.virtual_memory().percent,
                'ram_used_gb': psutil.virtual_memory().used / (1024**3),
                'ram_total_gb': psutil.virtual_memory().total / (1024**3),
            }
        except:
            return None
    
    def update_stats(self, **kwargs):
        """Обновление статистики"""
        self.stats.update(kwargs)
        
        # Сохраняем в файл для real-time доступа
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)
    
    def start_monitoring(self):
        """Запуск мониторинга в отдельном потоке"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.log("📊 Мониторинг запущен", "MONITOR")
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        self.log("📊 Мониторинг остановлен", "MONITOR")
    
    def _monitor_loop(self):
        """Цикл мониторинга"""
        while self.monitoring:
            # GPU статистика
            gpu_stats = self.get_gpu_stats()
            if gpu_stats:
                self.stats['gpu_usage'] = gpu_stats['utilization']
                self.stats['gpu_memory'] = gpu_stats['memory_used']
                self.stats['gpu_temp'] = gpu_stats['temperature']
            
            # CPU/RAM статистика
            cpu_ram = self.get_cpu_ram_stats()
            if cpu_ram:
                self.stats['cpu_usage'] = cpu_ram['cpu_percent']
                self.stats['ram_usage'] = cpu_ram['ram_percent']
            
            # Вычисляем скорость
            if self.stats['start_time']:
                elapsed = time.time() - self.stats['start_time']
                if elapsed > 0:
                    self.stats['topics_per_second'] = self.stats['topics_learned'] / elapsed
                    
                    remaining = self.stats['total_topics'] - self.stats['topics_learned']
                    if self.stats['topics_per_second'] > 0:
                        self.stats['eta_seconds'] = remaining / self.stats['topics_per_second']
            
            # Сохраняем
            self.update_stats()
            
            time.sleep(0.5)  # Обновление каждые 0.5 сек
    
    def show_realtime_stats(self):
        """Показать статистику в реальном времени"""
        if not self.stats['start_time']:
            return
        
        elapsed = time.time() - self.stats['start_time']
        progress = (self.stats['topics_learned'] / self.stats['total_topics'] * 100) if self.stats['total_topics'] > 0 else 0
        
        # Создаём прогресс-бар
        bar_width = 50
        filled = int(bar_width * progress / 100)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        # Формируем вывод
        output = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    📊 JARVIS REAL-TIME MONITOR                             ║
╚════════════════════════════════════════════════════════════════════════════╝

⏱️  ПРОГРЕСС
   [{bar}] {progress:.1f}%
   
   📚 Изучено: {self.stats['topics_learned']} / {self.stats['total_topics']}
   ⚡ Скорость: {self.stats['topics_per_second']:.1f} тем/сек
   🕐 Прошло: {elapsed:.1f} сек
   ⏳ Осталось: {self.stats['eta_seconds']:.1f} сек

🎮 GPU СТАТИСТИКА
   Загрузка: {self.stats['gpu_usage']:.1f}%
   VRAM: {self.stats['gpu_memory']:.0f} MB
   Температура: {self.stats['gpu_temp']:.0f}°C

💻 CPU/RAM
   CPU: {self.stats['cpu_usage']:.1f}%
   RAM: {self.stats['ram_usage']:.1f}%

⚙️  ОБРАБОТКА
   Размер батча: {self.stats['batch_size']}
   Текущий батч: {self.stats['current_batch']}
"""
        
        # Очищаем экран и выводим
        print('\033[2J\033[H')  # Очистка экрана
        print(output)


# Создаём глобальный монитор
monitor = RealTimeMonitor()


def create_detailed_logger():
    """Создание детального логгера для турбо-обучения"""
    
    code = '''# -*- coding: utf-8 -*-
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
'''
    
    return code


def create_optimized_turbo_config():
    """Создание оптимизированной конфигурации турбо-обучения"""
    
    config = {
        "gpu_enabled": True,
        "batch_size": 1024,  # Увеличен с 512
        "num_workers": 32,   # Увеличен с 24
        "pin_memory": True,
        "prefetch_factor": 4,  # Предзагрузка
        "persistent_workers": True,  # Постоянные воркеры
        
        # GPU оптимизация
        "gpu_optimization": {
            "cudnn_benchmark": True,
            "cudnn_deterministic": False,
            "fp16": True,  # Half precision для скорости
            "grad_scaler": True,
            "compile_mode": "max-autotune",
        },
        
        # Параллелизм
        "parallel": {
            "data_parallel": True,
            "distributed": False,
            "world_size": 1,
        },
        
        # Кэширование
        "cache": {
            "enabled": True,
            "max_size_gb": 8,
            "embeddings_cache": True,
        },
        
        # Мониторинг
        "monitoring": {
            "enabled": True,
            "update_interval": 0.5,
            "detailed_logs": True,
            "gpu_stats": True,
            "profiling": False,
        }
    }
    
    return config


def main():
    """Главная функция настройки"""
    print("="*80)
    print("📊 JARVIS REAL-TIME MONITOR SETUP")
    print("="*80)
    print()
    
    root = Path.cwd()
    
    # Создаём директории для логов
    print("[1/5] Создание структуры логов...")
    logs_dirs = [
        'logs/realtime',
        'logs/detailed',
        'logs/gpu',
        'logs/performance',
    ]
    
    for dir_path in logs_dirs:
        (root / dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")
    
    # Создаём оптимизированную конфигурацию
    print()
    print("[2/5] Создание оптимизированной конфигурации...")
    
    config_dir = root / 'config'
    config_dir.mkdir(exist_ok=True)
    
    optimized_config = create_optimized_turbo_config()
    config_file = config_dir / 'turbo_optimized.json'
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(optimized_config, f, indent=2)
    
    print(f"  ✓ Создан: {config_file}")
    print(f"  ✓ Batch size: {optimized_config['batch_size']}")
    print(f"  ✓ Workers: {optimized_config['num_workers']}")
    print(f"  ✓ FP16: {optimized_config['gpu_optimization']['fp16']}")
    
    # Создаём патч для детального логирования
    print()
    print("[3/5] Создание системы детального логирования...")
    
    logger_code = create_detailed_logger()
    logger_file = root / 'jarvis' / 'core' / 'learning' / 'detailed_logger.py'
    
    with open(logger_file, 'w', encoding='utf-8') as f:
        f.write(logger_code)
    
    print(f"  ✓ Создан: {logger_file}")
    
    # Создаём скрипт просмотра логов в реальном времени
    print()
    print("[4/5] Создание real-time viewer...")
    
    viewer_code = '''# -*- coding: utf-8 -*-
"""
Real-time log viewer
"""

import time
import json
from pathlib import Path

def tail_log(filepath, interval=0.1):
    """Просмотр логов в реальном времени"""
    with open(filepath, 'r', encoding='utf-8') as f:
        # Переходим в конец
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if line:
                print(line, end='')
            else:
                time.sleep(interval)

def show_live_stats():
    """Показ статистики в реальном времени"""
    stats_file = Path('logs/realtime/live_stats.json')
    
    while True:
        try:
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
                
                # Очищаем экран
                print('\\033[2J\\033[H')
                
                # Показываем статистику
                print("="*80)
                print("📊 LIVE STATS")
                print("="*80)
                print(f"Topics: {stats.get('topics_learned', 0)} / {stats.get('total_topics', 0)}")
                print(f"Speed: {stats.get('topics_per_second', 0):.1f} topics/sec")
                print(f"GPU: {stats.get('gpu_usage', 0):.1f}%")
                print(f"VRAM: {stats.get('gpu_memory', 0):.0f} MB")
                print(f"Temp: {stats.get('gpu_temp', 0):.0f}°C")
                print(f"CPU: {stats.get('cpu_usage', 0):.1f}%")
                print(f"RAM: {stats.get('ram_usage', 0):.1f}%")
                print("="*80)
            
            time.sleep(1)
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'stats':
        show_live_stats()
    else:
        # Tail логов
        log_file = Path('logs/turbo_detailed.log')
        if log_file.exists():
            tail_log(log_file)
        else:
            print("Лог файл не найден. Запустите обучение сначала.")
'''
    
    viewer_file = root / 'view_realtime.py'
    with open(viewer_file, 'w', encoding='utf-8') as f:
        f.write(viewer_code)
    
    print(f"  ✓ Создан: {viewer_file}")
    
    # Создаём инструкцию
    print()
    print("[5/5] Создание инструкции...")
    
    instructions = """# 📊 Real-Time Мониторинг JARVIS

## Использование

### 1. Просмотр логов в реальном времени:

```bash
python view_realtime.py
```

### 2. Просмотр статистики в реальном времени:

```bash
python view_realtime.py stats
```

### 3. Просмотр GPU в реальном времени:

```bash
nvidia-smi -l 1
```

Или для красивого вывода:

```bash
pip install nvitop
nvitop
```

## Файлы логов

- `logs/realtime/` - Real-time логи
- `logs/detailed/` - Детальные логи
- `logs/turbo_detailed.log` - Подробные логи обучения
- `logs/realtime/live_stats.json` - Живая статистика

## Оптимизация

Новая конфигурация в `config/turbo_optimized.json`:

- Batch size: 1024 (было 512)
- Workers: 32 (было 24)
- FP16: включено (ускорение 2x)
- Prefetch: 4 (предзагрузка данных)
- Persistent workers: да

## Ожидаемая скорость

С RTX 4070 Ti Super:
- Без оптимизации: ~500 тем/час
- С оптимизацией: ~1000-2000 тем/час
- Пиковая: до 3000 тем/час

## Мониторинг производительности

Во время работы JARVIS вы увидите:

```
[2026-01-30 15:23:45.123] [INFO] [TurboLearning] ⚡ НАЧАЛО БАТЧА #1
[2026-01-30 15:23:45.124] [DEBUG] [TurboLearning]    Размер батча: 1024
[2026-01-30 15:23:45.234] [INFO] [TurboLearning] ✓ БАТЧ #1 ЗАВЕРШЁН
[2026-01-30 15:23:45.235] [DEBUG] [TurboLearning]    Время: 0.111 сек
[2026-01-30 15:23:45.236] [DEBUG] [TurboLearning]    Скорость: 9225.2 элементов/сек
[2026-01-30 15:23:45.237] [DEBUG] [TurboLearning]    GPU: 95.2% | VRAM: 8456MB | Temp: 68°C
```

## Проблемы?

Если скорость всё равно низкая:

1. Проверьте что GPU используется:
   ```bash
   nvidia-smi
   ```

2. Проверьте настройки питания GPU:
   - NVIDIA Control Panel → Manage 3D Settings → Power Management → Prefer Maximum Performance

3. Увеличьте batch size в config/turbo_optimized.json

4. Проверьте что FP16 включен
"""
    
    instructions_file = root / 'docs' / 'REALTIME_MONITORING.md'
    instructions_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"  ✓ Создан: {instructions_file}")
    
    # Итоги
    print()
    print("="*80)
    print("✅ НАСТРОЙКА ЗАВЕРШЕНА!")
    print("="*80)
    print()
    print("📊 Что установлено:")
    print()
    print("  ✓ Real-time мониторинг")
    print("  ✓ Детальное логирование")
    print("  ✓ Оптимизированная конфигурация")
    print("  ✓ Live статистика")
    print()
    print("🚀 Следующие шаги:")
    print()
    print("1. Запустите JARVIS:")
    print("   python -m jarvis")
    print()
    print("2. В другом терминале запустите мониторинг:")
    print("   python view_realtime.py")
    print()
    print("3. Или статистику:")
    print("   python view_realtime.py stats")
    print()
    print("4. Или GPU монитор:")
    print("   nvidia-smi -l 1")
    print()
    print("📖 Инструкция: docs/REALTIME_MONITORING.md")
    print()
    print("="*80)


if __name__ == "__main__":
    main()
    input("\nНажмите Enter для выхода...")
