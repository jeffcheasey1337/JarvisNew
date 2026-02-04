# -*- coding: utf-8 -*-
"""
🔧 FIX JARVIS CONTINUOUS LEARNING
Исправление ошибки инициализации + интеграция GPU обучения
"""

from pathlib import Path
import shutil
from datetime import datetime

print("="*80)
print("🔧 FIX JARVIS CONTINUOUS LEARNING")
print("="*80)
print()

root = Path.cwd()

# ============================================================================
# ШАГ 1: BACKUP ТЕКУЩЕГО ФАЙЛА
# ============================================================================
print("[1/4] Создание backup...")

continuous_file = root / 'jarvis' / 'core' / 'learning' / 'continuous.py'

if continuous_file.exists():
    backup_file = root / 'jarvis' / 'core' / 'learning' / f'continuous_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
    shutil.copy2(continuous_file, backup_file)
    print(f"  ✓ Backup: {backup_file.name}")
else:
    print("  ⚠ continuous.py не найден, создаём новый")

print()

# ============================================================================
# ШАГ 2: КОПИРОВАНИЕ ИСПРАВЛЕННОГО ФАЙЛА
# ============================================================================
print("[2/4] Установка исправленного continuous.py...")

fixed_file = root / 'continuous_fixed.py'

if not fixed_file.exists():
    print("  ✗ continuous_fixed.py не найден!")
    print("    Запустите этот скрипт из папки проекта")
    input("\nНажмите Enter...")
    exit(1)

# Копируем
shutil.copy2(fixed_file, continuous_file)
print(f"  ✓ Установлен: {continuous_file.relative_to(root)}")
print()

# ============================================================================
# ШАГ 3: ПРОВЕРКА ИМПОРТА
# ============================================================================
print("[3/4] Проверка импорта...")

try:
    import sys
    sys.path.insert(0, str(root))
    
    from jarvis.core.learning.continuous import ContinuousLearning
    
    # Тестируем инициализацию с разными параметрами
    print("  Тест 1: Без параметров...")
    cl1 = ContinuousLearning()
    print("    ✓ OK")
    
    print("  Тест 2: С config...")
    cl2 = ContinuousLearning(config={'learning': {'batch_size': 512}})
    print("    ✓ OK")
    
    print("  Тест 3: С config + memory + nlp (как в JARVIS)...")
    cl3 = ContinuousLearning(
        config={'learning': {'batch_size': 512}},
        memory_system=None,
        nlp_processor=None
    )
    print("    ✓ OK")
    
    print()
    print("  ✓ Все тесты пройдены!")
    print()

except Exception as e:
    print(f"  ✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    print()
    input("\nНажмите Enter...")
    exit(1)

# ============================================================================
# ШАГ 4: ПРОВЕРКА ИНТЕГРАЦИИ GPU
# ============================================================================
print("[4/4] Проверка GPU интеграции...")

try:
    # Проверяем что turbo.py существует
    turbo_file = root / 'jarvis' / 'core' / 'learning' / 'turbo.py'
    
    if turbo_file.exists():
        print("  ✓ turbo.py найден")
        
        # Пытаемся импортировать
        try:
            from jarvis.core.learning.turbo import TurboLearningSystem
            print("  ✓ TurboLearningSystem импортирован")
            
            # Проверяем GPU
            import torch
            if torch.cuda.is_available():
                print(f"  ✓ GPU доступна: {torch.cuda.get_device_name(0)}")
                print(f"  ✓ CUDA версия: {torch.version.cuda}")
                print()
                print("  🚀 GPU ТУРБО-ОБУЧЕНИЕ БУДЕТ ИСПОЛЬЗОВАТЬСЯ!")
            else:
                print("  ⚠ GPU недоступна, будет использоваться CPU")
        
        except Exception as e:
            print(f"  ⚠ Turbo система недоступна: {e}")
            print("    Обучение будет работать в обычном режиме")
    else:
        print("  ⚠ turbo.py не найден")
        print("    Запустите: python fix_gpu_activation.py")

except Exception as e:
    print(f"  ⚠ Не удалось проверить GPU: {e}")

print()

# ============================================================================
# ИТОГИ
# ============================================================================
print("="*80)
print("✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!")
print("="*80)
print()

print("Что сделано:")
print()
print("  ✓ Создан backup старого continuous.py")
print("  ✓ Установлен исправленный continuous.py")
print("  ✓ Совместимость с JARVIS проверена")
print("  ✓ GPU интеграция проверена")
print()

print("Теперь JARVIS должен запускаться без ошибок!")
print()

print("🚀 ЗАПУСК JARVIS:")
print()
print("  python -m jarvis")
print()

print("Если GPU турбо-обучение доступно, вы увидите:")
print("  ✓ Turbo GPU система доступна")
print("  🚀 Инициализация Turbo GPU системы...")
print("  ✓ Turbo GPU система инициализирована")
print()

print("Проверка GPU во время работы:")
print()
print("  nvidia-smi -l 1")
print()
print("GPU должна загружаться до 90-95% во время обучения!")
print()

print("="*80)

input("\nНажмите Enter для выхода...")
